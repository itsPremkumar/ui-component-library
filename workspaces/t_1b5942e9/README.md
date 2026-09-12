# Frontend Test Results Visualizer

An interactive dashboard for automated test results built with SvelteKit, TypeScript, Tailwind CSS, and Chart.js.

## Features

- **Multi-format Support**: Parse JUnit XML and JSON test reports (Jest, Mocha, custom formats)
- **Interactive Dashboard**: Summary cards, suite breakdown charts, duration histograms
- **Test Explorer**: Sortable, paginated table with filtering by suite, status, and duration
- **Report Comparison**: Side-by-side comparison of two test reports
- **Export**: Download filtered results as JSON or CSV
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Sample Data**: Built-in demo mode with generated test data

## Tech Stack

- **Framework**: SvelteKit + TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **Testing**: Vitest + Playwright

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run unit tests
npm run test:unit

# Run e2e tests
npm run test:e2e
```

## Project Structure

```
src/
├── lib/
│   ├── components/     # Reusable Svelte components
│   ├── parsers.ts      # XML/JSON test report parsers
│   ├── sampleData.ts   # Sample data generator
│   ├── stores.ts       # Svelte stores for state management
│   └── types.ts        # TypeScript type definitions
├── routes/
│   ├── +layout.svelte  # App layout with sidebar
│   ├── dashboard/      # Main dashboard view
│   ├── tests/          # Test cases table view
│   ├── compare/        # Report comparison view
│   └── upload/         # File upload view
└── app.css             # Global styles with Tailwind
```

## Supported Test Formats

### JUnit XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test Suite" tests="2" failures="1">
  <testsuite name="Suite" tests="2" failures="1">
    <testcase name="passes" classname="Suite" time="0.001" />
    <testcase name="fails" classname="Suite" time="0.002">
      <failure message="Error" type="AssertionError">Details</failure>
    </testcase>
  </testsuite>
</testsuites>
```

### JSON (Jest/Mocha/Custom)
```json
[
  { "name": "test1", "suite": "Suite A", "status": "passed", "duration": 100 },
  { "name": "test2", "suite": "Suite A", "status": "failed", "duration": 200 }
]
```

## License

MIT
