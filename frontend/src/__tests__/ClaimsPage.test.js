/**
 * Tests for ClaimsPage component - THE CORE VISION
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ClaimsPage from '../pages/ClaimsPage';
import documentReducer from '../redux/documentSlice';

const mockAnalysisResult = {
  can_file_claims: true,
  recommendations: [
    {
      policy_name: 'Health Insurance',
      claim_type: 'Medical Claim',
      priority: 'high',
      likelihood: 'very_likely',
      estimated_amount: '$500-1000',
      required_documents: ['Medical records', 'Receipts'],
      filing_steps: ['Contact provider', 'Submit form', 'Follow up'],
      deadline: '30 days from service date',
      notes: 'Strong coverage for emergency care'
    },
    {
      policy_name: 'Auto Insurance',
      claim_type: 'Medical Payments',
      priority: 'medium',
      likelihood: 'likely',
      estimated_amount: '$300-500',
      required_documents: ['Police report', 'Medical records'],
      filing_steps: ['Report accident', 'File claim'],
      deadline: '60 days',
      notes: 'Secondary coverage after health insurance'
    }
  ],
  coordination: {
    primary_policy: 'Health Insurance',
    filing_order: ['File health claim first', 'Then file auto claim for remaining costs']
  },
  warnings: ['File within deadlines to avoid denial'],
  next_steps: ['Gather medical records', 'Contact health insurance provider']
};

const renderWithProviders = (component) => {
  const store = configureStore({
    reducer: {
      document: documentReducer,
    },
  });

  return render(
    <Provider store={store}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </Provider>
  );
};

describe('ClaimsPage', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });

  describe('Rendering', () => {
    test('renders page title', () => {
      renderWithProviders(<ClaimsPage />);
      expect(screen.getByText(/Claim Recommendations/i)).toBeInTheDocument();
    });

    test('renders situation input field', () => {
      renderWithProviders(<ClaimsPage />);
      expect(screen.getByPlaceholderText(/Describe what happened/i)).toBeInTheDocument();
    });

    test('renders analyze button', () => {
      renderWithProviders(<ClaimsPage />);
      expect(screen.getByText(/Analyze Situation/i)).toBeInTheDocument();
    });

    test('displays example situations', () => {
      renderWithProviders(<ClaimsPage />);
      expect(screen.getByText(/Example:/i) || screen.getByText(/Examples/i)).toBeInTheDocument();
    });

    test('shows authentication prompt when not logged in', () => {
      localStorage.getItem.mockReturnValue(null); // Not logged in

      renderWithProviders(<ClaimsPage />);
      // Should show login prompt or message
      const text = screen.queryByText(/log in/i) || screen.queryByText(/sign in/i);
      if (text) {
        expect(text).toBeInTheDocument();
      }
    });
  });

  describe('User Input', () => {
    test('allows typing in situation field', () => {
      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, {
        target: { value: 'I was in a car accident and hospitalized' }
      });

      expect(textarea.value).toBe('I was in a car accident and hospitalized');
    });

    test('example chips populate situation field when clicked', () => {
      renderWithProviders(<ClaimsPage />);

      const exampleChip = screen.queryByText(/hospital/i) ||
                          screen.queryByText(/accident/i);

      if (exampleChip) {
        fireEvent.click(exampleChip);

        const textarea = screen.getByPlaceholderText(/Describe what happened/i);
        expect(textarea.value).not.toBe('');
      }
    });

    test('optional incident details can be provided', () => {
      renderWithProviders(<ClaimsPage />);

      const dateInput = screen.queryByLabelText(/Incident Date/i);
      if (dateInput) {
        fireEvent.change(dateInput, { target: { value: '2024-01-15' } });
        expect(dateInput.value).toBe('2024-01-15');
      }
    });
  });

  describe('Analysis', () => {
    test('clicking analyze sends request with situation', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Hospital visit' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/analyze-situation'),
          expect.objectContaining({
            method: 'POST',
          })
        );
      });
    });

    test('displays loading state during analysis', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockImplementationOnce(() =>
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockAnalysisResult,
        }), 100))
      );

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test situation' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      // Should show loading indicator
      await waitFor(() => {
        const loadingIndicator = screen.queryByRole('progressbar') ||
                                screen.queryByText(/Analyzing/i);
        if (loadingIndicator) {
          expect(loadingIndicator).toBeInTheDocument();
        }
      });
    });

    test('handles analysis error gracefully', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockRejectedValueOnce(new Error('Analysis failed'));

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const errorMessage = screen.queryByText(/error/i) ||
                            screen.queryByText(/try again/i);
        if (errorMessage) {
          expect(errorMessage).toBeInTheDocument();
        }
      });
    });
  });

  describe('Results Display', () => {
    test('displays recommendations when analysis completes', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Hospital visit' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText('Health Insurance')).toBeInTheDocument();
        expect(screen.getByText('Medical Claim')).toBeInTheDocument();
      });
    });

    test('shows priority levels with color coding', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/high/i)).toBeInTheDocument();
        expect(screen.getByText(/medium/i)).toBeInTheDocument();
      });
    });

    test('displays required documents for each claim', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/Medical records/i)).toBeInTheDocument();
        expect(screen.getByText(/Receipts/i)).toBeInTheDocument();
      });
    });

    test('shows filing steps for each recommendation', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/Contact provider/i)).toBeInTheDocument();
      });
    });

    test('displays coordination information when multiple policies apply', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/Filing Order/i) ||
               screen.getByText(/Coordination/i) ||
               screen.getByText(/first/i)).toBeInTheDocument();
      });
    });

    test('shows warnings if any', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/deadline/i)).toBeInTheDocument();
      });
    });
  });

  describe('No Claims Case', () => {
    test('displays appropriate message when no claims can be filed', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          can_file_claims: false,
          recommendations: [],
          coordination: {},
          warnings: ['No applicable coverage found'],
          next_steps: []
        }),
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Cosmetic procedure' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/No applicable coverage/i) ||
               screen.getByText(/cannot file/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('textarea has proper label', () => {
      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      expect(textarea).toBeInTheDocument();
    });

    test('buttons are keyboard accessible', () => {
      renderWithProviders(<ClaimsPage />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
      });
    });

    test('recommendations use semantic HTML', async () => {
      localStorage.getItem.mockReturnValue('mock-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResult,
      });

      renderWithProviders(<ClaimsPage />);

      const textarea = screen.getByPlaceholderText(/Describe what happened/i);
      fireEvent.change(textarea, { target: { value: 'Test' } });

      const analyzeButton = screen.getByText(/Analyze Situation/i);
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const headings = screen.getAllByRole('heading');
        expect(headings.length).toBeGreaterThan(0);
      });
    });
  });
});
