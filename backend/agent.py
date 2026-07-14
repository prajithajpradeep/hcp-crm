"""
agent.py
--------
This is the BRAIN of the project. It builds a LangGraph "agent" that:

  1. Reads what the user typed in the chat (e.g. "Today I met Dr. Smith...").
  2. Asks the LLM (Groq gemma2-9b-it) to decide WHICH tool to use and to pull out
     the important details (doctor name, date, sentiment, etc.) as JSON.
  3. Routes to the matching tool. Each tool does one job and returns the fields
     that should be filled into the form on the left side of the screen.

Why this design?
  gemma2-9b-it is a small, fast model whose built-in "function calling" is not
  reliable. So instead of trusting that feature, we simply ask the model to
  answer in JSON. This is easier to understand, easier to debug, and still uses
  LangGraph + an LLM to drive every tool (which is what the task requires).

The LangGraph "graph" looks like this:

        START ->  router  ->  (one of the 5 tools)  ->  END
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from database import SessionLocal, Interaction, FollowUp


load_dotenv()

# ---------------------------------------------------------------------------
# 1. The LLM
# ---------------------------------------------------------------------------
# temperature=0 means "be consistent / don't get creative" - good for pulling
# out structured data.
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


# ---------------------------------------------------------------------------
# 2. The "state" - a shared bag of data that flows through the graph.
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    user_message: str      # what the user typed
    current_form: dict     # the form as it is right now
    tool_name: str         # which tool the LLM chose
    tool_args: dict        # the details the LLM pulled out
    form_updates: dict     # fields we want to change on the form
    reply: str             # the assistant's chat reply back to the user


# ---------------------------------------------------------------------------
# 3. The ROUTER node - the LLM reads the message and returns JSON.
# ---------------------------------------------------------------------------
ROUTER_PROMPT = """You are the AI assistant of a CRM used by pharmaceutical sales reps
to log meetings with doctors (HCPs = Healthcare Professionals).

Today's date is {today}.

You have exactly these 5 tools. Choose the ONE that best fits the user's message:

1. "log_interaction"  -> The user is describing a NEW interaction/meeting. Extract every
   detail you can. Fields you can extract: hcpName, interactionType (Meeting/Call/Email),
   date (YYYY-MM-DD), time, attendees, topicsDiscussed, materialsShared, sentiment
   (positive/neutral/negative).

2. "edit_interaction" -> The user wants to CHANGE / CORRECT something already in the form
   (words like "actually", "sorry", "change", "no it was"). Only put the fields they want
   to change into "args".

3. "clear_form" -> The user wants to clear/reset/empty the form and start over
   (words like "clear", "reset", "start over", "new interaction"). args can be empty.

4. "schedule_followup" -> The user wants to schedule/plan a follow-up. Extract
   {{"hcpName": "...", "followupDate": "YYYY-MM-DD", "note": "..."}} if given.

5. "summarize_interaction" -> The user asks for a summary of the interaction currently
   in the form. args can be empty.

The form currently contains:
{current_form}

The user just said:
"{user_message}"

