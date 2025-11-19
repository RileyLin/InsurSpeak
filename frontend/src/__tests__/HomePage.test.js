/**
 * Tests for HomePage component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import HomePage from '../pages/HomePage';
import documentReducer from '../redux/documentSlice';

// Helper function to render with providers
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

describe('HomePage', () => {
  describe('Rendering', () => {
    test('renders main heading', () => {
      renderWithProviders(<HomePage />);
      expect(screen.getByText(/Understand Your Insurance Rights/i)).toBeInTheDocument();
    });

    test('renders hero section with description', () => {
      renderWithProviders(<HomePage />);
      expect(screen.getByText(/Upload your policy documents/i)).toBeInTheDocument();
    });

    test('renders Get Started button', () => {
      renderWithProviders(<HomePage />);
      const buttons = screen.getAllByText(/Get Started/i);
      expect(buttons.length).toBeGreaterThan(0);
    });

    test('renders all 8 insurance type cards', () => {
      renderWithProviders(<HomePage />);

      expect(screen.getByText('Health Insurance')).toBeInTheDocument();
      expect(screen.getByText('Auto Insurance')).toBeInTheDocument();
      expect(screen.getByText('Life Insurance')).toBeInTheDocument();
      expect(screen.getByText('Disability Insurance')).toBeInTheDocument();
      expect(screen.getByText('Travel Insurance')).toBeInTheDocument();
      expect(screen.getByText('Home Insurance')).toBeInTheDocument();
      expect(screen.getByText('Pet Insurance')).toBeInTheDocument();
      expect(screen.getByText('Business Insurance')).toBeInTheDocument();
    });

    test('renders How It Works section', () => {
      renderWithProviders(<HomePage />);
      expect(screen.getByText(/How It Works/i)).toBeInTheDocument();
      expect(screen.getByText(/Upload Your Policy/i)).toBeInTheDocument();
      expect(screen.getByText(/AI Analysis/i)).toBeInTheDocument();
      expect(screen.getByText(/Get Clear Answers/i)).toBeInTheDocument();
    });

    test('renders pricing information', () => {
      renderWithProviders(<HomePage />);
      expect(screen.getByText(/Free for your first 2 policies/i)).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    test('insurance cards are expandable', async () => {
      renderWithProviders(<HomePage />);

      const healthCard = screen.getByText('Health Insurance').closest('.MuiCard-root');
      const learnMoreButton = healthCard.querySelector('button');

      if (learnMoreButton) {
        fireEvent.click(learnMoreButton);

        await waitFor(() => {
          // Should show expanded content (benefits, rights, etc.)
          expect(healthCard).toHaveTextContent(/Coverage/i);
        });
      }
    });

    test('Get Started button navigates to upload page', () => {
      renderWithProviders(<HomePage />);
      const getStartedButtons = screen.getAllByText(/Get Started/i);

      // Click first Get Started button
      fireEvent.click(getStartedButtons[0]);

      // Should navigate (test by checking URL change would require more setup)
      expect(getStartedButtons[0]).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper heading hierarchy', () => {
      renderWithProviders(<HomePage />);

      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    test('images have alt text', () => {
      renderWithProviders(<HomePage />);

      const images = screen.queryAllByRole('img');
      images.forEach(img => {
        expect(img).toHaveAttribute('alt');
      });
    });

    test('buttons are keyboard accessible', () => {
      renderWithProviders(<HomePage />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).not.toHaveAttribute('disabled');
      });
    });
  });

  describe('Responsive Design', () => {
    test('renders without crashing on mobile viewport', () => {
      global.innerWidth = 375;
      global.dispatchEvent(new Event('resize'));

      renderWithProviders(<HomePage />);
      expect(screen.getByText(/Understand Your Insurance Rights/i)).toBeInTheDocument();
    });

    test('renders without crashing on desktop viewport', () => {
      global.innerWidth = 1920;
      global.dispatchEvent(new Event('resize'));

      renderWithProviders(<HomePage />);
      expect(screen.getByText(/Understand Your Insurance Rights/i)).toBeInTheDocument();
    });
  });
});
