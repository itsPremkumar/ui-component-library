# Configuration Guide

Learn how to customize and configure DevPortal.

## Docsify Configuration

All Docsify settings are in `index.html` inside `window.$docsify`:

```javascript
window.$docsify = {
  name: 'DevPortal',
  repo: 'itsPremkumar/developer-portal',
  loadSidebar: true,
  loadNavbar: true,
  subMaxLevel: 3,
  auto2top: true,
  coverpage: true,
  onlyCover: false,
  search: { maxAge: 86400000, paths: 'auto' },
  tabs: { persist: true, sync: true, theme: 'classic' },
  copyCode: { buttonText: 'Copy', successText: 'Copied!' },
  pagination: { previousText: 'Previous', nextText: 'Next', crossChapter: true }
};
```

## Theme Configuration

Edit CSS variables in `assets/css/theme.css`:

```css
:root {
  /* Primary colors */
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --accent-color: #06b6d4;
  
  /* Text colors */
  --text-color: #1f2937;
  --text-muted: #6b7280;
  --heading-color: #111827;
  
  /* Background colors */
  --bg-color: #ffffff;
  --sidebar-bg: #f9fafb;
  --code-bg: #1e1e2e;
  
  /* UI elements */
  --border-color: #e5e7eb;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  
  /* Typography */
  --font-family: 'Inter', -apple-system, sans-serif;
  --code-font: 'JetBrains Mono', 'Fira Code', monospace;
  --base-font-size: 16px;
  --line-height: 1.7;
  
  /* Sidebar */
  --sidebar-width: 300px;
}
```

## Search Configuration

```javascript
search: {
  maxAge: 86400000,      // Cache duration (24h)
  paths: 'auto',         // Auto-index all pages
  placeholder: 'Search...',
  noData: 'No results',
  depth: 6,              // Heading depth to index
  hideOtherSidebarContent: true
}
```

## Sidebar Configuration

Create `_sidebar.md`:

```markdown
* **Section Title**
  * [Page Name](path/to/page.md)
  * [Another Page](path/another.md)

* **Nested Section**
  * [Nested Page](nested/page.md)
```

## Navbar Configuration

Create `_navbar.md`:

```markdown
* [Home](/)
* [Guides](guides/)
* [API](api/)
* [:external-link-alt: External](https://example.com)
```

## Coverpage Configuration

Create `_coverpage.md` for a landing page:

```markdown
# DevPortal
> Your tagline here

[Get Started](#main)
[GitHub](https://github.com/example)
```

## Plugin Configuration

### Docsify Tabs

```javascript
tabs: {
  persist: true,     // Remember active tab
  sync: true,        // Sync tabs across pages
  theme: 'classic',  // classic | material
  tabComments: true,
  tabHeadings: true
}
```

### Pagination

```javascript
pagination: {
  previousText: 'Previous',
  nextText: 'Next',
  crossChapter: true,
  crossChapterText: true
}
```

### Flexible Alerts

```javascript
flexibleAlerts: true
```

## Dark Mode

Dark mode is automatic based on system preference. Customize in CSS:

```css
[data-theme="dark"] {
  --text-color: #e5e7eb;
  --heading-color: #f9fafb;
  --bg-color: #111827;
  --sidebar-bg: #1f2937;
  --border-color: #374151;
  --code-bg: #0d1117;
}
```

## Environment Variables

For Docker deployments, you can set:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCSIFY_THEME` | `vue` | Base Docsify theme |
| `DOCSIFY_NAME` | `DevPortal` | Site name |
| `DOCSIFY_REPO` | `` | GitHub repo URL |
| `DOCSIFY_SEARCH` | `true` | Enable search |
