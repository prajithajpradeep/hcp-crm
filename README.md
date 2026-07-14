# AI-First CRM — HCP Log Interaction Screen

An AI-first CRM module for pharmaceutical sales reps to log interactions with
Healthcare Professionals (HCPs). Instead of filling a form by hand, you **talk to
an AI assistant** and it fills the form for you.

The AI is powered by **LangGraph** + a **Groq LLM (`openai/gpt-oss-20b`)**, and drives
**5 tools**.

---

## Tech stack

| Part     | Technology                   |
| -------- | ---------------------------- |
| Frontend | React + Redux Toolkit (Vite) |
| Backend  | Python + FastAPI             |
| AI agent | LangGraph                    |
| LLM      | Groq `openai/gpt-oss-20b`    |
| Database | MySQL                        |
| Font     | Google Inter                 |

---

## Role of the LangGraph agent

The LangGraph agent is the decision-making core that manages every HCP
interaction. When a sales rep types a message in the chat, the agent:

1. **Interprets intent** - it reads the natural-language message and, using the
   LLM, decides what the rep wants to do (log a new interaction, edit a field,
   clear the form, schedule a follow-up, or summarize).
2. **Extracts the data** - it pulls the relevant details out of plain English
   (HCP name, date, sentiment, topics, materials, etc.).
3. **Routes to the right tool** - based on that decision, it directs the request
   to one of the 5 tools, each of which performs a specific action.
4. **Returns the result** - the chosen tool updates the interaction form and/or
   the database, and the agent replies to the rep in the chat.

## The 5 LangGraph tools

**1. log_interaction**
Reads a natural-language description of a meeting, uses the LLM to extract the HCP name, date, sentiment, topics, and materials, fills the form, and saves the record to the database.

**2. edit_interaction**
Changes only the specific fields the user mentions (e.g. "actually the name was Dr. John"), leaving everything else untouched.

**3. clear_form**
Wipes all form fields so the rep can start a fresh interaction.

**4. schedule_followup**
Creates a follow-up task (defaults to one week out if no date is given) and saves it to the database.

**5. summarize_interaction**
Uses the LLM to write a short, professional summary of the interaction currently in the form. 

### How the agent works

`openai/gpt-oss-20b` is a small, fast model, and to keep the design simple and
robust we don't rely on a model's built-in "function calling." Instead, the
LangGraph **router node** asks the LLM to answer in plain JSON - which tool to
use and what values to extract - and then routes to the matching tool node. The
LLM still makes every decision and does every extraction, so this fully satisfies
the "must use LangGraph + an LLM to drive the tools" requirement, while being
easier to debug.

```
START -> router (LLM picks a tool) -> [one of 5 tool nodes] -> END
```

---

## How to run it

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
uvicorn main:app --reload
```

The API runs at http://localhost:8000

> **Groq key:** get a free one at https://console.groq.com/keys and paste it into
> `.env` as `GROQ_API_KEY`.

> **Database:** this project uses MySQL. Make sure MySQL is running and create a
> database called `hcp_crm` (`CREATE DATABASE hcp_crm;`), then set the
> `DATABASE_URL` line in `.env` to your MySQL connection string, e.g.
> `mysql+pymysql://root:PASSWORD@localhost:3306/hcp_crm`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL http://localhost:5173

---

## Prompts

1. **Log:** Today I met with Dr. Smith and discussed Product X efficiency. The sentiment was positive and I shared the brochures.
2. **Edit:** Sorry, the name was actually Dr. John and the sentiment was negative.
3. **Clear:** Clear the form.
4. **Follow-up:** Schedule a follow-up with Dr. Smith next week.
5. **Summarize:** Summarize this interaction.

---

## Project structure

**backend/** — Python + FastAPI + LangGraph

- `main.py` - FastAPI server with the /chat endpoint
- `agent.py` - the LangGraph agent and all 5 tools
- `database.py` - database tables
- `requirements.txt` - Python dependencies
- `.env.example` - sample environment file

**frontend/** — React + Redux (Vite)

- `index.html` - loads the Google Inter font
- `src/main.jsx` - app entry, connects Redux
- `src/store.js` - Redux store
- `src/formSlice.js` - form state
- `src/chatSlice.js` - chat messages
- `src/App.jsx` - split-screen layout
- `src/components/InteractionForm.jsx` = left panel
- `src/components/ChatPanel.jsx` - right panel
