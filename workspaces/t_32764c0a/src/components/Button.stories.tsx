import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['solid', 'outline', 'ghost', 'link'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    colorScheme: { control: 'select', options: ['primary', 'secondary', 'danger', 'success'] },
    fullWidth: { control: 'boolean' },
    isLoading: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Solid: Story = {
  args: { children: 'Button', variant: 'solid' },
};

export const Outline: Story = {
  args: { children: 'Button', variant: 'outline' },
};

export const Ghost: Story = {
  args: { children: 'Button', variant: 'ghost' },
};

export const Link: Story = {
  args: { children: 'Button', variant: 'link' },
};

export const Small: Story = {
  args: { children: 'Small Button', size: 'sm' },
};

export const Large: Story = {
  args: { children: 'Large Button', size: 'lg' },
};

export const Primary: Story = {
  args: { children: 'Primary', colorScheme: 'primary' },
};

export const Secondary: Story = {
  args: { children: 'Secondary', colorScheme: 'secondary' },
};

export const Danger: Story = {
  args: { children: 'Danger', colorScheme: 'danger' },
};

export const Success: Story = {
  args: { children: 'Success', colorScheme: 'success' },
};

export const Loading: Story = {
  args: { children: 'Loading...', isLoading: true },
};

export const Disabled: Story = {
  args: { children: 'Disabled', disabled: true },
};

export const FullWidth: Story = {
  args: { children: 'Full Width Button', fullWidth: true },
};
