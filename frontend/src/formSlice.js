import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcpName: "",
  interactionType: "Meeting",
  date: "",
  time: "",
  attendees: "",
  topicsDiscussed: "",
  materialsShared: "",
  samplesDistributed: "",
  sentiment: "",
  outcomes: "",
  followUpActions: "",
};

const formSlice = createSlice({
  name: "form",
  initialState,
  reducers: {
    setField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
    },
    updateFields: (state, action) => {
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState,
  },
});

export const { setField, updateFields, resetForm } = formSlice.actions;
export default formSlice.reducer;