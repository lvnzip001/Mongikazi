(function () {
  const root = document.documentElement;
  const key = 'mk-theme';
  const toggles = document.querySelectorAll('[data-theme-toggle]');

  function getStoredTheme() {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(key, theme);
    } catch (error) {
      // Ignore storage errors in restricted browser contexts.
    }
  }

  function preferredTheme() {
    const stored = getStoredTheme();
    if (stored === 'dark' || stored === 'light') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    const isDark = theme === 'dark';
    root.classList.toggle('dark', isDark);
    root.setAttribute('data-theme', theme);

    toggles.forEach(function (toggle) {
      toggle.textContent = isDark ? '☀' : '◐';
      toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      toggle.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }

  setTheme(preferredTheme());

  toggles.forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      const next = root.classList.contains('dark') ? 'light' : 'dark';
      saveTheme(next);
      setTheme(next);
    });
  });
})();
