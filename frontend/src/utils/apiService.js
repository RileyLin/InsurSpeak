import axios from 'axios';

// Base API URL
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
const apiService = {
  // Process document (PDF upload or text input)
  async processDocument(formData) {
    try {
      const response = await apiClient.post('/process-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Ask a question about the insurance document
  async askQuestion(formData) {
    try {
      const response = await apiClient.post('/ask-question', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// Helper function to handle API errors
const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // The server responded with a status code outside the 2xx range
    return new Error(error.response.data?.detail || 'Server error. Please try again.');
  } else if (error.request) {
    // The request was made but no response was received
    return new Error('No response from server. Please check your connection.');
  } else {
    // Something happened in setting up the request
    return new Error('Error making request. Please try again.');
  }
};

export default apiService;
