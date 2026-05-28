(function () {
  const key = "mk-theme";
  const root = document.documentElement;
  const saved = localStorage.getItem(key);
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (saved === "dark" || (!saved && prefersDark)) {
    root.classList.add("dark");
  } else if (saved === "light") {
    root.classList.remove("dark");
  }

  function refreshToggleState() {
    const isDark = root.classList.contains("dark");
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      button.textContent = isDark ? "¤" : "?";
    });
  }

  function toggleTheme() {
    const isDark = root.classList.toggle("dark");
    localStorage.setItem(key, isDark ? "dark" : "light");
    refreshToggleState();
  }

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", toggleTheme);
  });

  document.querySelectorAll(".mk-progress-bar").forEach((bar) => {
    const width = bar.style.width;
    bar.style.width = "0%";
    window.requestAnimationFrame(() => {
      bar.style.width = width || "0%";
    });
  });

  refreshToggleState();
})();

