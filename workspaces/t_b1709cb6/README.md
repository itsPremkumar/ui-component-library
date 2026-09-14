# DevPortal

**Modern Developer Portal with Interactive API Documentation**

DevPortal is a comprehensive, markdown-based developer portal built with [Docsify](https://docsify.js.org/). It provides beautiful documentation, interactive API testing, full-text search, versioned API references, and a customizable theme.

## Features

- **Markdown-based Documentation** - Write docs in Markdown, render beautifully
- **Interactive API Console** - Test endpoints directly from the browser
- **Full-text Search** - Instant search across all documentation
- **Versioned Documentation** - Support for multiple API versions (v1, v2)
- **Customizable Theme** - CSS variables for easy customization
- **Code Highlighting** - Syntax highlighting for 20+ languages
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Mode Support** - Toggle between light and dark themes
- **Copy Code Buttons** - One-click code copying
- **Pagination** - Navigate between pages seamlessly

## Quick Start

### Option 1: Open Directly

Simply open `index.html` in your browser. No build step required!

### Option 2: Serve Locally

Using Python:
```bash
python -m http.server 3000
```

Using Node.js:
```bash
npx serve .
```

Using Docsify CLI:
```bash
docsify serve .
```

Then open `http://localhost:3000` in your browser.

### Option 3: Deploy to GitHub Pages

1. Push this repository to GitHub
2. Go to Settings → Pages
3. Select `main` branch and `/ (root)` folder
4. Your portal is live at `https://itsPremkumar.github.io/developer-portal`

## Project Structure

```
├── index.html                 # Main entry point
├── README.md                  # Home page content
├── _sidebar.md                # Sidebar navigation
├── _navbar.md                 # Top navigation bar
├── _coverpage.md              # Cover page
├── docs/
│   ├── guides/
│   │   ├── quickstart.md      # Quick start guide
│   │   ├── installation.md    # Installation guide
│   │   ├── configuration.md   # Configuration guide
│   │   ├── authentication-flow.md
│   │   ├── rate-limiting.md
│   │   ├── error-handling.md
│   │   ├── pagination.md
│   │   ├── webhooks.md
│   │   ├── sdk-usage.md
│   │   └── api-console.md
│   └── api/
│       ├── README.md          # API overview
│       ├── v1/                # API v1 docs
│       │   ├── authentication.md
│       │   ├── users.md
│       │   └── resources.md
│       └── v2/                # API v2 docs
│           ├── authentication.md
│           ├── users.md
│           ├── resources.md
│           └── webhooks.md
├── assets/
│   ├── css/
│   │   └── theme.css          # Custom theme styles
│   └── js/
│       ├── api-spec.js        # API endpoint definitions
│       └── custom.js          # Custom JavaScript
├── openapi/
│   └── spec.yaml              # OpenAPI specification
├── scripts/
│   ├── serve.sh               # Development server
│   └── deploy.sh              # Deployment script
├── tests/
│   └── test_portal.py         # Test suite
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Customization

### Theme Customization

Edit `assets/css/theme.css` to customize colors, fonts, and layout:

```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --accent-color: #06b6d4;
  --text-color: #1f2937;
  --bg-color: #ffffff;
  --sidebar-bg: #f9fafb;
  --code-bg: #1e1e2e;
  --border-color: #e5e7eb;
  --font-family: 'Inter', -apple-system, sans-serif;
  --code-font: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Adding New Pages

1. Create a new `.md` file in the appropriate directory
2. Add a link to `_sidebar.md` for navigation
3. The page is automatically rendered by Docsify

### Adding API Versions

1. Create a new directory under `docs/api/` (e.g., `v3/`)
2. Add the version to `assets/js/api-spec.js`
3. Add sidebar entries in `_sidebar.md`

### Adding Code Languages

Add the corresponding Prism.js language component in `index.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-LANGUAGE.min.js"></script>
```

## Content Structure

### Writing Documentation

Docsify uses standard Markdown with some extensions:

```markdown
# Page Title

## Section Header

Regular paragraph text with **bold**, *italic*, and `code`.

```bash
# Code blocks with syntax highlighting
curl https://api.example.com/v2/users
```

> This is a blocktip. Docsify also supports:
> - :tip: Tips
> - :warning: Warnings
> - :danger: Danger alerts

[Link to another page](docs/guides/quickstart.md)
```

### Flexible Alerts

```
!> **Important** - This is an important note.

?> **Tip** - This is a helpful tip.

x> **Warning** - This is a warning message.

!> **Danger** - This is a critical alert.
```

### Badges

```
[!badge text="v2.0" variant="info"](https://example.com)
[!badge text="stable" variant="success"](https://example.com)
```

## Deployment

### Static Hosting

DevPortal is a static site — deploy it anywhere:

- **GitHub Pages** - Free, integrated with your repo
- **Netlify** - Continuous deployment with preview URLs
- **Vercel** - Edge network, instant global distribution
- **AWS S3 + CloudFront** - Scalable, production-grade hosting
- **Any web server** - Just serve the static files

### Docker

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
```

```bash
docker build -t devportal .
docker run -p 8080:80 devportal
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Tests validate:
- All markdown files parse correctly
- All internal links resolve
- Sidebar/navbar references are valid
- API spec is well-formed
- Theme CSS is valid

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
