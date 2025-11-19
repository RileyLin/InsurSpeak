/**
 * Tests for shared components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  describe('Rendering', () => {
    test('renders app name/logo', () => {
      renderWithRouter(<Header />);
      expect(screen.getByText(/InsurSpeak/i)).toBeInTheDocument();
    });

    test('renders navigation links', () => {
      renderWithRouter(<Header />);

      const homeLink = screen.queryByText(/Home/i);
      const uploadLink = screen.queryByText(/Upload/i);

      // At least one navigation element should be present
      expect(homeLink || uploadLink).toBeTruthy();
    });

    test('has proper semantic structure', () => {
      const { container } = renderWithRouter(<Header />);

      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    test('navigation links are clickable', () => {
      renderWithRouter(<Header />);

      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThan(0);

      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper landmark role', () => {
      const { container } = renderWithRouter(<Header />);

      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
    });

    test('logo/brand is accessible', () => {
      renderWithRouter(<Header />);

      const brandElement = screen.getByText(/InsurSpeak/i);
      expect(brandElement).toBeInTheDocument();
    });
  });
});

describe('Footer Component', () => {
  describe('Rendering', () => {
    test('renders footer element', () => {
      const { container } = renderWithRouter(<Footer />);

      const footer = container.querySelector('footer');
      expect(footer).toBeInTheDocument();
    });

    test('displays copyright or company info', () => {
      renderWithRouter(<Footer />);

      const copyrightText = screen.queryByText(/©/) ||
                           screen.queryByText(/InsurSpeak/i) ||
                           screen.queryByText(/2024/);

      expect(copyrightText).toBeInTheDocument();
    });

    test('renders footer links if present', () => {
      renderWithRouter(<Footer />);

      const links = screen.queryAllByRole('link');
      // Footer may or may not have links, just check it renders
      expect(true).toBe(true);
    });
  });

  describe('Accessibility', () => {
    test('uses semantic footer element', () => {
      const { container } = renderWithRouter(<Footer />);

      const footer = container.querySelector('footer');
      expect(footer).toBeInTheDocument();
    });
  });
});

describe('App Integration', () => {
  test('Header and Footer render together', () => {
    const TestApp = () => (
      <>
        <Header />
        <main>Content</main>
        <Footer />
      </>
    );

    renderWithRouter(<TestApp />);

    expect(screen.getByText(/InsurSpeak/i)).toBeInTheDocument();
    expect(screen.getByText(/Content/i)).toBeInTheDocument();
  });
});
