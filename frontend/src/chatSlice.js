/*
 * chatSlice.js
 * ------------
 * Redux slice that stores the list of chat messages shown in the AI panel.
 * Each message looks like: { sender: "user" | "ai", text: "..." }
 */
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  messages: [
    {
      sender: "ai",
      text: 'Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.',
    },
  ],
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
  },
});

export const { addMessage } = chatSlice.actions;
export default chatSlice.reducer;
