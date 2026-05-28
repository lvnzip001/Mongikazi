(function () {
  const key = "mk-theme";
  const root = document.documentElement;

  function safeStorageGet(name) {
    try { return localStorage.getItem(name); } catch (error) { return null; }
  }

  function safeStorageSet(name, value) {
    try { localStorage.setItem(name, value); } catch (error) { /* ignore unavailable storage */ }
  }

  function applyTheme(theme) {
    const dark = theme === "dark";
    root.classList.toggle("dark", dark);
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.textContent = dark ? "¤" : "?";
      btn.setAttribute("aria-pressed", String(dark));
      btn.setAttribute("title", dark ? "Switch to light mode" : "Switch to dark mode");
    });
  }

  function currentTheme() {
    const stored = safeStorageGet(key);
    if (stored === "dark" || stored === "light") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  applyTheme(currentTheme());

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = root.classList.contains("dark") ? "light" : "dark";
      safeStorageSet(key, next);
      applyTheme(next);
    });
  });
})();

