import type { Meta, StoryObj } from '@storybook/react';
import { Chart } from './Chart';

const salesData = [
  { label: 'Jan', value: 6500 },
  { label: 'Feb', value: 5900 },
  { label: 'Mar', value: 8000 },
  { label: 'Apr', value: 8100 },
  { label: 'May', value: 5600 },
  { label: 'Jun', value: 9500 },
];

const pieData = [
  { label: 'Desktop', value: 45 },
  { label: 'Mobile', value: 35 },
  { label: 'Tablet', value: 20 },
];

const meta: Meta<typeof Chart> = {
  title: 'Components/Chart',
  component: Chart,
  tags: ['autodocs'],
  argTypes: {
    type: { control: 'select', options: ['bar', 'line', 'pie', 'area'] },
    showLegend: { control: 'boolean' },
    showGrid: { control: 'boolean' },
    animated: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Chart>;

export const BarChart: Story = {
  args: {
    type: 'bar',
    title: 'Monthly Sales ($)',
    data: salesData,
    formatValue: (v) => `$${v}`,
  },
};

export const LineChart: Story = {
  args: {
    type: 'line',
    title: 'Revenue Trend',
    data: salesData,
  },
};

export const PieChart: Story = {
  args: {
    type: 'pie',
    title: 'Device Share',
    data: pieData,
  },
};

export const AreaChart: Story = {
  args: {
    type: 'area',
    title: 'Growth',
    data: salesData,
  },
};
