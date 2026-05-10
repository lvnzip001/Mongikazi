(function () {
  const root = document.documentElement;
  const storageKey = 'mk-theme';
  const toggles = document.querySelectorAll('[data-theme-toggle]');
  const progressBars = document.querySelectorAll('[data-progress-bar]');

  function preferredTheme() {
    const stored = localStorage.getItem(storageKey);
    if (stored === 'dark' || stored === 'light') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    root.classList.toggle('dark', isDark);
    toggles.forEach(function (toggle) {
      toggle.textContent = isDark ? '☀' : '◐';
      toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }

  applyTheme(preferredTheme());

  toggles.forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      const nextTheme = root.classList.contains('dark') ? 'light' : 'dark';
      localStorage.setItem(storageKey, nextTheme);
      applyTheme(nextTheme);
    });
  });

  progressBars.forEach(function (bar) {
    const value = Number(bar.getAttribute('data-progress-value') || 0);
    bar.style.width = Math.max(0, Math.min(100, value)) + '%';
  });
})();
