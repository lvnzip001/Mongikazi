(function () {
  const STORAGE_KEY = "mk-theme";

  function getPreferredTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch (error) {
      // Ignore localStorage errors and continue with system preference.
    }

    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }

    return "light";
  }

  function applyTheme(theme) {
    const safeTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", safeTheme);

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
    const current = document.documentElement.getAttribute("data-theme") || getPreferredTheme();
    const next = current === "dark" ? "light" : "dark";

    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (error) {
      // Ignore localStorage errors.
    }

    applyTheme(next);
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

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getPreferredTheme());

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", toggleTheme);
    });

    initMobileMenu();
  });
})();
