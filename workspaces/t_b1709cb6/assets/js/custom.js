/**
 * DevPortal Custom JavaScript
 * Handles theme switching, dark mode, and UI enhancements
 */

(function () {
  'use strict';

  // Dark mode detection and toggle
  function initTheme() {
    const savedTheme = localStorage.getItem('devportal-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }

  // Toggle theme function
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('devportal-theme', next);
  }

  // Add theme toggle button
  function addThemeToggle() {
    const navbar = document.querySelector('.app-nav');
    if (!navbar) return;

    const toggle = document.createElement('button');
    toggle.className = 'theme-toggle';
    toggle.innerHTML = '<i class="fas fa-moon"></i>';
    toggle.title = 'Toggle dark mode';
    toggle.style.cssText = `
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1.2em;
      padding: 8px;
      color: inherit;
      opacity: 0.8;
      transition: opacity 0.2s;
    `;
    toggle.addEventListener('mouseenter', () => toggle.style.opacity = '1');
    toggle.addEventListener('mouseleave', () => toggle.style.opacity = '0.8');
    toggle.addEventListener('click', () => {
      toggleTheme();
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      toggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    navbar.appendChild(toggle);
  }

  // Smooth scroll for anchor links
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  // Add copy buttons to code blocks
  function enhanceCodeBlocks() {
    document.querySelectorAll('pre code').forEach(block => {
      const pre = block.parentElement;
      if (pre.querySelector('.copy-btn')) return;

      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-btn';
      copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
      copyBtn.title = 'Copy code';
      copyBtn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: #ccc;
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8em;
        opacity: 0;
        transition: opacity 0.2s;
      `;

      pre.style.position = 'relative';
      pre.addEventListener('mouseenter', () => copyBtn.style.opacity = '1');
      pre.addEventListener('mouseleave', () => copyBtn.style.opacity = '0');

      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(block.textContent);
          copyBtn.innerHTML = '<i class="fas fa-check"></i>';
          setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i>', 2000);
        } catch (err) {
          console.error('Failed to copy:', err);
        }
      });

      pre.appendChild(copyBtn);
    });
  }

  // Keyboard shortcuts
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search input');
        if (searchInput) searchInput.focus();
      }

      // Ctrl/Cmd + D: Toggle dark mode
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
      }

      // Escape: Close search
      if (e.key === 'Escape') {
        const searchInput = document.querySelector('.search input');
        if (searchInput && document.activeElement === searchInput) {
          searchInput.blur();
        }
      }
    });
  }

  // Reading progress indicator
  function initReadingProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: var(--primary-color);
      z-index: 9999;
      transition: width 0.1s;
      width: 0%;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = progress + '%';
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initTheme();
    
    // Wait for Docsify to render
    const observer = new MutationObserver((mutations, obs) => {
      const app = document.querySelector('#app');
      if (app && app.querySelector('.markdown-section')) {
        obs.disconnect();
        addThemeToggle();
        enhanceCodeBlocks();
        initSmoothScroll();
        initKeyboardShortcuts();
        initReadingProgress();
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Expose toggle function globally
  window.toggleTheme = toggleTheme;
})();
