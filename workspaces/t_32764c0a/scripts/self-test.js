#!/usr/bin/env node
/**
 * ComponentCraft Self-Test
 * Verifies the library structure and key files
 */

const fs = require('fs');
const path = require('path');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed++;
    console.log(`  ✗ ${name}`);
    console.log(`    ${e.message}`);
  }
}

const srcDir = path.join(__dirname, '..', 'src');

console.log('\nComponentCraft Self-Test\n');

// File existence tests
const requiredFiles = [
  'index.ts',
  'theme/index.ts',
  'components/Button.tsx',
  'components/Input.tsx',
  'components/Modal.tsx',
  'components/Table.tsx',
  'components/Chart.tsx',
  'components/Form.tsx',
  'components/Navigation.tsx',
  'components/Button.test.tsx',
  'components/Input.test.tsx',
  'components/Modal.test.tsx',
  'components/Table.test.tsx',
  'components/Chart.test.tsx',
  'components/Form.test.tsx',
  'components/Navigation.test.tsx',
  'components/Button.stories.tsx',
  'components/Input.stories.tsx',
  'components/Modal.stories.tsx',
  'components/Table.stories.tsx',
  'components/Chart.stories.tsx',
  'components/Form.stories.tsx',
  'components/Navigation.stories.tsx',
];

requiredFiles.forEach(file => {
  test(`src/${file} exists`, () => {
    const filePath = path.join(srcDir, file);
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }
  });
});

// Content tests
test('Button component exports ButtonProps interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Button.tsx'), 'utf8');
  if (!content.includes('export interface ButtonProps')) {
    throw new Error('ButtonProps interface not found');
  }
});

test('Input component exports InputProps interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Input.tsx'), 'utf8');
  if (!content.includes('export interface InputProps')) {
    throw new Error('InputProps interface not found');
  }
});

test('Modal component exports ModalProps interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Modal.tsx'), 'utf8');
  if (!content.includes('export interface ModalProps')) {
    throw new Error('ModalProps interface not found');
  }
});

test('Table component exports Column interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Table.tsx'), 'utf8');
  if (!content.includes('export interface Column')) {
    throw new Error('Column interface not found');
  }
});

test('Chart component exports ChartProps interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Chart.tsx'), 'utf8');
  if (!content.includes('export interface ChartProps')) {
    throw new Error('ChartProps interface not found');
  }
});

test('Form component exports FormField interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Form.tsx'), 'utf8');
  if (!content.includes('export interface FormField')) {
    throw new Error('FormField interface not found');
  }
});

test('Navigation component exports NavItem interface', () => {
  const content = fs.readFileSync(path.join(srcDir, 'components/Navigation.tsx'), 'utf8');
  if (!content.includes('export interface NavItem')) {
    throw new Error('NavItem interface not found');
  }
});

test('Theme exports lightTheme and darkTheme', () => {
  const content = fs.readFileSync(path.join(srcDir, 'theme/index.ts'), 'utf8');
  if (!content.includes('export const lightTheme')) {
    throw new Error('lightTheme not exported');
  }
  if (!content.includes('export const darkTheme')) {
    throw new Error('darkTheme not exported');
  }
});

test('Index.ts re-exports all components', () => {
  const content = fs.readFileSync(path.join(srcDir, 'index.ts'), 'utf8');
  const exports = ['Button', 'Input', 'Modal', 'Table', 'Chart', 'Form', 'Navigation'];
  exports.forEach(exp => {
    if (!content.includes(`export { ${exp}`)) {
      throw new Error(`${exp} not re-exported from index.ts`);
    }
  });
});

test('All components have ARIA attributes', () => {
  const components = ['Button.tsx', 'Input.tsx', 'Modal.tsx', 'Table.tsx', 'Form.tsx', 'Navigation.tsx'];
  components.forEach(comp => {
    const content = fs.readFileSync(path.join(srcDir, 'components', comp), 'utf8');
    if (!content.includes('aria-') && !content.includes('role=')) {
      throw new Error(`${comp} missing ARIA attributes`);
    }
  });
});

test('All components support themeMode prop', () => {
  const components = ['Button.tsx', 'Input.tsx', 'Modal.tsx', 'Table.tsx', 'Chart.tsx', 'Form.tsx', 'Navigation.tsx'];
  components.forEach(comp => {
    const content = fs.readFileSync(path.join(srcDir, 'components', comp), 'utf8');
    if (!content.includes('themeMode')) {
      throw new Error(`${comp} missing themeMode prop`);
    }
  });
});

test('package.json has correct name', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));
  if (pkg.name !== '@itspremkumar/component-craft') {
    throw new Error(`Expected package name @itspremkumar/component-craft, got ${pkg.name}`);
  }
});

test('README exists and has content', () => {
  const readmePath = path.join(__dirname, '..', 'README.md');
  if (!fs.existsSync(readmePath)) {
    throw new Error('README.md not found');
  }
  const content = fs.readFileSync(readmePath, 'utf8');
  if (content.length < 1000) {
    throw new Error('README.md too short');
  }
});

console.log(`\nResults: ${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
