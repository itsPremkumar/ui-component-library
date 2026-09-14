# Changelog

All notable changes to the DevPortal project will be documented in this file.

## [2.0.0] - 2024-09-14

### Added
- Interactive API console for testing endpoints directly in the browser
- Versioned API documentation (v1 legacy + v2 latest)
- Full-text search across all documentation
- Dark mode support with system preference detection
- Customizable theme via CSS variables
- OpenAPI 3.0 specification
- Comprehensive test suite
- Deployment scripts for multiple platforms (GitHub Pages, Netcelery, Vercel, Docker, Nginx)
- Webhook management documentation
- Rate limiting guide with code examples
- Error handling documentation with typed error responses
- Pagination guide with cursor-based and offset-based examples
- SDK usage guide for JavaScript, Python, and Go
- Authentication flow documentation (API keys + OAuth 2.0)
- Keyboard shortcuts (Ctrl+K for search, Ctrl+D for dark mode)
- Reading progress indicator
- Copy code buttons on hover

### API v2
- Bearer token authentication (replaces v1 X-API-Key header)
- Improved pagination with cursor-based navigation
- Webhooks API for real-time event notifications
- Enhanced user management with roles and preferences
- Resource metadata support
- Idempotency key support for safe retries

### Documentation
- Quick start guide
- Installation guide for all platforms
- Configuration guide with theme customization
- Authentication flow guide
- Rate limiting guide
- Error handling guide
- Pagination guide
- Webhooks guide
- SDK usage guide

### Technical
- Built with Docsify 4.x
- Prism.js syntax highlighting for 25+ languages
- Vue.js 2.x for interactive components
- Font Awesome 6.x icons
- Fully static - no build step required

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Basic documentation structure
- API v1 reference
- Simple sidebar navigation
