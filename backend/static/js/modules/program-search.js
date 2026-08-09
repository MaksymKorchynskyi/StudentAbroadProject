export function initProgramSearch() {
  initSearchRedirect();

  if (window.location.pathname.includes("search.html")) {
    document.body.classList.add("search-page");

    const MOBILE_BREAKPOINT = 767;
    if (window.innerWidth <= MOBILE_BREAKPOINT) {
      document.body.classList.add("search-page-mobile");

      const programListEl = document.querySelector(".program-list");
      if (programListEl) {
        programListEl.style.display = "flex";
      }

      // 2) Резерв: вмонтуємо CSS правило з !important у head (переб'є медіа-правила)
      const styleId = "search-page-mobile-override";
      if (!document.getElementById(styleId)) {
        const style = document.createElement("style");
        style.id = styleId;
        style.textContent = `
                    /* Автоматично показувати програм-лист лише на сторінці пошуку у мобілці */
                    body.search-page.search-page-mobile .program-list {
                        display: flex !important;
                    }
                    /* Якщо програмки мають додаткові правила, переконаємось що картки теж відображаються */
                    body.search-page.search-page-mobile .program-list .program-card {
                        display: flex !important;
                    }
                `;
        document.head.appendChild(style);
      }
    }

    // Запускаємо обробку сторінки пошуку
    processSearchPage();
  }
}

/**
 * Ініціалізація перенаправлення з пошукових полів
 */
function initSearchRedirect() {
  const searchInputs = document.querySelectorAll(
    ".search-box__input, .footer__search-box .search-box__input"
  );

  searchInputs.forEach((input) => {
    input.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        const searchQuery = this.value.trim();
        if (searchQuery) {
          // Перенаправляємо на search.html з параметром пошуку
          window.location.href = `/search.html?q=${encodeURIComponent(
            searchQuery
          )}`;
        }
      }
    });
  });
}

/**
 * Обробка сторінки пошуку
 */
function processSearchPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const searchQuery = urlParams.get("q");

  if (!searchQuery) {
    displayNoResults();
    return;
  }

  loadAndFilterPrograms(searchQuery);
}

function loadAndFilterPrograms(searchQuery) {
  fetch("program-list.html")
    .then((res) => {
      if (!res.ok) throw new Error("Не вдалося завантажити список програм");
      return res.text();
    })
    .then((html) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const programCards = doc.querySelectorAll(".program-card");

      const filtered = filterPrograms(programCards, searchQuery);

      filtered.forEach((card) => (card.style.display = "flex"));

      displayResults(filtered, searchQuery);
    })
    .catch((err) => {
      console.error(err);
      displayErrorMessage();
    });
}

/**
 * Фільтрація програм за ключовим словом
 */
function filterPrograms(programCards, searchQuery) {
  const filtered = [];
  const query = searchQuery.toLowerCase().trim();

  programCards.forEach((card) => {
    const cardText = card.textContent.toLowerCase();
    const hasMatch = cardText.includes(query);

    const dataAttributes = card.querySelectorAll("[data-ua], [data-en]");
    let dataMatch = false;

    dataAttributes.forEach((element) => {
      const uaText = element.getAttribute("data-ua")?.toLowerCase() || "";
      const enText = element.getAttribute("data-en")?.toLowerCase() || "";

      if (uaText.includes(query) || enText.includes(query)) {
        dataMatch = true;
      }
    });

    if (hasMatch || dataMatch) {
      filtered.push(card.cloneNode(true));
    }
  });

  return filtered;
}

function displayResults(programs, searchQuery) {
  const mainElement = document.querySelector("main");

  if (programs.length === 0) {
    displayNoResults(searchQuery);
    return;
  }

  const resultsContainer = document.createElement("section");
  resultsContainer.className = "search-results";

  resultsContainer.innerHTML = `
    <div class="container">
      <h1 class="search-results__title"
          data-en="Search results for: '${searchQuery}'"
          data-ua="Результати пошуку для: '${searchQuery}'">
          Search results for: '${searchQuery}'
      </h1>

      <p class="search-results__count"
         data-en="Found ${programs.length} programs"
         data-ua="Знайдено ${programs.length} програм">
         Found ${programs.length} programs
      </p>

      <div class="program-list"></div>
    </div>
  `;

  const programList = resultsContainer.querySelector(".program-list");

  if (document.body.classList.contains("search-page-mobile")) {
    programList.style.display = "flex";
  }

  programs.forEach((program) => {
    const highlighted = highlightSearchTerm(program, searchQuery);
    highlighted.style.display = "flex";
    programList.appendChild(highlighted);
  });

  mainElement.appendChild(resultsContainer);

  if (window.updateLanguage) window.updateLanguage();
}

/**
 * Виділення ключового слова жовтим кольором
 */
function highlightSearchTerm(programElement, searchQuery) {
  const q = searchQuery.toLowerCase();
  const elements = programElement.querySelectorAll("h2, p, span");

  elements.forEach((el) => {
    if (el.textContent.toLowerCase().includes(q)) {
      highlightTextInElement(el, q);
    }

    if (el.hasAttribute("data-ua")) {
      let ua = el.getAttribute("data-ua");
      if (ua.toLowerCase().includes(q)) {
        el.setAttribute("data-ua", highlightText(ua, q));
      }
    }

    if (el.hasAttribute("data-en")) {
      let en = el.getAttribute("data-en");
      if (en.toLowerCase().includes(q)) {
        el.setAttribute("data-en", highlightText(en, q));
      }
    }
  });

  return programElement;
}

/**
 * Виділення тексту в елементі
 */
function highlightTextInElement(element, query) {
  const original = element.textContent;
  const highlightedHtml = highlightText(original, query);

  const attrs = {};
  for (let attr of element.attributes) {
    if (attr.name.startsWith("data-")) attrs[attr.name] = attr.value;
  }

  element.innerHTML = highlightedHtml;

  Object.entries(attrs).forEach(([k, v]) => element.setAttribute(k, v));
}

function highlightText(text, query) {
  const regex = new RegExp(`(${escapeRegex(query)})`, "gi");
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function displayNoResults(searchQuery = "") {
  const mainElement = document.querySelector("main");

  mainElement.innerHTML = `
    <section class="search">
      <div class="container">

        <h1 class="search-results__title"
            data-en="No results found"
            data-ua="Результатів не знайдено">
            No results found
        </h1>

        ${
          searchQuery
            ? `
        <p class="search-results__message"
           data-en="No programs found for: '${searchQuery}'"
           data-ua="Не знайдено програм для: '${searchQuery}'">
           No programs found for: '${searchQuery}'
        </p>
        `
            : ""
        }

        <a href="program-list.html" class="btn search-results__back-btn"
           data-en="Back to all programs"
           data-ua="Повернутися до програм">
           Back to all programs
        </a>

      </div>
    </section>
  `;
}

function displayErrorMessage() {
  const mainElement = document.querySelector("main");
  mainElement.innerHTML = `
        <section class="search-results">
            <div class="container">
                <h1 class="search-results__title" 
                    data-en="Error loading programs"
                    data-ua="Помилка завантаження програм">
                    Error loading programs
                </h1>
                <p class="search-results__message"
                   data-en="Please try again later"
                   data-ua="Будь ласка, спробуйте пізніше">
                   Please try again later
                </p>
            </div>
        </section>
    `;
}
