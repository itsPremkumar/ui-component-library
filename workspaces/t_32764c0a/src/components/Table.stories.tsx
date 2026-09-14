import type { Meta, StoryObj } from '@storybook/react';
import { Table, Column } from './Table';

interface UserData {
  id: number;
  name: string;
  email: string;
  role: string;
  status: string;
}

const sampleData: UserData[] = [
  { id: 1, name: 'Alice Johnson', email: 'alice@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Bob Smith', email: 'bob@example.com', role: 'Editor', status: 'Active' },
  { id: 3, name: 'Carol White', email: 'carol@example.com', role: 'Viewer', status: 'Inactive' },
  { id: 4, name: 'David Brown', email: 'david@example.com', role: 'Editor', status: 'Active' },
  { id: 5, name: 'Eve Davis', email: 'eve@example.com', role: 'Admin', status: 'Active' },
];

const columns: Column<UserData>[] = [
  { key: 'id', header: 'ID', width: '60px' },
  { key: 'name', header: 'Name' },
  { key: 'email', header: 'Email' },
  { key: 'role', header: 'Role', width: '100px' },
  {
    key: 'status',
    header: 'Status',
    width: '100px',
    render: (value) => (
      <span
        style={{
          padding: '2px 8px',
          borderRadius: '4px',
          fontSize: '12px',
          backgroundColor: value === 'Active' ? '#dcfce7' : '#fee2e2',
          color: value === 'Active' ? '#166534' : '#991b1b',
        }}
      >
        {String(value)}
      </span>
    ),
  },
];

const meta: Meta<typeof Table> = {
  title: 'Components/Table',
  component: Table,
  tags: ['autodocs'],
  argTypes: {
    sortable: { control: 'boolean' },
    paginated: { control: 'boolean' },
    selectable: { control: 'boolean' },
    compact: { control: 'boolean' },
    striped: { control: 'boolean' },
    bordered: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Table<UserData>>;

export const Default: Story = {
  args: { columns, data: sampleData, getRowKey: (row) => String(row.id) },
};

export const Sortable: Story = {
  args: { columns, data: sampleData, sortable: true, getRowKey: (row) => String(row.id) },
};

export const Paginated: Story = {
  args: { columns, data: sampleData, paginated: true, pageSize: 2, getRowKey: (row) => String(row.id) },
};

export const Selectable: Story = {
  args: { columns, data: sampleData, selectable: true, getRowKey: (row) => String(row.id) },
};

export const Compact: Story = {
  args: { columns, data: sampleData, compact: true, getRowKey: (row) => String(row.id) },
};

export const Bordered: Story = {
  args: { columns, data: sampleData, bordered: true, getRowKey: (row) => String(row.id) },
};

export const Empty: Story = {
  args: { columns, data: [], emptyMessage: 'No users found' },
};