Respond with ONLY a JSON object, no extra words, in exactly this shape:
{{"tool": "<one tool name>", "args": {{ ...extracted fields... }}, "reply": "<short friendly reply to the user>"}}
"""


def _extract_json(text: str) -> dict:
    """LLMs sometimes wrap JSON in ```code fences``` or add stray words.
    This finds the first {...} block and parses it safely."""
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    # If everything fails, do nothing harmful.
    return {"tool": "none", "args": {}, "reply": "Sorry, I didn't quite catch that. Could you rephrase?"}


def router_node(state: AgentState) -> AgentState:
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = ROUTER_PROMPT.format(
        today=today,
        current_form=json.dumps(state.get("current_form", {})),
        user_message=state["user_message"],
    )
    response = llm.invoke(prompt)
    parsed = _extract_json(response.content)

    state["tool_name"] = parsed.get("tool", "none")
    state["tool_args"] = parsed.get("args", {}) or {}
    state["reply"] = parsed.get("reply", "")
    state["form_updates"] = {}
    return state


# ---------------------------------------------------------------------------
# 4. THE 5 TOOLS (each one is a node in the graph)
# ---------------------------------------------------------------------------

# Tool 1: LOG INTERACTION -------------------------------------------------
def log_interaction_node(state: AgentState) -> AgentState:
    """Take the details the LLM extracted, fill the form, and save to the database."""
    args = state["tool_args"]

    # If the LLM didn't give a date, default to today.
    if not args.get("date"):
        args["date"] = datetime.now().strftime("%Y-%m-%d")

    # These are the fields we push back to the form on the left.
    updates = {
        "hcpName": args.get("hcpName", ""),
        "interactionType": args.get("interactionType", "Meeting"),
        "date": args.get("date", ""),
        "time": args.get("time", ""),
        "attendees": args.get("attendees", ""),
        "topicsDiscussed": args.get("topicsDiscussed", ""),
        "materialsShared": args.get("materialsShared", ""),
        "sentiment": args.get("sentiment", ""),
    }
    # Remove empty values so we don't wipe existing data with blanks.
    updates = {k: v for k, v in updates.items() if v}
    state["form_updates"] = updates

    # Save a copy to the database.
    db = SessionLocal()
    try:
        db.add(Interaction(
            hcp_name=updates.get("hcpName", ""),
            interaction_type=updates.get("interactionType", "Meeting"),
            date=updates.get("date", ""),
            time=updates.get("time", ""),
            attendees=updates.get("attendees", ""),
            topics=updates.get("topicsDiscussed", ""),
            materials=updates.get("materialsShared", ""),
            sentiment=updates.get("sentiment", ""),
        ))
        db.commit()
    finally:
        db.close()

    if not state.get("reply"):
        state["reply"] = "Interaction logged successfully. I've filled in the form for you."
    return state


# Tool 2: EDIT INTERACTION ------------------------------------------------
def edit_interaction_node(state: AgentState) -> AgentState:
    """Change ONLY the fields the user mentioned; leave everything else alone."""
    args = state["tool_args"]

    # Map any field the LLM returned onto our form field names.
    allowed = ["hcpName", "interactionType", "date", "time",
               "attendees", "topicsDiscussed", "materialsShared", "sentiment"]
    updates = {k: v for k, v in args.items() if k in allowed and v}
    state["form_updates"] = updates

    if not state.get("reply"):
        changed = ", ".join(updates.keys()) or "nothing"
        state["reply"] = f"Updated: {changed}. Everything else is unchanged."
    return state


# Tool 3: CLEAR FORM ------------------------------------------------------
def clear_form_node(state: AgentState) -> AgentState:
    """Wipe every field so the user can start a fresh interaction."""
    # Setting each field to "" empties it on the form.
    state["form_updates"] = {
        "hcpName": "",
        "interactionType": "Meeting",
        "date": "",
        "time": "",
        "attendees": "",
        "topicsDiscussed": "",
        "materialsShared": "",
        "samplesDistributed": "",
        "sentiment": "",
        "outcomes": "",
        "followUpActions": "",
    }
    state["reply"] = "Cleared the form. You can start logging a new interaction."
    return state


# Tool 4: SCHEDULE FOLLOW-UP ----------------------------------------------
def schedule_followup_node(state: AgentState) -> AgentState:
    """Create a follow-up task. If no date is given, suggest one week from now."""
    args = state["tool_args"]
    hcp = args.get("hcpName") or state.get("current_form", {}).get("hcpName", "")
    date = args.get("followupDate")
    if not date:
        date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    note = args.get("note", "Follow-up meeting")

    db = SessionLocal()
    try:
        db.add(FollowUp(hcp_name=hcp, followup_date=date, note=note))
        db.commit()
    finally:
        db.close()

    state["form_updates"] = {}
    state["reply"] = f"Follow-up scheduled with {hcp or 'the HCP'} on {date}: {note}."
    return state


# Tool 5: SUMMARIZE INTERACTION -------------------------------------------
def summarize_interaction_node(state: AgentState) -> AgentState:
    """Ask the LLM to write a short professional summary of the current form."""
    form = state.get("current_form", {})
    prompt = (
        "Write a short, professional 2-sentence summary of this HCP interaction "
        "for a sales rep's records. Only use the information given:\n"
        + json.dumps(form)
    )
    response = llm.invoke(prompt)
    state["form_updates"] = {}
    state["reply"] = response.content.strip()
    return state


# A tiny fallback for when the LLM couldn't pick a tool.
def none_node(state: AgentState) -> AgentState:
    if not state.get("reply"):
        state["reply"] = "Could you tell me a bit more?"
    state["form_updates"] = {}
    return state


# ---------------------------------------------------------------------------
# 5. WIRE THE GRAPH TOGETHER
# ---------------------------------------------------------------------------
def _choose_tool(state: AgentState) -> str:
    """This decides which tool node to jump to, based on the LLM's choice."""
    valid = {
        "log_interaction", "edit_interaction", "clear_form",
        "schedule_followup", "summarize_interaction",
    }
    return state["tool_name"] if state["tool_name"] in valid else "none"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("log_interaction", log_interaction_node)
    graph.add_node("edit_interaction", edit_interaction_node)
    graph.add_node("clear_form", clear_form_node)
    graph.add_node("schedule_followup", schedule_followup_node)
    graph.add_node("summarize_interaction", summarize_interaction_node)
    graph.add_node("none", none_node)

    # Always start at the router.
    graph.add_edge(START, "router")

    # After the router, jump to whichever tool the LLM chose.
    graph.add_conditional_edges("router", _choose_tool, {
        "log_interaction": "log_interaction",
        "edit_interaction": "edit_interaction",
        "clear_form": "clear_form",
        "schedule_followup": "schedule_followup",
        "summarize_interaction": "summarize_interaction",
        "none": "none",
    })

    # Every tool finishes the run.
    for tool in ["log_interaction", "edit_interaction", "clear_form",
                 "schedule_followup", "summarize_interaction", "none"]:
        graph.add_edge(tool, END)

    return graph.compile()


# Build the graph once when this file is imported.
crm_agent = build_graph()


def run_agent(user_message: str, current_form: dict) -> dict:
    """Convenience function the API calls. Returns the reply + form updates."""
    result = crm_agent.invoke({
        "user_message": user_message,
        "current_form": current_form or {},
        "tool_name": "",
        "tool_args": {},
        "form_updates": {},
        "reply": "",
    })
    return {
        "reply": result["reply"],
        "formUpdates": result["form_updates"],
        "toolUsed": result["tool_name"],
    }
