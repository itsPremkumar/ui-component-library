# Installation Guide

Complete installation instructions for DevPortal.

## System Requirements

- **Browser**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Node.js**: 14+ (for development server, optional)
- **Python**: 3.7+ (for test suite and simple server)
- **Disk Space**: ~5 MB (static files only)

## Method 1: Direct Download

1. Download the latest release from GitHub Releases
2. Extract the ZIP file
3. Open `index.html` in your browser

No build tools, no dependencies, no configuration needed.

## Method 2: Git Clone

```bash
git clone https://github.com/itsPremkumar/developer-portal.git
cd developer-portal
```

## Method 3: npm Package

```bash
npm install @itsPremkumar/devportal
```

Then copy `node_modules/@itsPremkumar/devportal/dist/` to your web root.

## Development Setup

### Install Docsify CLI (optional)

```bash
npm install -g docsify-cli
```

### Start Development Server

```bash
# Using Docsify CLI (recommended)
docsify serve . --port 3000

# Using Python
python -m http.server 3000

# Using Node.js
npx serve .
```

The server starts at `http://localhost:3000` with live reload.

### Project Structure After Setup

```
developer-portal/
├── index.html          # Entry point
├── _sidebar.md         # Navigation
├── _coverpage.md       # Landing page
├── docs/               # Documentation content
├── assets/             # CSS and JS
├── openapi/            # API specifications
├── scripts/            # Utility scripts
└── tests/              # Test suite
```

## Production Deployment

### Docker

```bash
docker pull itspremkumar/devportal:latest
docker run -d -p 8080:80 --name devportal itspremkumar/devportal
```

### Nginx

```nginx
server {
    listen 80;
    server_name docs.example.com;
    root /var/www/devportal;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Apache

```apache
<VirtualHost *:80>
    ServerName docs.example.com
    DocumentRoot /var/www/devportal
    
    <Directory /var/www/devportal>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

## Verification

After installation, verify everything works:

1. Open the portal in your browser
2. Check the cover page renders correctly
3. Navigate through sidebar links
4. Test the search functionality
5. Open the API Console and try an endpoint

## Troubleshooting

### Blank Page
- Make sure you're serving over HTTP (not `file://`)
- Check browser console for errors
- Verify `index.html` is in the root directory

### Search Not Working
- Search requires HTTP(S) protocol
- Ensure `search.min.js` plugin is loaded
- Check that markdown files are accessible

### Sidebar Not Showing
- Verify `_sidebar.md` exists in root
- Check for syntax errors in sidebar markdown
- Ensure `loadSidebar: true` is set in Docsify config
