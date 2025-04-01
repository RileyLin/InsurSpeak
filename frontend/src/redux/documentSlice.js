import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for uploading and processing a document
export const processDocument = createAsyncThunk(
  'document/process',
  async ({ file, textContent, insuranceType }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (textContent) {
        formData.append('text_content', textContent);
      }
      formData.append('insurance_type', insuranceType);

      const response = await axios.post('http://localhost:8000/process-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to process document');
    }
  }
);

const initialState = {
  originalText: '',
  processedText: '',
  terms: [],
  insuranceType: 'health', // Default type
  loading: false,
  error: null,
  currentDocument: null,
  isDocumentProcessed: false,
};

const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    setInsuranceType: (state, action) => {
      state.insuranceType = action.payload;
    },
    resetDocument: (state) => {
      return initialState;
    },
    highlightTerm: (state, action) => {
      const { termId } = action.payload;
      state.selectedTermId = termId;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(processDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(processDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.originalText = action.payload.original_text;
        state.terms = action.payload.terms;
        state.insuranceType = action.payload.insurance_type;
        state.isDocumentProcessed = true;
        state.currentDocument = {
          id: Date.now().toString(),
          name: 'Insurance Document',
          date: new Date().toISOString(),
        };
      })
      .addCase(processDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to process document';
      });
  },
});

export const { setInsuranceType, resetDocument, highlightTerm } = documentSlice.actions;

export default documentSlice.reducer;
