/*
 * formSlice.js
 * ------------
 * This is our Redux "slice" for the interaction form. A slice is just a bundle
 * of: (1) the data, and (2) the functions that change that data.
 *
 * The whole point of the assignment is that the AI fills this form, so we keep
 * the form's data here in Redux where both the form AND the chat panel can reach
 * it.
 */
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcpName: "",
  interactionType: "Meeting",
  date: "",
  time: "",
  attendees: "",
  topicsDiscussed: "",
  materialsShared: "",
  sentiment: "",
};

const formSlice = createSlice({
  name: "form",
  initialState,
  reducers: {
    // Change one field (used if you type in the form yourself).
    setField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
    },
    // Merge in several fields at once - this is what the AI uses to fill the form.
    updateFields: (state, action) => {
      return { ...state, ...action.payload };
    },
    // Wipe the form back to empty.
    resetForm: () => initialState,
  },
});

export const { setField, updateFields, resetForm } = formSlice.actions;
export default formSlice.reducer;
