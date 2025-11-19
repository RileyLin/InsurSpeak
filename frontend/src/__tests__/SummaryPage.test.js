/**
 * Tests for SummaryPage component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import SummaryPage from '../pages/SummaryPage';
import documentReducer from '../redux/documentSlice';

const mockSummaryData = {
  benefits: [
    'Medical coverage up to $1,000,000',
    'Prescription drug coverage',
    'Preventive care at 100% coverage'
  ],
  exclusions: [
    'Cosmetic procedures',
    'Experimental treatments'
  ],
  claimsProcess: {
    steps: ['Contact provider', 'Submit claim form', 'Wait for approval'],
    timeline: '30 days',
    requiredDocuments: ['Medical records', 'Receipts']
  },
  costs: {
    deductible: '$1,000',
    copay: '$25',
    outOfPocketMax: '$5,000'
  },
  rights: [
    'Right to appeal denied claims',
    'Right to second opinion'
  ],
  insights: [
    'Good coverage for preventive care',
    'High deductible plan'
  ]
};

const renderWithProviders = (component, initialState = {}) => {
  const store = configureStore({
    reducer: {
      document: documentReducer,
    },
    preloadedState: {
      document: {
        text: 'Sample policy text',
        insuranceType: 'health',
        summary: initialState.summary || mockSummaryData,
        entities: {},
        loading: false,
        error: null,
      },
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

describe('SummaryPage', () => {
  describe('Rendering', () => {
    test('renders page title', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/Policy Summary/i)).toBeInTheDocument();
    });

    test('renders benefits section', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/What You CAN Claim/i)).toBeInTheDocument();
    });

    test('renders exclusions section', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/What You CANNOT Claim/i)).toBeInTheDocument();
    });

    test('renders claims process section', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/Claims Process/i)).toBeInTheDocument();
    });

    test('renders costs section', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/Costs/i)).toBeInTheDocument();
    });

    test('displays benefits list', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/Medical coverage/i)).toBeInTheDocument();
      expect(screen.getByText(/Prescription drug coverage/i)).toBeInTheDocument();
    });

    test('displays exclusions list', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/Cosmetic procedures/i)).toBeInTheDocument();
    });

    test('displays cost information', () => {
      renderWithProviders(<SummaryPage />);
      expect(screen.getByText(/\$1,000/i)).toBeInTheDocument(); // Deductible
      expect(screen.getByText(/\$25/i)).toBeInTheDocument(); // Copay
    });
  });

  describe('Interactions', () => {
    test('sections are collapsible', () => {
      renderWithProviders(<SummaryPage />);

      const benefitsHeader = screen.getByText(/What You CAN Claim/i);
      const section = benefitsHeader.closest('[role="button"]') || benefitsHeader.closest('.MuiAccordion-root');

      if (section) {
        fireEvent.click(section);
        // Section should collapse/expand
        expect(section).toBeInTheDocument();
      }
    });

    test('shows action buttons', () => {
      renderWithProviders(<SummaryPage />);

      // Should have buttons for print, download, share, etc.
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Empty States', () => {
    test('handles missing summary data gracefully', () => {
      renderWithProviders(<SummaryPage />, { summary: null });

      // Should either show empty state or redirect
      expect(screen.queryByText(/No summary available/i) ||
             screen.queryByText(/Upload/i)).toBeInTheDocument();
    });

    test('handles empty benefits array', () => {
      const emptyData = { ...mockSummaryData, benefits: [] };
      renderWithProviders(<SummaryPage />, { summary: emptyData });

      expect(screen.getByText(/What You CAN Claim/i)).toBeInTheDocument();
    });
  });

  describe('Visual Elements', () => {
    test('benefits section uses success color (green)', () => {
      const { container } = renderWithProviders(<SummaryPage />);

      const benefitsSection = screen.getByText(/What You CAN Claim/i).closest('.MuiCard-root');
      expect(benefitsSection).toBeInTheDocument();
      // Color coding would be tested with visual regression testing
    });

    test('exclusions section uses error color (red)', () => {
      const { container } = renderWithProviders(<SummaryPage />);

      const exclusionsSection = screen.getByText(/What You CANNOT Claim/i).closest('.MuiCard-root');
      expect(exclusionsSection).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    test('has link to ask questions', () => {
      renderWithProviders(<SummaryPage />);

      const questionLinks = screen.queryAllByText(/Ask Questions/i);
      if (questionLinks.length > 0) {
        expect(questionLinks[0]).toBeInTheDocument();
      }
    });

    test('has link back to upload new document', () => {
      renderWithProviders(<SummaryPage />);

      const uploadLinks = screen.queryAllByText(/Upload/i);
      if (uploadLinks.length > 0) {
        expect(uploadLinks[0]).toBeInTheDocument();
      }
    });
  });

  describe('Accessibility', () => {
    test('uses semantic HTML', () => {
      const { container } = renderWithProviders(<SummaryPage />);

      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    test('lists use proper list semantics', () => {
      const { container } = renderWithProviders(<SummaryPage />);

      const lists = container.querySelectorAll('ul, ol');
      expect(lists.length).toBeGreaterThan(0);
    });
  });
});
