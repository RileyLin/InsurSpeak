import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for asking questions about the document
export const askQuestion = createAsyncThunk(
  'questions/ask',
  async ({ question, documentText, insuranceType }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('question', question);
      formData.append('document_text', documentText);
      formData.append('insurance_type', insuranceType);

      const response = await axios.post('http://localhost:8000/ask-question', formData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to get answer');
    }
  }
);

const initialState = {
  questions: [],
  loading: false,
  error: null,
  currentQuestion: '',
};

const questionSlice = createSlice({
  name: 'questions',
  initialState,
  reducers: {
    setCurrentQuestion: (state, action) => {
      state.currentQuestion = action.payload;
    },
    clearQuestions: (state) => {
      state.questions = [];
      state.currentQuestion = '';
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(askQuestion.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(askQuestion.fulfilled, (state, action) => {
        state.loading = false;
        state.questions.push({
          id: Date.now().toString(),
          question: action.payload.question,
          answer: action.payload.answer,
          timestamp: new Date().toISOString(),
        });
        state.currentQuestion = '';
      })
      .addCase(askQuestion.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to get answer';
      });
  },
});

export const { setCurrentQuestion, clearQuestions } = questionSlice.actions;

export default questionSlice.reducer;
