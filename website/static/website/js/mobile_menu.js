/* Public site: theme + mobile menu (uses mk-theme.js) */
(function () {
  if (window.MkTheme) {
    return;
  }
  document.addEventListener("DOMContentLoaded", function () {
    if (window.MkTheme) {
      window.MkTheme.initAll();
    }
  });
})();
