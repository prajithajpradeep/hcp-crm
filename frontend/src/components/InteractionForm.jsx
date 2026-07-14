/*
 * InteractionForm.jsx
 * -------------------
 * The form on the LEFT side. Notice it does NOT keep its own state - it reads
 * every value straight from Redux. That is how the AI is able to fill it: the
 * AI updates Redux, and this form re-draws itself automatically.
 */
import { useSelector, useDispatch } from "react-redux";
import { setField } from "../formSlice";

export default function InteractionForm() {
  const form = useSelector((state) => state.form);
  const dispatch = useDispatch();

  // Helper so the fields can still be edited by hand if needed.
  const onChange = (field) => (e) =>
    dispatch(setField({ field, value: e.target.value }));

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

      <div className="field">
        <label>Sentiment</label>
        <input
          placeholder="positive / neutral / negative"
          value={form.sentiment}
          onChange={onChange("sentiment")}
        />
      </div>

      <p className="section-label">Materials Shared / Samples Distributed</p>
      <div className="field">
        <label>Materials Shared</label>
        <input
          placeholder="No materials added."
          value={form.materialsShared}
          onChange={onChange("materialsShared")}
        />
      </div>
    </div>
  );
}
