import type { Meta, StoryObj } from '@storybook/react';
import { Input } from './Input';

const meta: Meta<typeof Input> = {
  title: 'Components/Input',
  component: Input,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    fullWidth: { control: 'boolean' },
    disabled: { control: 'boolean' },
    isSuccess: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: { placeholder: 'Enter text...' },
};

export const WithLabel: Story = {
  args: { label: 'Email', placeholder: 'you@example.com', type: 'email' },
};

export const WithHelperText: Story = {
  args: { label: 'Username', helperText: 'Must be 3-20 characters' },
};

export const WithError: Story = {
  args: { label: 'Email', error: 'Please enter a valid email', value: 'invalid' },
};

export const Success: Story = {
  args: { label: 'Username', isSuccess: true, value: 'valid_user' },
};

export const Small: Story = {
  args: { size: 'sm', placeholder: 'Small input' },
};

export const Large: Story = {
  args: { size: 'lg', placeholder: 'Large input' },
};

export const Disabled: Story = {
  args: { disabled: true, placeholder: 'Disabled input' },
};

export const Password: Story = {
  args: { type: 'password', label: 'Password', placeholder: '••••••••' },
};

export const WithAdornments: Story = {
  args: {
    label: 'Search',
    placeholder: 'Search...',
    leftAdornment: '🔍',
    rightAdornment: '⌘K',
  },
};
