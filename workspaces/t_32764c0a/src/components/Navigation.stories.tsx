import type { Meta, StoryObj } from '@storybook/react';
import { Navigation, NavItem } from './Navigation';

const meta: Meta<typeof Navigation> = {
  title: 'Components/Navigation',
  component: Navigation,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['horizontal', 'vertical', 'sidebar'] },
    collapsible: { control: 'boolean' },
    fixed: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Navigation>;

const navItems: NavItem[] = [
  { label: 'Dashboard', active: true, onClick: () => {} },
  { label: 'Projects', onClick: () => {} },
  {
    label: 'Settings',
    children: [
      { label: 'Profile', onClick: () => {} },
      { label: 'Security', onClick: () => {} },
      { label: 'Billing', onClick: () => {} },
    ],
  },
  { label: 'Help', disabled: true },
];

export const Horizontal: Story = {
  args: {
    items: navItems,
    variant: 'horizontal',
    brand: 'MyApp',
  },
};

export const Vertical: Story = {
  args: {
    items: navItems,
    variant: 'vertical',
  },
};

export const Sidebar: Story = {
  args: {
    items: navItems,
    variant: 'sidebar',
    brand: 'MyApp',
  },
};

export const Collapsible: Story = {
  args: {
    items: navItems,
    variant: 'sidebar',
    brand: 'MyApp',
    collapsible: true,
  },
};

export const WithIcons: Story = {
  args: {
    items: [
      { label: 'Home', icon: '🏠', active: true, onClick: () => {} },
      { label: 'Inbox', icon: '📥', onClick: () => {} },
      { label: 'Calendar', icon: '📅', onClick: () => {} },
      { label: 'Settings', icon: '⚙️', onClick: () => {} },
    ],
    variant: 'horizontal',
    brand: 'MyApp',
  },
};
