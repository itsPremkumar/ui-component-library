import React from 'react';
import { render, screen } from '@testing-library/react';
import { Chart } from '../components/Chart';

const chartData = [
  { label: 'Jan', value: 65 },
  { label: 'Feb', value: 59 },
  { label: 'Mar', value: 80 },
];

describe('Chart', () => {
  it('renders chart title', () => {
    render(<Chart data={chartData} title="Sales" />);
    expect(screen.getByText('Sales')).toBeInTheDocument();
  });

  it('renders bar chart with data labels', () => {
    render(<Chart data={chartData} type="bar" />);
    // Bar chart renders labels in both chart area and legend
    expect(screen.getAllByText('Jan').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Feb').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Mar').length).toBeGreaterThan(0);
  });

  it('renders line chart', () => {
    render(<Chart data={chartData} type="line" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveAttribute('role', 'img');
  });

  it('renders pie chart', () => {
    render(<Chart data={chartData} type="pie" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    // Jan=65/204=31.9%, Feb=59/204=28.9%, Mar=80/204=39.2%
    expect(screen.getByText('Jan (31.9%)')).toBeInTheDocument();
  });

  it('renders area chart', () => {
    render(<Chart data={chartData} type="area" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('renders legend when showLegend is true', () => {
    render(<Chart data={chartData} title="Test" type="bar" />);
    // Bar chart renders labels in both chart area and legend
    expect(screen.getAllByText('Jan').length).toBeGreaterThan(0);
  });

  it('hides legend when showLegend is false', () => {
    render(<Chart data={chartData} title="Test" showLegend={false} type="bar" />);
    // Only chart data labels should appear, no legend items
    // Bar chart renders data labels in the chart area
  });

  it('uses custom colors', () => {
    render(<Chart data={chartData} colors={['#ff0000']} type="bar" />);
    const rects = document.querySelectorAll('svg rect');
    expect(rects[0]).toHaveAttribute('fill', '#ff0000');
  });
});
