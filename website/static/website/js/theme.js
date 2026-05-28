(function () {
  const STORAGE_KEY = "mk-theme";

  function getPreferredTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch (error) {
      // Ignore localStorage access failures.
    }

    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }

    return "light";
  }

  function applyTheme(theme) {
    const safeTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.classList.toggle("dark", safeTheme === "dark");

    document.querySelectorAll("[data-theme-icon]").forEach((icon) => {
      icon.textContent = safeTheme === "dark" ? "\u263C" : "\u25D0";
    });

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.setAttribute(
        "aria-label",
        safeTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      );
    });
  }

  function toggleTheme() {
    const current = document.documentElement.classList.contains("dark") ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";

    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (error) {
      // Ignore localStorage access failures.
    }

    applyTheme(next);
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getPreferredTheme());

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", toggleTheme);
    });
  });
})();
