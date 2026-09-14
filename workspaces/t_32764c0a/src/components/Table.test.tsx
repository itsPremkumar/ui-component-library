import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Table, Column } from '../components/Table';

interface TestRow {
  id: number;
  name: string;
  email: string;
}

const columns: Column<TestRow>[] = [
  { key: 'id', header: 'ID' },
  { key: 'name', header: 'Name' },
  { key: 'email', header: 'Email' },
];

const data: TestRow[] = [
  { id: 1, name: 'Alice', email: 'alice@test.com' },
  { id: 2, name: 'Bob', email: 'bob@test.com' },
];

describe('Table', () => {
  it('renders table headers', () => {
    render(<Table columns={columns} data={data} getRowKey={(row) => String(row.id)} />);
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  it('renders table data', () => {
    render(<Table columns={columns} data={data} getRowKey={(row) => String(row.id)} />);
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('bob@test.com')).toBeInTheDocument();
  });

  it('renders empty message when no data', () => {
    render(<Table columns={columns} data={[]} emptyMessage="No records" getRowKey={(row) => String(row.id)} />);
    expect(screen.getByText('No records')).toBeInTheDocument();
  });

  it('renders custom cell renderer', () => {
    const customColumns: Column<TestRow>[] = [
      { key: 'name', header: 'Name', render: (value) => <strong>{String(value)}</strong> },
    ];
    render(<Table columns={customColumns} data={data} getRowKey={(row) => String(row.id)} />);
    expect(screen.getByText('Alice').tagName).toBe('STRONG');
  });

  it('handles sorting when sortable prop is true', () => {
    render(<Table columns={columns} data={data} sortable getRowKey={(row) => String(row.id)} />);
    const nameHeader = screen.getByText('Name');
    fireEvent.click(nameHeader);
    expect(screen.getByText('Alice')).toBeInTheDocument();
  });

  it('handles row selection', () => {
    const onSelectionChange = jest.fn();
    render(
      <Table
        columns={columns}
        data={data}
        selectable
        selectedKeys={[]}
        onSelectionChange={onSelectionChange}
        getRowKey={(row) => String(row.id)}
      />
    );
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]);
    expect(onSelectionChange).toHaveBeenCalledWith(['1']);
  });

  it('renders pagination when paginated', () => {
    const manyData = Array.from({ length: 15 }, (_, i) => ({ id: i, name: `User ${i}`, email: `user${i}@test.com` }));
    render(
      <Table
        columns={columns}
        data={manyData}
        paginated
        pageSize={5}
        getRowKey={(row) => String(row.id)}
      />
    );
    expect(screen.getByText('Page 1 of 3')).toBeInTheDocument();
  });
});
