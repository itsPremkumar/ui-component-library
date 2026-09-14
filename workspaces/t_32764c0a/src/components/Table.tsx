import React, { useState, useMemo } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export interface Column<T = Record<string, unknown>> {
  /** Column key */
  key: string;
  /** Column header */
  header: string;
  /** Cell renderer */
  render?: (value: unknown, row: T, index: number) => React.ReactNode;
  /** Whether column is sortable */
  sortable?: boolean;
  /** Column width */
  width?: string;
}

export interface TableProps<T = Record<string, unknown>> {
  /** Table columns */
  columns: Column<T>[];
  /** Table data */
  data: T[];
  /** Enable sorting */
  sortable?: boolean;
  /** Enable pagination */
  paginated?: boolean;
  /** Page size */
  pageSize?: number;
  /** Enable row selection */
  selectable?: boolean;
  /** Selected row keys */
  selectedKeys?: string[];
  /** Row key extractor */
  getRowKey?: (row: T, index: number) => string;
  /** Selection change handler */
  onSelectionChange?: (keys: string[]) => void;
  /** Empty state message */
  emptyMessage?: string;
  /** Theme mode */
  themeMode?: ThemeMode;
  /** Compact mode */
  compact?: boolean;
  /** Striped rows */
  striped?: boolean;
  /** Bordered table */
  bordered?: boolean;
}

export function Table<T = Record<string, unknown>>({
  columns,
  data,
  sortable = false,
  paginated = false,
  pageSize = 10,
  selectable = false,
  selectedKeys = [],
  getRowKey,
  onSelectionChange,
  emptyMessage = 'No data available',
  themeMode = 'light',
  compact = false,
  striped = true,
  bordered = false,
}: TableProps<T>) {
  const theme = getTheme(themeMode);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);

  const handleSort = (columnKey: string) => {
    if (!sortable) return;
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortable || !sortColumn) return data;
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortColumn];
      const bVal = (b as Record<string, unknown>)[sortColumn];
      const modifier = sortDirection === 'asc' ? 1 : -1;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * modifier;
      }
      return String(aVal).localeCompare(String(bVal)) * modifier;
    });
  }, [data, sortable, sortColumn, sortDirection]);

  const paginatedData = useMemo(() => {
    if (!paginated) return sortedData;
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, paginated, currentPage, pageSize]);

  const totalPages = Math.ceil(sortedData.length / pageSize);

  const toggleSelectAll = () => {
    if (!onSelectionChange) return;
    const allKeys = data.map((row, idx) => getRowKey?.(row, idx) || String(idx));
    if (selectedKeys.length === allKeys.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(allKeys);
    }
  };

  const toggleSelectRow = (key: string) => {
    if (!onSelectionChange) return;
    if (selectedKeys.includes(key)) {
      onSelectionChange(selectedKeys.filter((k) => k !== key));
    } else {
      onSelectionChange([...selectedKeys, key]);
    }
  };

  const tableStyles: React.CSSProperties = {
    width: '100%',
    borderCollapse: 'collapse',
    fontFamily: theme.typography.fontFamily,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text,
    border: bordered ? `1px solid ${theme.colors.border}` : 'none',
  };

  const thStyles: React.CSSProperties = {
    textAlign: 'left',
    padding: compact ? theme.spacing.sm : theme.spacing.md,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.textSecondary,
    backgroundColor: theme.colors.surface,
    borderBottom: `2px solid ${theme.colors.border}`,
    border: bordered ? `1px solid ${theme.colors.border}` : undefined,
    userSelect: (sortable ? 'pointer' : 'none') as React.CSSProperties['userSelect'],
    whiteSpace: 'nowrap',
  };

  const tdStyles: React.CSSProperties = {
    padding: compact ? theme.spacing.sm : theme.spacing.md,
    borderBottom: `1px solid ${theme.colors.border}`,
    border: bordered ? `1px solid ${theme.colors.border}` : undefined,
  };

  const rowStyles = (index: number): React.CSSProperties => ({
    backgroundColor: striped && index % 2 === 1 ? theme.colors.surface : 'transparent',
    transition: `background-color ${theme.transitions.fast}`,
  });

  const emptyStyles: React.CSSProperties = {
    padding: theme.spacing.xl,
    textAlign: 'center',
    color: theme.colors.textSecondary,
  };

  if (data.length === 0) {
    return (
      <div style={emptyStyles} role="status">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div style={{ overflow: 'auto' }}>
      <table style={tableStyles} role="grid">
        <thead>
          <tr>
            {selectable && (
              <th style={{ ...thStyles, width: '40px' }}>
                <input
                  type="checkbox"
                  checked={selectedKeys.length === data.length && data.length > 0}
                  onChange={toggleSelectAll}
                  aria-label="Select all rows"
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={col.key}
                style={{ ...thStyles, width: col.width }}
                onClick={() => col.sortable !== false && handleSort(col.key)}
                aria-sort={
                  sortColumn === col.key
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : undefined
                }
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs }}>
                  {col.header}
                  {sortable && col.sortable !== false && (
                    <span aria-hidden="true" style={{ opacity: sortColumn === col.key ? 1 : 0.3 }}>
                      {sortColumn === col.key && sortDirection === 'desc' ? '▼' : '▲'}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((row, rowIndex) => {
            const key = getRowKey?.(row, rowIndex) || String(rowIndex);
            return (
              <tr
                key={key}
                style={rowStyles(rowIndex)}
                aria-selected={selectable ? selectedKeys.includes(key) : undefined}
              >
                {selectable && (
                  <td style={tdStyles}>
                    <input
                      type="checkbox"
                      checked={selectedKeys.includes(key)}
                      onChange={() => toggleSelectRow(key)}
                      aria-label={`Select row ${key}`}
                    />
                  </td>
                )}
                {columns.map((col) => {
                  const cellValue = (row as Record<string, unknown>)[col.key];
                  return (
                    <td key={col.key} style={tdStyles}>
                      {col.render
                        ? col.render(cellValue, row, rowIndex)
                        : (cellValue as React.ReactNode) ?? ''}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>

      {paginated && totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: theme.spacing.sm,
            padding: theme.spacing.md,
          }}
          role="navigation"
          aria-label="Pagination"
        >
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            aria-label="Previous page"
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.md}`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              background: theme.colors.background,
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
              opacity: currentPage === 1 ? 0.5 : 1,
            }}
          >
            ←
          </button>
          <span style={{ color: theme.colors.textSecondary }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            aria-label="Next page"
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.md}`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              background: theme.colors.background,
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
              opacity: currentPage === totalPages ? 0.5 : 1,
            }}
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}
