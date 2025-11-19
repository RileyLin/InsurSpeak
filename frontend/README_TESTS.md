# InsurSpeak Frontend Tests

Comprehensive test suite for the InsurSpeak React frontend.

## Test Structure

```
src/
├── __tests__/
│   ├── HomePage.test.js        # Homepage component tests
│   ├── DocumentPage.test.js    # Document upload page tests
│   ├── SummaryPage.test.js     # Policy summary page tests
│   ├── ClaimsPage.test.js      # Claims analysis page tests (CORE VISION)
│   └── Components.test.js      # Shared components tests
└── setupTests.js               # Test configuration and global mocks
```

## Running Tests

### Run All Tests

```bash
cd frontend
npm test
```

### Run Tests in Watch Mode (default)

```bash
npm test
```

Press `a` to run all tests, `p` to filter by filename, `t` to filter by test name.

### Run Tests Once (for CI/CD)

```bash
npm test -- --watchAll=false
```

### Run Tests with Coverage

```bash
npm test -- --coverage --watchAll=false
```

Coverage report will be generated in `coverage/` directory.

### Run Specific Test File

```bash
npm test HomePage.test.js
```

### Run Tests Matching Pattern

```bash
npm test -- --testNamePattern="renders"
```

## Test Coverage

Current test coverage includes:

### Pages
- **HomePage**: Hero section, insurance types, expandable cards, navigation
- **DocumentPage**: File upload, insurance type selection, form validation
- **SummaryPage**: Policy summary display, benefits/exclusions, collapsible sections
- **ClaimsPage**: THE CORE VISION - situation analysis, recommendations display

### Components
- **Header**: Navigation, branding, accessibility
- **Footer**: Copyright, links, semantic HTML

### Features Tested
- ✅ Component rendering
- ✅ User interactions (clicks, form inputs)
- ✅ API calls and mocking
- ✅ Loading states
- ✅ Error handling
- ✅ Accessibility (a11y)
- ✅ Responsive design
- ✅ Navigation
- ✅ State management (Redux)

## Writing New Tests

### Basic Test Structure

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../components/MyComponent';

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  test('handles click', () => {
    render(<MyComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Clicked')).toBeInTheDocument();
  });
});
```

### Testing with Redux

```javascript
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import reducer from '../redux/mySlice';

const renderWithProviders = (component) => {
  const store = configureStore({ reducer: { mySlice: reducer } });
  return render(<Provider store={store}>{component}</Provider>);
};

test('component with Redux', () => {
  renderWithProviders(<MyComponent />);
  // assertions...
});
```

### Testing with Router

```javascript
import { BrowserRouter } from 'react-router-dom';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

test('component with routing', () => {
  renderWithRouter(<MyComponent />);
  // assertions...
});
```

### Testing Async Operations

```javascript
import { waitFor } from '@testing-library/react';

test('async operation', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ data: 'test' }),
  });

  render(<MyComponent />);

  await waitFor(() => {
    expect(screen.getByText('test')).toBeInTheDocument();
  });
});
```

## Mocking Strategy

### Global Mocks (in setupTests.js)

- **fetch**: All API calls mocked
- **localStorage**: Storage operations mocked
- **matchMedia**: For responsive components (Material-UI)

### Test-Specific Mocks

```javascript
beforeEach(() => {
  fetch.mockClear();
  localStorage.clear();
});

test('with mock', () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ result: 'success' }),
  });
  // test code...
});
```

## Common Testing Patterns

### Query Priorities (use in order)

1. `getByRole` - Accessibility-first
2. `getByLabelText` - Form elements
3. `getByPlaceholderText` - Input placeholders
4. `getByText` - Text content
5. `getByTestId` - Last resort

### Assertions

```javascript
// Element presence
expect(element).toBeInTheDocument();
expect(element).not.toBeInTheDocument();

// Text content
expect(element).toHaveTextContent('text');

// Form inputs
expect(input).toHaveValue('value');

// Attributes
expect(element).toHaveAttribute('href', '/path');

// Classes
expect(element).toHaveClass('className');
```

### Async Utilities

```javascript
// Wait for element
await waitFor(() => {
  expect(screen.getByText('loaded')).toBeInTheDocument();
});

// Find (async query)
const element = await screen.findByText('async content');
```

## Accessibility Testing

Every test should consider accessibility:

```javascript
test('is accessible', () => {
  const { container } = render(<MyComponent />);

  // Semantic HTML
  const nav = container.querySelector('nav');
  expect(nav).toBeInTheDocument();

  // ARIA labels
  const button = screen.getByRole('button', { name: 'Submit' });
  expect(button).toBeInTheDocument();

  // Alt text
  const img = screen.getByAltText('Description');
  expect(img).toBeInTheDocument();
});
```

## Performance Testing

```javascript
test('renders efficiently', () => {
  const { rerender } = render(<MyComponent count={0} />);

  rerender(<MyComponent count={1} />);
  rerender(<MyComponent count={2} />);

  // Should not cause unnecessary renders
});
```

## Snapshot Testing (use sparingly)

```javascript
test('matches snapshot', () => {
  const { container } = render(<MyComponent />);
  expect(container).toMatchSnapshot();
});
```

Update snapshots: `npm test -- -u`

## Debugging Tests

### See rendered HTML

```javascript
const { debug } = render(<MyComponent />);
debug(); // Prints DOM to console
```

### See specific element

```javascript
const element = screen.getByRole('button');
debug(element);
```

### Check available queries

```javascript
screen.logTestingPlaygroundURL();
// Opens browser with Testing Playground
```

## CI/CD Integration

Tests run automatically on every commit via GitHub Actions.

See `.github/workflows/test.yml` for configuration.

## Troubleshooting

### "Not wrapped in act(...)" warning

```javascript
await waitFor(() => {
  expect(screen.getByText('loaded')).toBeInTheDocument();
});
```

### Can't find element

```javascript
// Use query instead of get (doesn't throw)
expect(screen.queryByText('missing')).not.toBeInTheDocument();
```

### Async test timeout

```javascript
test('slow test', async () => {
  // Increase timeout
  jest.setTimeout(10000);
  await longOperation();
}, 10000); // Per-test timeout
```

## Best Practices

1. **Test behavior, not implementation**
2. **Write accessible tests** (use roles, labels)
3. **Avoid testing implementation details**
4. **Mock external dependencies**
5. **Test user flows, not units**
6. **Keep tests simple and focused**
7. **Use descriptive test names**

## Next Steps

- Add E2E tests with Cypress or Playwright
- Add visual regression tests
- Increase coverage to 90%+
- Add performance benchmarks
- Test mobile responsiveness more thoroughly
