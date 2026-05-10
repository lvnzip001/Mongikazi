document.addEventListener("DOMContentLoaded", function () {
  const openButton = document.querySelector("[data-mobile-menu-open]");
  const closeButtons = document.querySelectorAll("[data-mobile-menu-close]");
  const menu = document.querySelector("[data-mobile-menu]");
  const themeButtons = document.querySelectorAll("[data-theme-toggle]");
  const root = document.documentElement;

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("mongikazi-theme", theme);
    themeButtons.forEach((button) => {
      button.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
      button.textContent = theme === "dark" ? "☀" : "◐";
    });
  }

  const savedTheme = localStorage.getItem("mongikazi-theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  setTheme(savedTheme || (prefersDark ? "dark" : "light"));

  themeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  });

  if (!openButton || !menu) return;

  function openMenu() {
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    openButton.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeMenu() {
    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
    openButton.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  openButton.addEventListener("click", openMenu);
  closeButtons.forEach((button) => button.addEventListener("click", closeMenu));

  menu.addEventListener("click", function (event) {
    if (event.target === menu) closeMenu();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && menu.classList.contains("is-open")) closeMenu();
  });
});
