/* Worker portal: uses mk-theme.js for theme, more menu, progress bars */
(function () {
  function initFileUploads() {
    document.querySelectorAll("[data-file-upload]").forEach(function (wrap) {
      var input = wrap.querySelector(".mk-file-upload__input");
      var nameEl = wrap.querySelector("[data-file-name]");
      if (!input || !nameEl) {
        return;
      }
      input.addEventListener("change", function () {
        var file = input.files && input.files[0];
        if (file) {
          nameEl.textContent = file.name;
          wrap.classList.add("is-selected");
        } else {
          nameEl.textContent = nameEl.dataset.defaultLabel || "No file chosen";
          wrap.classList.remove("is-selected");
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (window.MkTheme) {
      window.MkTheme.initPortalMoreMenu();
      window.MkTheme.initProgressBars();
    }
    initFileUploads();
  });
})();
