(function () {
  const DEBOUNCE_MS = 220;

  function debounce(fn, wait) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  function closeAll(except) {
    document.querySelectorAll("[data-locality-list]").forEach((list) => {
      if (list !== except) {
        list.hidden = true;
        list.classList.remove("is-open");
        list.innerHTML = "";
      }
    });
  }

  function typeClass(type) {
    if (type === "city") return "mk-locality-type--city";
    if (type === "town") return "mk-locality-type--town";
    return "mk-locality-type--suburb";
  }

  function initLocalityInput(input) {
    if (input.dataset.localityBound === "1") {
      return;
    }
    input.dataset.localityBound = "1";

    const hiddenId = input.getAttribute("data-locality-hidden-id");
    const hidden = hiddenId ? document.getElementById(hiddenId) : null;
    const url = input.getAttribute("data-locality-url") || "/locations/autocomplete/";
    const wrapper = input.closest("[data-locality-field]") || input.parentElement;

    const list = document.createElement("ul");
    list.className = "mk-locality-suggestions";
    list.setAttribute("data-locality-list", "");
    list.setAttribute("role", "listbox");
    list.id = `locality-list-${Math.random().toString(36).slice(2, 9)}`;
    list.hidden = true;
    input.setAttribute("aria-controls", list.id);
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    wrapper.appendChild(list);

    let activeIndex = -1;
    let currentResults = [];

    function setExpanded(open) {
      input.setAttribute("aria-expanded", open ? "true" : "false");
    }

    function clearActive() {
      activeIndex = -1;
      list.querySelectorAll(".mk-locality-suggestion").forEach((btn) => {
        btn.classList.remove("is-active");
        btn.setAttribute("aria-selected", "false");
      });
    }

    function highlightIndex(index) {
      const buttons = list.querySelectorAll(".mk-locality-suggestion");
      if (!buttons.length) return;
      clearActive();
      activeIndex = Math.max(0, Math.min(index, buttons.length - 1));
      const btn = buttons[activeIndex];
      btn.classList.add("is-active");
      btn.setAttribute("aria-selected", "true");
      btn.scrollIntoView({ block: "nearest" });
    }

    function selectItem(item) {
      input.value = item.label;
      if (hidden) {
        hidden.value = String(item.id);
      }
      list.hidden = true;
      list.classList.remove("is-open", "is-loading");
      list.innerHTML = "";
      setExpanded(false);
      clearActive();
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function renderEmpty(query) {
      list.innerHTML = "";
      const header = document.createElement("li");
      header.className = "mk-locality-suggestions__header";
      header.setAttribute("aria-hidden", "true");
      header.textContent = "No matches";
      list.appendChild(header);
      const empty = document.createElement("li");
      empty.className = "mk-locality-empty";
      empty.textContent = `We could not find “${query}”. Try another spelling or a nearby city.`;
      list.appendChild(empty);
      list.hidden = false;
      list.classList.add("is-open");
      list.classList.remove("is-loading");
      setExpanded(true);
    }

    function renderResults(results) {
      list.innerHTML = "";
      currentResults = results;
      activeIndex = -1;

      if (!results.length) {
        renderEmpty(input.value.trim());
        return;
      }

      const header = document.createElement("li");
      header.className = "mk-locality-suggestions__header";
      header.setAttribute("aria-hidden", "true");
      header.textContent =
        results.length === 1 ? "1 suggestion" : `${results.length} suggestions`;
      list.appendChild(header);

      results.forEach((item, index) => {
        const li = document.createElement("li");
        li.setAttribute("role", "presentation");

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "mk-locality-suggestion";
        btn.setAttribute("role", "option");
        btn.setAttribute("aria-selected", "false");
        btn.id = `${list.id}-opt-${index}`;

        const main = document.createElement("span");
        main.className = "mk-locality-suggestion__main";
        const title = document.createElement("span");
        title.className = "mk-locality-suggestion__title";
        title.textContent = item.name;
        main.appendChild(title);

        const meta = document.createElement("span");
        meta.className = "mk-locality-suggestion__meta";
        meta.textContent = item.subtitle || item.province || "";
        main.appendChild(meta);
        btn.appendChild(main);

        const badge = document.createElement("span");
        badge.className = `mk-locality-type ${typeClass(item.type)}`;
        badge.textContent = item.type_label || "Area";
        btn.appendChild(badge);

        btn.addEventListener("click", () => selectItem(item));
        btn.addEventListener("mouseenter", () => highlightIndex(index));
        li.appendChild(btn);
        list.appendChild(li);
      });

      list.hidden = false;
      list.classList.add("is-open");
      list.classList.remove("is-loading");
      setExpanded(true);
    }

    function showLoading() {
      list.innerHTML = "";
      const header = document.createElement("li");
      header.className = "mk-locality-suggestions__header";
      header.setAttribute("aria-hidden", "true");
      header.textContent = "Searching…";
      list.appendChild(header);
      const loading = document.createElement("li");
      loading.className = "mk-locality-loading";
      loading.innerHTML = '<span></span><span></span><span></span>';
      list.appendChild(loading);
      list.hidden = false;
      list.classList.add("is-open", "is-loading");
      setExpanded(true);
    }

    const fetchResults = debounce(function () {
      const q = input.value.trim();
      if (hidden && q.length < 2) {
        hidden.value = "";
      }
      if (q.length < 2) {
        list.hidden = true;
        list.classList.remove("is-open", "is-loading");
        list.innerHTML = "";
        setExpanded(false);
        return;
      }

      showLoading();
      const requestUrl = `${url}?q=${encodeURIComponent(q)}`;
      fetch(requestUrl, {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Autocomplete failed");
          }
          return response.json();
        })
        .then((data) => renderResults(data.results || []))
        .catch(() => {
          list.hidden = true;
          list.classList.remove("is-open", "is-loading");
          setExpanded(false);
        });
    }, DEBOUNCE_MS);

    input.addEventListener("input", fetchResults);
    input.addEventListener("focus", function () {
      closeAll(list);
      if (input.value.trim().length >= 2) {
        fetchResults();
      }
    });
    input.addEventListener("keydown", function (event) {
      const buttons = list.querySelectorAll(".mk-locality-suggestion");
      if (event.key === "Escape") {
        list.hidden = true;
        list.classList.remove("is-open");
        setExpanded(false);
        clearActive();
        return;
      }
      if (!buttons.length || list.hidden) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        highlightIndex(activeIndex + 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        highlightIndex(activeIndex <= 0 ? buttons.length - 1 : activeIndex - 1);
      } else if (event.key === "Enter" && activeIndex >= 0) {
        event.preventDefault();
        selectItem(currentResults[activeIndex]);
      }
    });
    input.addEventListener("blur", function () {
      setTimeout(() => {
        list.hidden = true;
        list.classList.remove("is-open");
        setExpanded(false);
        clearActive();
      }, 180);
    });
    document.addEventListener("click", function (event) {
      if (!wrapper.contains(event.target)) {
        list.hidden = true;
        list.classList.remove("is-open");
        setExpanded(false);
        clearActive();
      }
    });
  }

  function initAll() {
    document.querySelectorAll("[data-locality-autocomplete]").forEach(initLocalityInput);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();
