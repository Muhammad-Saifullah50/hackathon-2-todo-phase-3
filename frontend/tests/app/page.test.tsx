import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Page from '@/app/page';

describe('Home Page', () => {
  it('renders the welcome message', () => {
    render(<Page />);
    // Use getAllByText because "Todo application" appears in both title and paragraph
    const elements = screen.getAllByText(/Todo Application/i);
    expect(elements.length).toBeGreaterThan(0);
  });

  it('displays the application description', () => {
    render(<Page />);
    // The text is broken up by <strong> tags, so we use a function matcher
    expect(
      screen.getByText((content) => content.includes('Welcome to the modernized version'))
    ).toBeDefined();
  });
});
