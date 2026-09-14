# Contributing to DevPortal

Thank you for your interest in contributing to DevPortal! This document outlines the guidelines for contributing.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in the issue tracker
2. Create a new issue with a clear title and description
3. Include steps to reproduce, expected behavior, and actual behavior
4. Add screenshots or code examples if applicable

### Submitting Changes

1. Fork the repository
2. Create a new branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass: `python tests/test_portal.py`
6. Commit with a descriptive message: `git commit -m "feat: add new feature"`
7. Push to your fork: `git push origin feature/my-feature`
8. Open a Pull Request

## Code Style

### Markdown
- Use ATX-style headings (`#` not `===`)
- Use fenced code blocks with language identifiers
- Maximum line length: 120 characters
- Use reference-style links for repeated URLs

### CSS
- Use CSS custom properties for theming
- Follow BEM naming convention for classes
- Mobile-first responsive design
- Test in both light and dark modes

### JavaScript
- Use ES6+ syntax
- Prefer `const` and `let` over `var`
- Use arrow functions for callbacks
- Comment complex logic

## Adding Documentation

1. Create a new `.md` file in the appropriate directory
2. Add a link in `_sidebar.md`
3. Include a clear title and table of contents
4. Use code examples with proper syntax highlighting
5. Test that all internal links resolve

## Adding API Versions

1. Create a new directory under `docs/api/` (e.g., `v3/`)
2. Add endpoints to `assets/js/api-spec.js`
3. Update `_sidebar.md` with new version links
4. Add OpenAPI paths to `openapi/spec.yaml`

## Pull Request Checklist

- [ ] Tests pass (`python tests/test_portal.py`)
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] No broken links
- [ ] Changes work in both light and dark modes
- [ ] Mobile-responsive (if UI changes)
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intent

## Questions?

Open an issue with the `question` label, or reach out to the maintainers.

## License

By contributing to DevPortal, you agree that your contributions will be licensed under the MIT License.
