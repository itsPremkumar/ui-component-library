import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Navigation, NavItem } from '../components/Navigation';

const navItems: NavItem[] = [
  { label: 'Home', active: true, onClick: jest.fn() },
  { label: 'About', onClick: jest.fn() },
  {
    label: 'Services',
    children: [
      { label: 'Web Dev', onClick: jest.fn() },
      { label: 'Mobile', onClick: jest.fn() },
    ],
  },
  { label: 'Contact', disabled: true },
];

describe('Navigation', () => {
  it('renders all nav items', () => {
    render(<Navigation items={navItems} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
    expect(screen.getByText('Services')).toBeInTheDocument();
    expect(screen.getByText('Contact')).toBeInTheDocument();
  });

  it('renders brand element', () => {
    render(<Navigation items={[]} brand={<span>MyBrand</span>} />);
    expect(screen.getByText('MyBrand')).toBeInTheDocument();
  });

  it('calls onClick when item is clicked', () => {
    const onClick = jest.fn();
    render(<Navigation items={[{ label: 'Click me', onClick }]} />);
    fireEvent.click(screen.getByText('Click me'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders with horizontal variant', () => {
    render(<Navigation items={navItems} variant="horizontal" />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveStyle({ flexDirection: 'row' });
  });

  it('renders with vertical variant', () => {
    render(<Navigation items={navItems} variant="vertical" />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveStyle({ flexDirection: 'column' });
  });

  it('renders with sidebar variant', () => {
    render(<Navigation items={navItems} variant="sidebar" />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveStyle({ flexDirection: 'column' });
  });

  it('shows dropdown on item with children', () => {
    render(<Navigation items={navItems} variant="horizontal" />);
    fireEvent.click(screen.getByText('Services'));
    expect(screen.getByText('Web Dev')).toBeInTheDocument();
    expect(screen.getByText('Mobile')).toBeInTheDocument();
  });

  it('renders collapsible toggle button', () => {
    render(<Navigation items={navItems} variant="sidebar" collapsible />);
    expect(screen.getByLabelText('Collapse navigation')).toBeInTheDocument();
  });

  it('toggles collapsed state', () => {
    render(<Navigation items={navItems} variant="sidebar" collapsible />);
    const toggle = screen.getByLabelText('Collapse navigation');
    fireEvent.click(toggle);
    expect(screen.getByLabelText('Expand navigation')).toBeInTheDocument();
  });

  it('marks disabled items', () => {
    render(<Navigation items={navItems} />);
    const contactItem = screen.getByText('Contact').closest('[role="button"]');
    expect(contactItem).toHaveAttribute('aria-disabled', 'true');
  });
});
