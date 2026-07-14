/*
 * App.jsx
 * -------
 * The top-level component. It just draws the split screen:
 *   LEFT  = the interaction form
 *   RIGHT = the AI assistant chat
 */
import InteractionForm from "./components/InteractionForm";
import ChatPanel from "./components/ChatPanel";

export default function App() {
  return (
    <div className="page">
      <div className="split">
        <div className="panel form-panel">
          <InteractionForm />
        </div>
        <div className="panel chat-panel">
          <ChatPanel />
        </div>
      </div>
    </div>
  );
}
