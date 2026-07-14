# AI-First CRM — HCP Log Interaction Screen

An AI-first CRM module for pharmaceutical sales reps to log interactions with
Healthcare Professionals (HCPs). Instead of filling a form by hand, you **talk to
an AI assistant** and it fills the form for you.

The AI is powered by **LangGraph** + a **Groq LLM (`openai/gpt-oss-20b`)**, and drives
**5 tools**.

---

## What it looks like

A split screen:

- **Left:** the "Log HCP Interaction" form.
- **Right:** an AI Assistant chat. You type a plain sentence, and the assistant
  fills or edits the form on the left.

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

## The 5 LangGraph tools

| #   | Tool                      | What it does                                                                                                                                                                         |
| --- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **log_interaction**       | Reads a natural-language description of a meeting, uses the LLM to extract HCP name, date, sentiment, topics, materials, etc., fills the form, and saves the record to the database. |
| 2   | **edit_interaction**      | Changes only the specific fields the user mentions (e.g. "actually the name was Dr. John"), leaving everything else untouched.                                                       |
| 3   | **clear_form**            | Wipes all form fields so the rep can start a fresh interaction.                                                                                                                      |
| 4   | **schedule_followup**     | Creates a follow-up task (defaults to one week out if no date is given) and saves it.                                                                                                |
| 5   | **summarize_interaction** | Uses the LLM to write a short professional summary of the interaction currently in the form.                                                                                         |

### How the agent works (design note)

`openai/gpt-oss-20b` is a small, fast model, and to keep the design simple and
robust we don't rely on a model's built-in "function calling." Instead, the
LangGraph **router node** asks the LLM to answer in plain JSON — _which tool to
use and what values to extract_ — and then routes to the matching tool node. The
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
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then open .env and paste your Groq API key
uvicorn main:app --reload
```

The API now runs at http://localhost:8000

> **Groq key:** get a free one at https://console.groq.com/keys and paste it into
> `.env` as `GROQ_API_KEY`.

> **Database:** this project uses MySQL. Make sure MySQL is running and create a
> database called `hcp_crm` (`CREATE DATABASE hcp_crm;`), then set the
> `DATABASE_URL` line in `.env` to your MySQL connection string, e.g.
> `mysql+pymysql://root:YOURPASSWORD@localhost:3306/hcp_crm`.

### 2. Frontend

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Open the URL it prints (usually http://localhost:5173).

---

## Try these prompts

1. **Log:** `Today I met with Dr. Smith and discussed Product X efficiency. The sentiment was positive and I shared the brochures.`
2. **Edit:** `Sorry, the name was actually Dr. John and the sentiment was negative.`
3. **Clear:** `Clear the form.`
4. **Follow-up:** `Schedule a follow-up with Dr. Smith next week.`
5. **Summarize:** `Summarize this interaction.`

---

## Project structure

```
hcp-crm/
├── backend/
│   ├── main.py            # FastAPI server + /chat endpoint
│   ├── agent.py           # LangGraph agent + the 5 tools  <-- the brain
│   ├── database.py        # database tables (SQLAlchemy)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html         # loads the Inter font
    └── src/
        ├── main.jsx       # app entry, connects Redux
        ├── store.js       # Redux store
        ├── formSlice.js   # form state (the AI fills this)
        ├── chatSlice.js   # chat messages
        ├── App.jsx        # split-screen layout
        └── components/
            ├── InteractionForm.jsx   # left panel
            └── ChatPanel.jsx         # right panel (talks to backend)
```
