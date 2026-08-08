export function initCountryFilter() {
  const countrySearchInput = document.querySelector(
    ".country-search-box__input"
  );
  const checkboxGroups = document.querySelectorAll(
    ".checkbox-group, .checkbox-group-special, .checkbox-group-mobile"
  );

  // 1. Ініціалізація пагінації та пошуку для чекбоксів (Ваш старий код)
  createNavigationButtons();

  if (countrySearchInput && checkboxGroups.length > 0) {
    const groupStates = new Map();

    checkboxGroups.forEach((group) => {
      const state = initGroupPagination(group);
      groupStates.set(group, state);
    });

    function updateVisibility() {
      const allGroupsHidden = Array.from(checkboxGroups).every(
        (group) => window.getComputedStyle(group).display === "none"
      );
      if (countrySearchInput) {
        countrySearchInput.style.display = allGroupsHidden ? "none" : "block";
      }

      checkboxGroups.forEach((group) => {
        const state = groupStates.get(group);
        const navId = group.getAttribute("data-nav-id");
        const navContainer = document.querySelector(
          `.pagination-nav[data-nav-id="${navId}"]`
        );

        if (navContainer) {
          const isGroupVisible =
            window.getComputedStyle(group).display !== "none";

          navContainer.classList.toggle("show", isGroupVisible);
          navContainer.setAttribute("aria-hidden", !isGroupVisible);

          if (isGroupVisible && !state.isSearchMode) {
            showPage(group, state.currentPage, state.itemsPerPage, false);
            updateNavigationButtons(
              navContainer,
              state.currentPage,
              state.totalPages
            );
          }
        }
      });
    }

    updateVisibility();
    requestAnimationFrame(() => updateVisibility());

    countrySearchInput.addEventListener("input", () => {
      const query = countrySearchInput.value.trim().toLowerCase();

      checkboxGroups.forEach((group) => {
        const state = groupStates.get(group);
        const checkboxes = group.querySelectorAll(".container-checkbox");
        const visibleItems = [];

        const isGroupVisible =
          window.getComputedStyle(group).display !== "none";
        const navId = group.getAttribute("data-nav-id");
        const navContainer = document.querySelector(
          `.pagination-nav[data-nav-id="${navId}"]`
        );

        if (!isGroupVisible && navContainer) {
          navContainer.classList.remove("show");
          navContainer.setAttribute("aria-hidden", "true");
          return;
        }

        checkboxes.forEach((checkbox) => {
          const labelEl = checkbox.querySelector(".country-label");
          const en = labelEl
            ? labelEl.getAttribute("data-en")?.toLowerCase() || ""
            : "";
          const ua = labelEl
            ? labelEl.getAttribute("data-ua")?.toLowerCase() || ""
            : "";

          if (query === "" || en.includes(query) || ua.includes(query)) {
            visibleItems.push(checkbox);
          }
        });

        state.visibleItems = visibleItems;
        state.searchTotalPages = Math.ceil(
          visibleItems.length / state.itemsPerPage
        );

        if (navContainer && isGroupVisible) {
          if (query === "") {
            navContainer.classList.add("show");
            state.isSearchMode = false;
            const pageToRestore =
              state.lastPageBeforeSearch ?? state.currentPage;
            state.currentPage = Math.min(pageToRestore, state.totalPages - 1);
            showPage(group, state.currentPage, state.itemsPerPage, false);
            updateNavigationButtons(
              navContainer,
              state.currentPage,
              state.totalPages
            );
          } else {
            if (!state.isSearchMode) {
              state.lastPageBeforeSearch = state.currentPage;
            }

            navContainer.classList.toggle(
              "show",
              visibleItems.length > state.itemsPerPage
            );
            state.isSearchMode = true;
            state.searchCurrentPage = 0;

            if (visibleItems.length > 0) {
              showSearchResults(group, visibleItems, 0, state.itemsPerPage);
              updateNavigationButtons(navContainer, 0, state.searchTotalPages);
            } else {
              checkboxes.forEach((checkbox) => {
                checkbox.style.display = "none";
              });
            }
          }
        }
      });

      updateVisibility();
    });

    window.addEventListener("resize", updateVisibility);
  }

  // 2. ЗАПУСК ЛОГІКИ ФІЛЬТРАЦІЇ УНІВЕРСИТЕТІВ
  initUniversityFiltering();

  // --- Допоміжні функції пагінації ---

  function initGroupPagination(group) {
    const checkboxes = group.querySelectorAll(".container-checkbox");
    const itemsPerPage =
      group.classList.contains("checkbox-group-special") ||
      group.classList.contains("checkbox-group-mobile")
        ? 6
        : 12;
    const totalPages = Math.ceil(checkboxes.length / itemsPerPage);

    let navContainer = group.nextElementSibling;
    if (navContainer && navContainer.classList.contains("pagination-nav")) {
      const existingNavId = navContainer.getAttribute("data-nav-id");
      group.setAttribute("data-nav-id", existingNavId);
    } else {
      const navId = `nav-${Math.random().toString(36).substr(2, 9)}`;
      group.setAttribute("data-nav-id", navId);
      addNavigationForGroup(group, {
        currentPage: 0,
        totalPages,
        itemsPerPage,
        navId,
        isSearchMode: false,
        searchCurrentPage: 0,
        searchTotalPages: 0,
        visibleItems: [],
        lastPageBeforeSearch: 0,
      });
    }

    const state = {
      currentPage: 0,
      totalPages,
      itemsPerPage,
      navId: group.getAttribute("data-nav-id"),
      isSearchMode: false,
      searchCurrentPage: 0,
      searchTotalPages: 0,
      visibleItems: [],
      lastPageBeforeSearch: 0,
    };

    if (window.getComputedStyle(group).display !== "none") {
      showPage(group, 0, itemsPerPage, false);
    }

    return state;
  }

  function addNavigationForGroup(group, state) {
    const navContainer = document.createElement("div");
    navContainer.className = "pagination-nav";
    navContainer.setAttribute("data-nav-id", state.navId);
    navContainer.innerHTML = `
      <button class="nav-arrow prev-arrow" disabled>←</button>
      <span class="page-info">1/${state.totalPages}</span>
      <button class="nav-arrow next-arrow">→</button>
    `;

    group.parentNode.insertBefore(navContainer, group.nextSibling);
    navContainer.classList.remove("show");
    navContainer.setAttribute("aria-hidden", "true");

    const prevBtn = navContainer.querySelector(".prev-arrow");
    const nextBtn = navContainer.querySelector(".next-arrow");

    state.navElements = { prevBtn, nextBtn, navContainer };

    prevBtn.addEventListener("click", () => {
      if (state.isSearchMode) {
        if (state.searchCurrentPage > 0) {
          state.searchCurrentPage--;
          showSearchResults(
            group,
            state.visibleItems,
            state.searchCurrentPage,
            state.itemsPerPage
          );
          updateNavigationButtons(
            navContainer,
            state.searchCurrentPage,
            state.searchTotalPages
          );
        }
      } else {
        if (state.currentPage > 0) {
          state.currentPage--;
          showPage(group, state.currentPage, state.itemsPerPage, false);
          updateNavigationButtons(
            navContainer,
            state.currentPage,
            state.totalPages
          );
        }
      }
    });

    nextBtn.addEventListener("click", () => {
      if (state.isSearchMode) {
        if (state.searchCurrentPage < state.searchTotalPages - 1) {
          state.searchCurrentPage++;
          showSearchResults(
            group,
            state.visibleItems,
            state.searchCurrentPage,
            state.itemsPerPage
          );
          updateNavigationButtons(
            navContainer,
            state.searchCurrentPage,
            state.searchTotalPages
          );
        }
      } else {
        if (state.currentPage < state.totalPages - 1) {
          state.currentPage++;
          showPage(group, state.currentPage, state.itemsPerPage, false);
          updateNavigationButtons(
            navContainer,
            state.currentPage,
            state.totalPages
          );
        }
      }
    });
  }

  function updateNavigationButtons(navContainer, currentPage, totalPages) {
    const prevBtn = navContainer.querySelector(".prev-arrow");
    const nextBtn = navContainer.querySelector(".next-arrow");
    const pageInfo = navContainer.querySelector(".page-info");

    pageInfo.textContent = `${currentPage + 1}/${totalPages}`;
    prevBtn.disabled = currentPage === 0;
    nextBtn.disabled = currentPage === totalPages - 1;
  }

  function showPage(group, page, itemsPerPage) {
    const checkboxes = group.querySelectorAll(".container-checkbox");
    const start = page * itemsPerPage;
    const end = start + itemsPerPage;

    checkboxes.forEach((checkbox, index) => {
      if (index >= start && index < end) {
        checkbox.style.display = "inline-flex";
        applyFadeIn(checkbox);
      } else {
        checkbox.style.display = "none";
      }
    });
  }

  function showSearchResults(group, visibleItems, page, itemsPerPage) {
    const allCheckboxes = group.querySelectorAll(".container-checkbox");
    allCheckboxes.forEach((checkbox) => {
      checkbox.style.display = "none";
    });

    const start = page * itemsPerPage;
    const end = start + itemsPerPage;

    visibleItems.slice(start, end).forEach((checkbox) => {
      checkbox.style.display = "inline-flex";
      applyFadeIn(checkbox);
    });
  }

  function createNavigationButtons() {
    const style = document.createElement("style");
    style.textContent = `
      .pagination-nav {
        display: none;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 15px 0;
      }
      .pagination-nav.show {
        display: flex;
      }
      .nav-arrow {
        background: none;
        border: 1px solid #ccc;
        padding: 5px 10px;
        cursor: pointer;
        border-radius: 3px;
        font-size: 14px;
      }
      .nav-arrow:hover:not(:disabled) {
        background-color: #f0f0f0;
      }
      .nav-arrow:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      .page-info {
        font-size: 14px;
        color: #666;
      }
      .fade-in {
        animation: fadeIn 0.2s ease-in;
      }
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
    `;
    document.head.appendChild(style);
  }

  function applyFadeIn(el) {
    el.classList.remove("fade-in");
    void el.offsetWidth;
    el.classList.add("fade-in");
  }

  // === НОВА ЛОГІКА: Фільтрація університетів ===
  function initUniversityFiltering() {
    // Знаходимо всі чекбокси (включаючи мобільні)
    const inputs = document.querySelectorAll(".container-checkbox__input");
    
    // Знаходимо всі картки університетів (десктоп і мобільні), окрім повідомлень про відсутність результатів
    const cards = document.querySelectorAll(".university-card:not(.no-results-message):not(#no-filter-results), .university-card-m:not(.no-results-message-mobile):not(#no-filter-results-mobile)");

    // Знаходимо чекбокси "All" (Всі країни)
    const allCheckboxes = document.querySelectorAll('.container-checkbox__input[value="all"]');

    // Функція застосування фільтру
    function applyFilter() {
      // Збираємо список обраних країн (ігноруючи 'all')
      const checkedCountries = Array.from(inputs)
        .filter(input => input.checked && input.value !== 'all')
        .map(input => input.value);

      // Чи обрано "Всі" або жодна країна не обрана?
      // Якщо жодна не обрана, вважаємо, що треба показати всі (дефолтна поведінка)
      const showAll = checkedCountries.length === 0;

      // Якщо список порожній, повертаємо галочку на "All", щоб користувач бачив стан
      if (showAll) {
        allCheckboxes.forEach(cb => cb.checked = true);
      }

      let visibleCountDesktop = 0;
      let visibleCountMobile = 0;

      cards.forEach(card => {
        const country = card.getAttribute("data-country");
        const isMobile = card.classList.contains("university-card-m");
        
        // Показуємо, якщо "Всі" або країна є у списку обраних
        if (showAll || checkedCountries.includes(country)) {
          card.style.display = ""; // Скидаємо inline style (display: none), повертається flex/block з CSS
          if (isMobile) {
            visibleCountMobile++;
          } else {
            visibleCountDesktop++;
          }
        } else {
          card.style.display = "none";
        }
      });

      const noResultsDesktop = document.getElementById("no-filter-results");
      const noResultsMobile = document.getElementById("no-filter-results-mobile");
      
      const desktopCards = document.querySelectorAll('.university-card:not(.no-results-message):not(#no-filter-results)');
      const mobileCards = document.querySelectorAll('.university-card-m:not(.no-results-message-mobile):not(#no-filter-results-mobile)');
      
      if (noResultsDesktop) {
        if (desktopCards.length === 0) {
          noResultsDesktop.style.display = 'none';
        } else {
          noResultsDesktop.style.display = visibleCountDesktop === 0 ? 'flex' : 'none';
        }
      }
      
      if (noResultsMobile) {
        if (mobileCards.length === 0) {
          noResultsMobile.style.display = 'none';
        } else {
          noResultsMobile.style.display = visibleCountMobile === 0 ? 'block' : 'none';
        }
      }
    }

    // Слухач подій для всіх чекбоксів
    inputs.forEach(input => {
      input.addEventListener("change", (e) => {
        const isAll = e.target.value === "all";
        const isChecked = e.target.checked;

        if (isAll && isChecked) {
          // Якщо натиснули "All", знімаємо вибір з усіх інших
          inputs.forEach(i => {
            if (i.value !== "all") i.checked = false;
          });
          // Синхронізуємо інші чекбокси "All" (наприклад, у мобільній і десктоп версіях)
          allCheckboxes.forEach(cb => cb.checked = true);
        } else if (!isAll && isChecked) {
          // Якщо обрали конкретну країну, знімаємо галочку з "All"
          allCheckboxes.forEach(cb => cb.checked = false);
        }

        applyFilter();
      });
    });

    // Запускаємо фільтрацію одразу при завантаженні (щоб все показати або застосувати збережений стан)
    applyFilter();
  }
}