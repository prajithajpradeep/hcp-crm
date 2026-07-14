import { useSelector, useDispatch } from "react-redux";
import { setField } from "../formSlice";

export default function InteractionForm() {
  const form = useSelector((state) => state.form);
  const dispatch = useDispatch();

  const onChange = (field) => (e) =>
    dispatch(setField({ field, value: e.target.value }));

  // The AI sends sentiment as "positive" / "neutral" / "negative".
  // We lowercase it so the matching radio button lights up automatically.
  const sentiment = (form.sentiment || "").toLowerCase();
  const pickSentiment = (value) =>
    dispatch(setField({ field: "sentiment", value }));

  return (
    <div>
      <h2 className="title">Log HCP Interaction</h2>

      <p className="section-label">Interaction Details</p>

      <div className="row">
        <div className="field">
          <label>HCP Name</label>
          <input
            placeholder="Search or select HCP..."
            value={form.hcpName}
            onChange={onChange("hcpName")}
          />
        </div>
        <div className="field">
          <label>Interaction Type</label>
          <select value={form.interactionType} onChange={onChange("interactionType")}>
            <option>Meeting</option>
            <option>Call</option>
            <option>Email</option>
            <option>Virtual</option>
          </select>
        </div>
      </div>

      <div className="row">
        <div className="field">
          <label>Date</label>
          <input type="date" value={form.date} onChange={onChange("date")} />
        </div>
        <div className="field">
          <label>Time</label>
          <input type="time" value={form.time} onChange={onChange("time")} />
        </div>
      </div>

      <div className="field">
        <label>Attendees</label>
        <input
          placeholder="Enter names or search..."
          value={form.attendees}
          onChange={onChange("attendees")}
        />
      </div>

      <div className="field">
        <label>Topics Discussed</label>
        <textarea
          rows={4}
          placeholder="Enter key discussion points..."
          value={form.topicsDiscussed}
          onChange={onChange("topicsDiscussed")}
        />
      </div>

      <p style={{ color: "#2563eb", fontSize: 13, cursor: "pointer", margin: "0 0 16px" }}>
        🎙️ Summarize from Voice Note (Requires Consent)
      </p>

      <p className="section-label">Materials Shared / Samples Distributed</p>

      <div className="field">
        <label>Materials Shared</label>
        <input
          placeholder="No materials added."
          value={form.materialsShared}
          onChange={onChange("materialsShared")}
        />
      </div>

      <div className="field">
        <label>Samples Distributed</label>
        <input
          placeholder="No samples added."
          value={form.samplesDistributed}
          onChange={onChange("samplesDistributed")}
        />
      </div>

      <div className="field">
        <label>Observed / Inferred HCP Sentiment</label>
        <div style={{ display: "flex", gap: 24, marginTop: 4 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontWeight: 400 }}>
            <input
              type="radio"
              name="sentiment"
              checked={sentiment === "positive"}
              onChange={() => pickSentiment("positive")}
            />
            😊 Positive
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontWeight: 400 }}>
            <input
              type="radio"
              name="sentiment"
              checked={sentiment === "neutral"}
              onChange={() => pickSentiment("neutral")}
            />
            😐 Neutral
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontWeight: 400 }}>
            <input
              type="radio"
              name="sentiment"
              checked={sentiment === "negative"}
              onChange={() => pickSentiment("negative")}
            />
            😞 Negative
          </label>
        </div>
      </div>

      <div className="field">
        <label>Outcomes</label>
        <textarea
          rows={3}
          placeholder="Key outcomes or agreements..."
          value={form.outcomes}
          onChange={onChange("outcomes")}
        />
      </div>

      <div className="field">
        <label>Follow-up Actions</label>
        <textarea
          rows={3}
          placeholder="Next steps..."
          value={form.followUpActions}
          onChange={onChange("followUpActions")}
        />
      </div>
    </div>
  );
}