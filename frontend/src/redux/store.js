import { configureStore } from '@reduxjs/toolkit';
import documentReducer from './documentSlice';
import questionReducer from './questionSlice';

export const store = configureStore({
  reducer: {
    document: documentReducer,
    questions: questionReducer,
  },
});
