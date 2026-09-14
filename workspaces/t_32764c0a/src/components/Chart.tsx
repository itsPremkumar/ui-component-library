import React, { useMemo } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export type ChartType = 'bar' | 'line' | 'pie' | 'area';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ChartProps {
  /** Chart type */
  type?: ChartType;
  /** Chart data */
  data: ChartDataPoint[];
  /** Chart title */
  title?: string;
  /** Width of chart */
  width?: number | string;
  /** Height of chart */
  height?: number;
  /** Show legend */
  showLegend?: boolean;
  /** Show grid lines */
  showGrid?: boolean;
  /** Color palette */
  colors?: string[];
  /** Theme mode */
  themeMode?: ThemeMode;
  /** Y-axis formatter */
  formatValue?: (value: number) => string;
  /** Animation */
  animated?: boolean;
}

const DEFAULT_COLORS = [
  '#2563eb', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#10b981', '#f97316', '#6366f1',
];

export function Chart({
  type = 'bar',
  data,
  title,
  width = '100%',
  height = 300,
  showLegend = true,
  showGrid = true,
  colors = DEFAULT_COLORS,
  themeMode = 'light',
  formatValue,
  animated = true,
}: ChartProps) {
  const theme = getTheme(themeMode);

  const maxValue = useMemo(() => Math.max(...data.map((d) => d.value), 0), [data]);
  const totalValue = useMemo(() => data.reduce((sum, d) => sum + d.value, 0), [data]);

  const chartStyles: React.CSSProperties = {
    width,
    fontFamily: theme.typography.fontFamily,
    color: theme.colors.text,
  };

  const titleStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    marginBottom: theme.spacing.md,
    color: theme.colors.text,
  };

  const legendStyles: React.CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing.md,
    marginTop: theme.spacing.md,
  };

  const legendItemStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  };

  const swatchStyles = (color: string): React.CSSProperties => ({
    width: '12px',
    height: '12px',
    borderRadius: theme.borderRadius.sm,
    backgroundColor: color,
  });

  const getColor = (index: number, point: ChartDataPoint) =>
    point.color || colors[index % colors.length];

  const renderBarChart = () => {
    const barWidth = Math.max(20, Math.min(60, (100 / data.length) - 10));
    return (
      <svg width="100%" height={height} viewBox={`0 0 600 ${height}`} role="img" aria-label={title || 'Bar chart'}>
        {showGrid && maxValue > 0 && (
          <>
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
              <line
                key={ratio}
                x1={50}
                y1={height - 40 - (height - 60) * ratio}
                x2={590}
                y2={height - 40 - (height - 60) * ratio}
                stroke={theme.colors.border}
                strokeDasharray="4,4"
              />
            ))}
          </>
        )}
        {data.map((point, index) => {
          const x = 50 + (index * 540) / data.length + 5;
          const barHeight = maxValue > 0 ? ((point.value / maxValue) * (height - 60)) : 0;
          const color = getColor(index, point);
          return (
            <g key={index}>
              <rect
                x={x}
                y={height - 40 - barHeight}
                width={barWidth}
                height={barHeight}
                fill={color}
                rx={4}
                style={{
                  transition: animated ? `height ${theme.transitions.slow}` : undefined,
                }}
              />
              <text
                x={x + barWidth / 2}
                y={height - 20}
                textAnchor="middle"
                fontSize={11}
                fill={theme.colors.textSecondary}
              >
                {point.label.length > 8 ? point.label.slice(0, 8) + '…' : point.label}
              </text>
              <text
                x={x + barWidth / 2}
                y={height - 45 - barHeight}
                textAnchor="middle"
                fontSize={11}
                fill={theme.colors.text}
                fontWeight="600"
              >
                {formatValue ? formatValue(point.value) : point.value}
              </text>
            </g>
          );
        })}
        {/* X-axis line */}
        <line x1={50} y1={height - 40} x2={590} y2={height - 40} stroke={theme.colors.border} />
      </svg>
    );
  };

  const renderLineChart = () => {
    const points = data.map((point, index) => {
      const x = 50 + (index * 540) / Math.max(data.length - 1, 1);
      const y = height - 40 - (maxValue > 0 ? (point.value / maxValue) * (height - 60) : 0);
      return { x, y, ...point };
    });

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

    return (
      <svg width="100%" height={height} viewBox={`0 0 600 ${height}`} role="img" aria-label={title || 'Line chart'}>
        {showGrid && (
          <>
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
              <line
                key={ratio}
                x1={50}
                y1={height - 40 - (height - 60) * ratio}
                x2={590}
                y2={height - 40 - (height - 60) * ratio}
                stroke={theme.colors.border}
                strokeDasharray="4,4"
              />
            ))}
          </>
        )}
        <path
          d={pathD}
          fill="none"
          stroke={colors[0]}
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r={6} fill={colors[0]} stroke={theme.colors.background} strokeWidth={2} />
            <text
              x={p.x}
              y={height - 20}
              textAnchor="middle"
              fontSize={11}
              fill={theme.colors.textSecondary}
            >
              {p.label.length > 8 ? p.label.slice(0, 8) + '…' : p.label}
            </text>
          </g>
        ))}
        <line x1={50} y1={height - 40} x2={590} y2={height - 40} stroke={theme.colors.border} />
      </svg>
    );
  };

  const renderPieChart = () => {
    const cx = 200;
    const cy = height / 2;
    const radius = Math.min(150, (height - 80) / 2);
    let currentAngle = -Math.PI / 2;

    return (
      <svg width="100%" height={height} viewBox={`0 0 600 ${height}`} role="img" aria-label={title || 'Pie chart'}>
        {data.map((point, index) => {
          const angle = totalValue > 0 ? (point.value / totalValue) * Math.PI * 2 : 0;
          const startAngle = currentAngle;
          const endAngle = currentAngle + angle;
          currentAngle = endAngle;

          const x1 = cx + radius * Math.cos(startAngle);
          const y1 = cy + radius * Math.sin(startAngle);
          const x2 = cx + radius * Math.cos(endAngle);
          const y2 = cy + radius * Math.sin(endAngle);

          const largeArc = angle > Math.PI ? 1 : 0;
          const pathData = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

          const midAngle = startAngle + angle / 2;
          const labelX = cx + (radius * 0.7) * Math.cos(midAngle);
          const labelY = cy + (radius * 0.7) * Math.sin(midAngle);

          const color = getColor(index, point);
          const percentage = totalValue > 0 ? ((point.value / totalValue) * 100).toFixed(1) : '0';

          return (
            <g key={index}>
              <path d={pathData} fill={color} stroke={theme.colors.background} strokeWidth={2}>
                <title>{point.label}: {formatValue ? formatValue(point.value) : point.value} ({percentage}%)</title>
              </path>
              {angle > 0.3 && (
                <text x={labelX} y={labelY} textAnchor="middle" dominantBaseline="middle" fontSize={11} fill="#ffffff" fontWeight="600">
                  {percentage}%
                </text>
              )}
            </g>
          );
        })}
        {/* Legend on the right */}
        {showLegend && (
          <g transform={`translate(400, ${height / 2 - data.length * 10})`}>
            {data.map((point, index) => {
              const color = getColor(index, point);
              const percentage = totalValue > 0 ? ((point.value / totalValue) * 100).toFixed(1) : '0';
              return (
                <g key={index} transform={`translate(0, ${index * 24})`}>
                  <rect width={12} height={12} fill={color} rx={2} />
                  <text x={18} y={11} fontSize={11} fill={theme.colors.text}>
                    {point.label} ({percentage}%)
                  </text>
                </g>
              );
            })}
          </g>
        )}
      </svg>
    );
  };

  const renderAreaChart = () => {
    const points = data.map((point, index) => {
      const x = 50 + (index * 540) / Math.max(data.length - 1, 1);
      const y = height - 40 - (maxValue > 0 ? (point.value / maxValue) * (height - 60) : 0);
      return { x, y };
    });

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    const areaD = `${pathD} L ${points[points.length - 1].x} ${height - 40} L ${points[0].x} ${height - 40} Z`;

    return (
      <svg width="100%" height={height} viewBox={`0 0 600 ${height}`} role="img" aria-label={title || 'Area chart'}>
        <defs>
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={colors[0]} stopOpacity={0.4} />
            <stop offset="100%" stopColor={colors[0]} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        {showGrid && (
          <>
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
              <line
                key={ratio}
                x1={50}
                y1={height - 40 - (height - 60) * ratio}
                x2={590}
                y2={height - 40 - (height - 60) * ratio}
                stroke={theme.colors.border}
                strokeDasharray="4,4"
              />
            ))}
          </>
        )}
        <path d={areaD} fill="url(#areaGradient)" />
        <path d={pathD} fill="none" stroke={colors[0]} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r={5} fill={colors[0]} stroke={theme.colors.background} strokeWidth={2} />
            <text
              x={p.x}
              y={height - 20}
              textAnchor="middle"
              fontSize={11}
              fill={theme.colors.textSecondary}
            >
              {data[i].label.length > 8 ? data[i].label.slice(0, 8) + '…' : data[i].label}
            </text>
          </g>
        ))}
        <line x1={50} y1={height - 40} x2={590} y2={height - 40} stroke={theme.colors.border} />
      </svg>
    );
  };

  const renderChart = () => {
    switch (type) {
      case 'line': return renderLineChart();
      case 'pie': return renderPieChart();
      case 'area': return renderAreaChart();
      default: return renderBarChart();
    }
  };

  return (
    <div style={chartStyles}>
      {title && <div style={titleStyles}>{title}</div>}
      {renderChart()}
      {showLegend && type !== 'pie' && (
        <div style={legendStyles}>
          {data.map((point, index) => (
            <div key={index} style={legendItemStyles}>
              <span style={swatchStyles(getColor(index, point))} />
              {point.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
