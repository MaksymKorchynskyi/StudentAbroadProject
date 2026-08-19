export function initCustomSelects(options = {}) {
  try {
    // --- Hero scroll indicator ---
    const scrollIndicator = document.querySelector(".scroll-indicator");
    if (scrollIndicator) {
      scrollIndicator.addEventListener("click", (e) => {
        e.preventDefault();
        const aboutSection = document.querySelector("#about-us-section");
        if (aboutSection) {
          aboutSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    }

    // --- Smooth anchor scroll ---
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (ev) => {
        const href = anchor.getAttribute("href")?.trim();
        ev.preventDefault();
        if (!href || href === "#") {
          window.scrollTo({ top: 0, behavior: "smooth" });
          return;
        }
        const target = document.querySelector(href);
        if (target)
          target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    // --- Button touch effects ---
    document.querySelectorAll(".btn").forEach((btn) => {
      btn.addEventListener("touchstart", () => btn.classList.add("hover"), {
        passive: true,
      });
      btn.addEventListener("touchend", () => btn.classList.remove("hover"), {
        passive: true,
      });
    });
  } catch (err) {
    console.error("initCustomSelects (top) error:", err);
  }

  // --- Custom selects logic ---
  try {
    const wrappers = Array.from(
      document.querySelectorAll(".custom-select-wrapper")
    );

    const debounce = (fn, wait = 150) => {
      let t;
      return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn(...args), wait);
      };
    };

    const getOptions = (dropdown) =>
      Array.from(dropdown.querySelectorAll(".custom-select-option"));

    const positionDropdown = (wrapper, input, dropdown) => {
      if (getComputedStyle(wrapper).position === "static")
        wrapper.style.position = "relative";
      dropdown.style.position = "absolute";
      dropdown.style.top = `${input.offsetHeight + 8}px`;
      dropdown.style.left = `0px`;
      dropdown.style.zIndex = 200;
    };

    const positionNewForm = (wrapper, input, form) => {
      const parentRect = wrapper.getBoundingClientRect();
      const width = form.offsetWidth || 320;
      form.style.position = "absolute";
      form.style.left = `${Math.round((parentRect.width - width) / 2)}px`;
      form.style.top = `${input.offsetHeight + 8}px`;
      form.style.transform = "none";
      form.style.zIndex = 150;
    };

    // --- New helper: close all other wrappers except the current one ---
    const closeOthers = (current) => {
      wrappers.forEach((w) => {
        if (w === current) return;
        w.classList.remove("active");
        const dd = w.querySelector(".custom-select-dropdown");
        if (dd) dd.classList.remove("active");
        const nf =
          w.querySelector(".new-item-form") ||
          w
            .closest(".form-field-and-description")
            ?.querySelector(".new-item-form");
        if (nf) nf.classList.remove("active");
        const si = w.querySelector(".custom-select-search-input");
        if (si) si.value = "";
        w.querySelectorAll(".custom-select-option").forEach(
          (o) => (o.style.display = "block")
        );
        const mi = w.querySelector(".custom-select-input");
        if (mi) mi.setAttribute("aria-expanded", "false");
      });
    };

    // --- Закриття всіх дропдаунів при кліку поза ---
    document.addEventListener("click", (e) => {
      const clickedInsideWrapper = !!e.target.closest(".custom-select-wrapper");
      const clickedInsideNewForm = !!e.target.closest(".new-item-form");

      if (!clickedInsideWrapper && !clickedInsideNewForm) {
        wrappers.forEach((wrapper) => {
          wrapper.classList.remove("active");
          const dd = wrapper.querySelector(".custom-select-dropdown");
          if (dd) dd.classList.remove("active");
          const nf =
            wrapper.querySelector(".new-item-form") ||
            wrapper
              .closest(".form-field-and-description")
              ?.querySelector(".new-item-form");
          if (nf) nf.classList.remove("active");
          const si = wrapper.querySelector(".custom-select-search-input");
          if (si) si.value = "";
          wrapper
            .querySelectorAll(".custom-select-option")
            .forEach((o) => (o.style.display = "block"));
          const mainInput = wrapper.querySelector(".custom-select-input");
          if (mainInput) mainInput.setAttribute("aria-expanded", "false");
        });
      }
    });

    window.addEventListener("resize", () => {
      wrappers.forEach((wrapper) => {
        const dd = wrapper.querySelector(".custom-select-dropdown");
        const mainInput = wrapper.querySelector(".custom-select-input");
        const nf =
          wrapper.querySelector(".new-item-form") ||
          wrapper
            .closest(".form-field-and-description")
            ?.querySelector(".new-item-form");
        if (dd && dd.classList.contains("active") && mainInput)
          positionDropdown(wrapper, mainInput, dd);
        if (nf && nf.classList.contains("active") && mainInput)
          positionNewForm(wrapper, mainInput, nf);
      });
    });

    wrappers.forEach((wrapper) => {
      const mainInput = wrapper.querySelector(".custom-select-input");
      const dropdown = wrapper.querySelector(".custom-select-dropdown");
      const arrow = wrapper.querySelector(".select-arrow");
      const row = wrapper.closest(".form-field-and-description");
      const addButton =
        wrapper.querySelector(
          ".custom-select-add-button, .form-section__add-button"
        ) ||
        row?.querySelector(
          ".custom-select-add-button, .form-section__add-button"
        ) ||
        null;
      const newForm =
        wrapper.querySelector(".new-item-form") ||
        row?.querySelector(".new-item-form") ||
        null;
      const newFormInput = newForm?.querySelector("input, textarea") || null;

      if (!mainInput || !dropdown) return;

      // --- Створення поля пошуку в дропдауні, якщо його немає ---
      let searchInput = dropdown.querySelector(".custom-select-search-input");
      if (!searchInput) {
        const searchDiv = document.createElement("div");
        searchDiv.className = "custom-select-search";
        searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.placeholder = "Пошук...";
        searchInput.className = "custom-select-search-input";
        const searchIcon = document.createElement("img");
        searchIcon.src = "./project/img/search.svg";
        searchIcon.alt = "Search";
        searchIcon.className = "custom-select-search-icon";
        searchDiv.appendChild(searchInput);
        searchDiv.appendChild(searchIcon);
        dropdown.prepend(searchDiv);
      }

      mainInput.setAttribute("role", "combobox");
      mainInput.setAttribute("aria-haspopup", "listbox");
      mainInput.setAttribute("aria-expanded", "false");
      dropdown.setAttribute("role", "listbox");

      getOptions(dropdown).forEach((opt, i) => {
        opt.setAttribute("role", "option");
        opt.dataset.index = i;
      });

      const filterOptions = (term = "") => {
        // закриваємо інші перед відкриттям поточного
        closeOthers(wrapper);

        const t = term.toLowerCase();
        getOptions(dropdown).forEach((o) => {
          o.style.display = o.textContent.toLowerCase().includes(t)
            ? "block"
            : "none";
        });
        dropdown.classList.add("active");
        wrapper.classList.add("active");
        mainInput.setAttribute("aria-expanded", "true");
        positionDropdown(wrapper, mainInput, dropdown);
      };

      const closeDropdown = () => {
        dropdown.classList.remove("active");
        wrapper.classList.remove("active");
        if (searchInput) searchInput.value = "";
        getOptions(dropdown).forEach((o) => (o.style.display = "block"));
        mainInput.setAttribute("aria-expanded", "false");
      };

      const toggleNewForm = (show) => {
        if (!newForm) return;
        if (show) {
          newForm.classList.add("active");
          positionNewForm(wrapper, mainInput, newForm);
          newFormInput?.focus();
        } else newForm.classList.remove("active");
      };

      // --- Клік по стрілці ---
      arrow?.addEventListener("click", (e) => {
        e.stopPropagation();

        // закриваємо інші
        closeOthers(wrapper);

        document.querySelectorAll(".new-item-form.active").forEach((nf) => {
          if (nf !== newForm) nf.classList.remove("active");
        });

        document
          .querySelectorAll(".custom-select-wrapper.active")
          .forEach((w) => {
            if (w !== wrapper) {
              w.classList.remove("active");
              const dd = w.querySelector(".custom-select-dropdown");
              if (dd) dd.classList.remove("active");
              const mi = w.querySelector(".custom-select-input");
              if (mi) mi.setAttribute("aria-expanded", "false");
            }
          });

        if (wrapper.classList.contains("active")) {
          closeDropdown();
        } else {
          positionDropdown(wrapper, mainInput, dropdown);
          dropdown.classList.add("active");
          wrapper.classList.add("active");
          mainInput.setAttribute("aria-expanded", "true");
          searchInput?.focus();
        }
      });

      // --- Клік по головному інпуту ---
      mainInput.addEventListener("click", (e) => {
        e.stopPropagation();

        // закриваємо інші
        closeOthers(wrapper);

        document.querySelectorAll(".new-item-form.active").forEach((nf) => {
          nf.classList.remove("active");
        });

        if (wrapper.classList.contains("active")) return;

        positionDropdown(wrapper, mainInput, dropdown);
        dropdown.classList.add("active");
        wrapper.classList.add("active");
        mainInput.setAttribute("aria-expanded", "true");
        searchInput?.focus();
      });

      // --- Фільтрування при вводі ---
      mainInput.addEventListener(
        "input",
        debounce(() => filterOptions(mainInput.value), 120)
      );

      // фільтрація + дублювання пошуку в mainInput
      searchInput.addEventListener(
        "input",
        debounce(() => filterOptions(searchInput.value), 120)
      );
      // дублювання в головний інпут одразу (без дебаунсу)
      searchInput.addEventListener("input", (e) => {
        mainInput.value = e.target.value;
      });

      // --- Клік по опції ---
      dropdown.addEventListener("click", (e) => {
        const option = e.target.closest(".custom-select-option");
        if (option) {
          mainInput.value = option.textContent.trim();
          closeDropdown();
        }
      });

      // --- Кнопка додавання нового елемента ---
      if (addButton) {
        addButton.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          closeOthers(wrapper);
          document.querySelectorAll(".new-item-form.active").forEach((nf) => {
            if (nf !== newForm) nf.classList.remove("active");
          });
          document
            .querySelectorAll(".custom-select-wrapper.active")
            .forEach((w) => {
              if (w !== wrapper) {
                w.classList.remove("active");
                const dd = w.querySelector(".custom-select-dropdown");
                if (dd) dd.classList.remove("active");
                const mi = w.querySelector(".custom-select-input");
                if (mi) mi.setAttribute("aria-expanded", "false");
              }
            });
          closeDropdown();
          toggleNewForm(true);
        });
      }

      if (newFormInput) {
        newFormInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            const value = newFormInput.value.trim();
            if (value) {
              mainInput.value = value;
              const newOpt = document.createElement("div");
              newOpt.className = "custom-select-option";
              newOpt.textContent = value;
              newOpt.setAttribute("role", "option");
              dropdown.appendChild(newOpt);
              toggleNewForm(false);
              newFormInput.value = "";
            }
          } else if (e.key === "Escape") {
            toggleNewForm(false);
          }
        });

        newForm.addEventListener("click", (ev) => ev.stopPropagation());
      }

      mainInput.addEventListener("keydown", (e) => {
        const visibleOpts = getOptions(dropdown).filter(
          (o) => o.style.display !== "none"
        );
        if (!visibleOpts.length) return;
        let idx = visibleOpts.findIndex((o) =>
          o.classList.contains("focused-option")
        );
        if (idx === -1) idx = 0;
        if (e.key === "ArrowDown") {
          e.preventDefault();
          visibleOpts.forEach((o) => o.classList.remove("focused-option"));
          idx = (idx + 1) % visibleOpts.length;
          visibleOpts[idx].classList.add("focused-option");
          visibleOpts[idx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          visibleOpts.forEach((o) => o.classList.remove("focused-option"));
          idx = (idx - 1 + visibleOpts.length) % visibleOpts.length;
          visibleOpts[idx].classList.add("focused-option");
          visibleOpts[idx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "Enter") {
          e.preventDefault();
          const sel = visibleOpts[idx];
          if (sel) {
            mainInput.value = sel.textContent.trim();
            closeDropdown();
          }
        } else if (e.key === "Escape") {
          closeDropdown();
        }
      });

      searchInput.addEventListener("click", (e) => e.stopPropagation());
    });
  } catch (err) {
    console.error("initCustomSelects (selects) error:", err);
  }


}
