(function () {
  const key = "mk-theme";
  const root = document.documentElement;

  function getStoredTheme() {
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function setStoredTheme(value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      // Storage may be blocked. Theme still toggles for the current page session.
    }
  }

  function prefersDarkMode() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function applyInitialTheme() {
    const saved = getStoredTheme();
    if (saved === "dark" || (!saved && prefersDarkMode())) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }

  function updateThemeToggle() {
    const isDark = root.classList.contains("dark");
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.textContent = isDark ? "\u263C" : "\u25D0";
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute("title", isDark ? "Switch to light mode" : "Switch to dark mode");
    });
  }

  function toggleTheme() {
    const isDark = root.classList.toggle("dark");
    setStoredTheme(isDark ? "dark" : "light");
    updateThemeToggle();
  }

  applyInitialTheme();

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", toggleTheme);
  });

  document.querySelectorAll(".mk-progress-bar").forEach((bar) => {
    const width = bar.style.width || "0%";
    bar.style.width = "0%";
    window.requestAnimationFrame(() => {
      bar.style.width = width;
    });
  });

  updateThemeToggle();
})();

