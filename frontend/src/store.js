/*
 * store.js
 * --------
 * The Redux "store" is the single place that holds ALL app state.
 * We combine our two slices (form + chat) into it here.
 */
import { configureStore } from "@reduxjs/toolkit";
import formReducer from "./formSlice";
import chatReducer from "./chatSlice";

export const store = configureStore({
  reducer: {
    form: formReducer,
    chat: chatReducer,
  },
});
