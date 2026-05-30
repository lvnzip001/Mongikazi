/* Bookings uses mk-theme.js */
(function () {
  function initBookingCreateForm() {
    var requestType = document.getElementById("id_request_type");
    var workerStep = document.querySelector("[data-booking-worker-step]");
    if (!requestType || !workerStep) {
      return;
    }

    var workerSelect = workerStep.querySelector("select[name='worker']");
    var workerHint = workerStep.querySelector("[data-worker-hint]");
    var marketplaceValue = "OPEN_MARKETPLACE";

    function syncWorkerStep() {
      var isMarketplace = requestType.value === marketplaceValue;
      workerStep.classList.toggle("is-disabled", isMarketplace);
      if (workerSelect) {
        workerSelect.disabled = isMarketplace;
        if (isMarketplace) {
          workerSelect.value = "";
        }
      }
      if (workerHint) {
        workerHint.textContent = isMarketplace
          ? "Not used for open marketplace jobs — helpers will apply instead."
          : "Required for direct requests. Disabled when posting an open marketplace job.";
      }
    }

    requestType.addEventListener("change", syncWorkerStep);
    syncWorkerStep();
  }

  document.addEventListener("DOMContentLoaded", initBookingCreateForm);
})();
