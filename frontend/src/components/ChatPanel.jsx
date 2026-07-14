import { useState } from "react";
import axios from "axios";
import { useSelector, useDispatch } from "react-redux";
import { updateFields } from "../formSlice";
import { addMessage } from "../chatSlice";

const API_URL = "http://localhost:8000/chat";

export default function ChatPanel() {
  const dispatch = useDispatch();
  const messages = useSelector((state) => state.chat.messages);
  const currentForm = useSelector((state) => state.form);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // 1. Show the user's message.
    dispatch(addMessage({ sender: "user", text }));
    setInput("");
    setLoading(true);

    try {
      // 2 & 3. Ask the backend what to do.
      const res = await axios.post(API_URL, {
        message: text,
        currentForm,
      });

      const { reply, formUpdates } = res.data;

      // 4. Fill the form with whatever the AI extracted.
      if (formUpdates && Object.keys(formUpdates).length > 0) {
        dispatch(updateFields(formUpdates));
      }

      // Show the AI's reply.
      dispatch(addMessage({ sender: "ai", text: reply }));
    } catch (err) {
      dispatch(
        addMessage({
          sender: "ai",
          text: "Error contacting the server. Is the backend running on port 8000?",
        })
      );
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") send();
  };

  return (
    <div className="chat-wrap">
      <div className="chat-header">
        <span className="ai-title">🤖 AI Assistant</span>
        <p className="ai-sub">Log interaction details here via chat</p>
      </div>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.sender}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="bubble ai">Thinking…</div>}
      </div>

      <div className="chat-input">
        <input
          placeholder="Describe interaction..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <button onClick={send} disabled={loading}>
          Log
        </button>
      </div>
    </div>
  );
}
