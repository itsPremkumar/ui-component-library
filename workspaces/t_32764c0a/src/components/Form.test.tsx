import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Form, FormField } from '../components/Form';

const fields: FormField[] = [
  { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'you@example.com' },
  { name: 'password', label: 'Password', type: 'password', required: true },
  { name: 'remember', label: 'Remember me', type: 'checkbox' },
];

describe('Form', () => {
  it('renders all fields', () => {
    render(<Form fields={fields} onSubmit={() => {}} />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Remember me')).toBeInTheDocument();
  });

  it('renders submit button with text', () => {
    render(<Form fields={fields} onSubmit={() => {}} submitText="Sign In" />);
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('calls onSubmit with form values', () => {
    const onSubmit = jest.fn();
    render(<Form fields={fields} onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ email: 'test@example.com', password: 'secret' })
    );
  });

  it('shows validation errors for required fields', () => {
    render(<Form fields={fields} onSubmit={() => {}} />);
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
  });

  it('shows error for invalid email', () => {
    render(<Form fields={fields} onSubmit={() => {}} />);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'invalid' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
  });

  it('renders reset button when showReset is true', () => {
    render(<Form fields={fields} onSubmit={() => {}} showReset resetText="Clear" />);
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('disables submit button when isLoading is true', () => {
    render(<Form fields={fields} onSubmit={() => {}} isLoading />);
    expect(screen.getByRole('button', { name: /submit/i })).toBeDisabled();
  });

  it('handles checkbox toggle', () => {
    const onSubmit = jest.fn();
    render(<Form fields={fields} onSubmit={onSubmit} />);
    const checkbox = screen.getByLabelText('Remember me');
    fireEvent.click(checkbox);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ remember: true })
    );
  });
});
