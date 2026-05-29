/* Worker portal: uses mk-theme.js for theme, more menu, progress bars */
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    if (window.MkTheme) {
      window.MkTheme.initPortalMoreMenu();
      window.MkTheme.initProgressBars();
    }
  });
})();
