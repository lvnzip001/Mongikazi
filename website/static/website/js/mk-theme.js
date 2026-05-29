(function (global) {
  const STORAGE_KEY = "mk-theme";

  function getPreferredTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch (error) {
      // Ignore.
    }
    if (global.matchMedia && global.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  function applyTheme(theme) {
    const safeTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", safeTheme);
    document.documentElement.classList.remove("dark");
    if (safeTheme === "dark") {
      document.documentElement.classList.add("dark");
    }

    document.querySelectorAll("[data-theme-icon]").forEach((icon) => {
      icon.textContent = safeTheme === "dark" ? "\u263C" : "\u25D0";
    });

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const isDark = safeTheme === "dark";
      if (button.textContent && !button.querySelector("[data-theme-icon]")) {
        button.textContent = isDark ? "\u263C" : "\u25D0";
      }
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      button.setAttribute(
        "aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode"
      );
      button.setAttribute("title", isDark ? "Switch to light mode" : "Switch to dark mode");
    });
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || getPreferredTheme();
    const next = current === "dark" ? "light" : "dark";
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (error) {
      // Ignore.
    }
    applyTheme(next);
  }

  function initThemeToggles() {
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      if (button.dataset.mkThemeBound === "1") {
        return;
      }
      button.dataset.mkThemeBound = "1";
      button.addEventListener("click", toggleTheme);
    });
  }

  function initMobileMenu() {
    const openButton = document.querySelector("[data-mobile-menu-open]");
    const menu = document.querySelector("[data-mobile-menu]");
    const closeButtons = document.querySelectorAll("[data-mobile-menu-close]");
    if (!openButton || !menu) {
      return;
    }

    function lockBody(lock) {
      document.body.style.overflow = lock ? "hidden" : "";
    }

    function openMenu() {
      menu.classList.add("is-open");
      menu.setAttribute("aria-hidden", "false");
      openButton.setAttribute("aria-expanded", "true");
      lockBody(true);
    }

    function closeMenu() {
      menu.classList.remove("is-open");
      menu.setAttribute("aria-hidden", "true");
      openButton.setAttribute("aria-expanded", "false");
      lockBody(false);
    }

    openButton.addEventListener("click", openMenu);
    closeButtons.forEach((button) => button.addEventListener("click", closeMenu));
    menu.addEventListener("click", function (event) {
      if (event.target === menu) {
        closeMenu();
      }
    });
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && menu.classList.contains("is-open")) {
        closeMenu();
      }
    });
  }

  function initPortalMoreMenu() {
    const openButton = document.querySelector("[data-worker-more-open], [data-portal-more-open]");
    const menu = document.querySelector("[data-worker-more-menu], [data-portal-more-menu]");
    const closeButtons = document.querySelectorAll("[data-worker-more-close], [data-portal-more-close]");
    if (!openButton || !menu) {
      return;
    }

    function lockBody(lock) {
      document.body.style.overflow = lock ? "hidden" : "";
    }

    function openMenu() {
      menu.removeAttribute("hidden");
      menu.classList.add("is-open");
      menu.setAttribute("aria-hidden", "false");
      openButton.setAttribute("aria-expanded", "true");
      lockBody(true);
    }

    function closeMenu() {
      menu.classList.remove("is-open");
      menu.setAttribute("aria-hidden", "true");
      menu.setAttribute("hidden", "");
      openButton.setAttribute("aria-expanded", "false");
      lockBody(false);
    }

    openButton.addEventListener("click", openMenu);
    closeButtons.forEach((button) => button.addEventListener("click", closeMenu));
    menu.addEventListener("click", function (event) {
      if (event.target === menu) {
        closeMenu();
      }
    });
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && menu.classList.contains("is-open")) {
        closeMenu();
      }
    });
  }

  function initProgressBars() {
    const reducedMotion = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.querySelectorAll(".mk-progress-bar").forEach((bar) => {
      if (reducedMotion) {
        return;
      }
      const width = bar.style.width || "0%";
      bar.style.width = "0%";
      global.requestAnimationFrame(() => {
        bar.style.width = width;
      });
    });
  }

  function initAll() {
    applyTheme(getPreferredTheme());
    initThemeToggles();
    initMobileMenu();
    initPortalMoreMenu();
    initProgressBars();
  }

  global.MkTheme = {
    STORAGE_KEY,
    getPreferredTheme,
    applyTheme,
    toggleTheme,
    initAll,
    initThemeToggles,
    initMobileMenu,
    initPortalMoreMenu,
    initProgressBars,
  };

  document.addEventListener("DOMContentLoaded", initAll);
})(window);
