from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db
from agent import run_agent

app = FastAPI(title="AI-First CRM - HCP Log Interaction")

# Allow the React app (running on a different port) to call this server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # fine for a local assignment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()  # create database tables if needed


# Describes the shape of the data the frontend sends us.
class ChatRequest(BaseModel):
    message: str
    currentForm: dict = {}


@app.get("/")
def health():
    return {"status": "ok", "message": "HCP CRM backend is running"}


@app.post("/chat")
def chat(req: ChatRequest):
    """The frontend calls this every time the user sends a chat message."""
    result = run_agent(req.message, req.currentForm)
    return result
