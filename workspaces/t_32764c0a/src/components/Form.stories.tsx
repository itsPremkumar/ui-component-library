import type { Meta, StoryObj } from '@storybook/react';
import { Form, FormField } from './Form';

const meta: Meta<typeof Form> = {
  title: 'Components/Form',
  component: Form,
  tags: ['autodocs'],
  argTypes: {
    isLoading: { control: 'boolean' },
    twoColumns: { control: 'boolean' },
    showReset: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Form>;

const contactFields: FormField[] = [
  { name: 'name', label: 'Full Name', required: true, placeholder: 'John Doe' },
  { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'john@example.com' },
  { name: 'subject', label: 'Subject', placeholder: 'How can we help?' },
  {
    name: 'message',
    label: 'Message',
    type: 'textarea',
    required: true,
    placeholder: 'Tell us more...',
  },
  {
    name: 'priority',
    label: 'Priority',
    type: 'select',
    options: [
      { label: 'Low', value: 'low' },
      { label: 'Medium', value: 'medium' },
      { label: 'High', value: 'high' },
    ],
  },
  { name: 'subscribe', label: 'Subscribe to newsletter', type: 'checkbox' },
];

export const Default: Story = {
  args: {
    fields: contactFields,
    onSubmit: (values) => console.log(values),
  },
};

export const Login: Story = {
  args: {
    fields: [
      { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'you@example.com' },
      { name: 'password', label: 'Password', type: 'password', required: true, placeholder: '••••••••' },
      { name: 'remember', label: 'Remember me', type: 'checkbox' },
    ],
    onSubmit: (values) => console.log(values),
    submitText: 'Sign In',
  },
};

export const Loading: Story = {
  args: {
    fields: contactFields,
    onSubmit: () => {},
    isLoading: true,
  },
};

export const TwoColumns: Story = {
  args: {
    fields: [
      { name: 'firstName', label: 'First Name', required: true },
      { name: 'lastName', label: 'Last Name', required: true },
      { name: 'email', label: 'Email', type: 'email', required: true },
      { name: 'phone', label: 'Phone', type: 'tel' },
      { name: 'company', label: 'Company' },
      { name: 'role', label: 'Role' },
    ],
    onSubmit: (values) => console.log(values),
    twoColumns: true,
  },
};

export const WithReset: Story = {
  args: {
    fields: [
      { name: 'search', label: 'Search', placeholder: 'Search...' },
    ],
    onSubmit: (values) => console.log(values),
    showReset: true,
  },
};
