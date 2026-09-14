# ComponentCraft

A modern, accessible, and themeable React component library with Storybook documentation.

## Features

- **7 Components**: Button, Input, Modal, Table, Chart, Form, Navigation
- **Dark/Light Theme Support** with CSS custom properties
- **Accessibility (a11y)** compliant with ARIA attributes
- **TypeScript** with full type definitions
- **Storybook** documentation with interactive examples
- **Jest + React Testing Library** unit tests
- **Tree-shakeable** ESM + CJS builds

## Installation

```bash
npm install @itspremkumar/component-craft
```

## Quick Start

```tsx
import React from 'react';
import { Button, Input, Modal, Table, Chart, Form, Navigation } from '@itspremkumar/component-craft';

function App() {
  return (
    <div>
      <Button variant="solid" colorScheme="primary">Click Me</Button>
      <Input label="Email" placeholder="you@example.com" type="email" />
    </div>
  );
}
```

## Components

### Button

```tsx
<Button variant="solid" size="md" colorScheme="primary" isLoading={false}>
  Click Me
</Button>
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'solid' \| 'outline' \| 'ghost' \| 'link'` | `'solid'` | Button style variant |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| colorScheme | `'primary' \| 'secondary' \| 'danger' \| 'success'` | `'primary'` | Color scheme |
| fullWidth | `boolean` | `false` | Full width button |
| isLoading | `boolean` | `false` | Loading state with spinner |
| leftIcon | `ReactNode` | - | Left icon element |
| rightIcon | `ReactNode` | - | Right icon element |

### Input

```tsx
<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  helperText="We'll never share your email"
  error="Invalid email"
  required
/>
```

### Modal

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm"
  size="md"
  footer={<Button>Save</Button>}
>
  <p>Modal content goes here</p>
</Modal>
```

### Table

```tsx
const columns = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'email', header: 'Email' },
  { key: 'status', header: 'Status', render: (v) => <Badge>{v}</Badge> },
];

<Table
  columns={columns}
  data={users}
  sortable
  paginated
  pageSize={10}
  selectable
  getRowKey={(row) => row.id}
/>
```

### Chart

```tsx
<Chart
  type="bar"
  title="Monthly Sales"
  data={[
    { label: 'Jan', value: 6500 },
    { label: 'Feb', value: 5900 },
    { label: 'Mar', value: 8000 },
  ]}
  formatValue={(v) => `$${v}`}
/>
```

Supports `bar`, `line`, `pie`, and `area` chart types.

### Form

```tsx
<Form
  fields={[
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'password', label: 'Password', type: 'password', required: true },
    { name: 'role', label: 'Role', type: 'select', options: [{ label: 'Admin', value: 'admin' }] },
    { name: 'agree', label: 'I agree', type: 'checkbox' },
  ]}
  onSubmit={(values) => console.log(values)}
  submitText="Sign Up"
  showReset
  twoColumns
/>
```

### Navigation

```tsx
<Navigation
  variant="horizontal"
  brand="MyApp"
  items={[
    { label: 'Home', active: true, onClick: () => {} },
    { label: 'About', onClick: () => {} },
    { label: 'Services', children: [
      { label: 'Web', onClick: () => {} },
      { label: 'Mobile', onClick: () => {} },
    ]},
  ]}
/>
```

Supports `horizontal`, `vertical`, and `sidebar` variants with collapsible sidebar mode.

## Theme System

The library includes a comprehensive theme system with light and dark modes:

```tsx
import { lightTheme, darkTheme, getTheme } from '@itspremkumar/component-craft';

// Access theme values
const theme = getTheme('dark');
console.log(theme.colors.primary); // '#3b82f6'
```

Pass `themeMode` prop to any component:

```tsx
<Button themeMode="dark">Dark Button</Button>
<Input themeMode="dark" label="Name" />
```

## Storybook

View the full component documentation:

```bash
npm run storybook
```

Build static Storybook:

```bash
npm run build-storybook
```

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run Storybook
npm run storybook

# Build library
npm run build
```

## Accessibility

All components follow WAI-ARIA guidelines:
- Proper ARIA roles and attributes
- Keyboard navigation support
- Focus management in modals
- Screen reader friendly labels
- Color contrast compliance

## License

MIT
