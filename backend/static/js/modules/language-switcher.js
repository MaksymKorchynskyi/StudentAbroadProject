export function initLanguageSwitcher() {
  const switchButtons = document.querySelectorAll(".js-switch-button");
  const searchInputsSelector = ".search-box__input";

  let currentLang = localStorage.getItem("lang") || "en";

  function applyLangToElement(el, lang) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return;
    if (!el.hasAttribute(`data-en`) || !el.hasAttribute(`data-ua`)) return;

    if (el.dataset._langApplied === lang) return;

    const translation = el.getAttribute(`data-${lang}`);
    if (!translation) return;
    const htmlTags = [
      "H1",
      "H2",
      "H3",
      "H4",
      "H5",
      "P",
      "A",
      "BUTTON",
      "LABEL",
      "INPUT",
      "TEXTAREA",
      "SELECT",
    ];

    if (
      htmlTags.includes(el.tagName) ||
      el.classList.contains("about-us__title") ||
      el.classList.contains("faq__answer-text")
    ) {
      el.innerHTML = translation;
    } else {
      el.textContent = translation;
    }

    el.dataset._langApplied = lang;
  }

  function applyLangToAll(lang) {
    currentLang = lang;
    document.querySelectorAll("[data-en][data-ua]").forEach((el) => {
      applyLangToElement(el, lang);
    });
    document.querySelectorAll(searchInputsSelector).forEach((input) => {
      const ph = input.getAttribute(`data-${lang}`);
      if (ph) input.placeholder = ph;
      input.dataset._langApplied = lang;
    });

    switchButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
    });

    localStorage.setItem("lang", lang);
  }
  switchButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const selectedLang = this.getAttribute("data-lang");
      if (!selectedLang) return;
      applyLangToAll(selectedLang);
    });
  });

  applyLangToAll(currentLang);
  let debounceTimer = null;
  const observer = new MutationObserver((mutations) => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType !== Node.ELEMENT_NODE) return;
          if (node.matches && node.matches("[data-en][data-ua]")) {
            applyLangToElement(node, currentLang);
          }
          node.querySelectorAll &&
            node.querySelectorAll("[data-en][data-ua]").forEach((el) => {
              applyLangToElement(el, currentLang);
            });

          node.querySelectorAll &&
            node.querySelectorAll(searchInputsSelector).forEach((input) => {
              const ph = input.getAttribute(`data-${currentLang}`);
              if (ph) input.placeholder = ph;
              input.dataset._langApplied = currentLang;
            });
        });

        if (mutation.type === "characterData") {
          const parent = mutation.target.parentElement;
          if (
            parent &&
            parent.matches &&
            parent.matches("[data-en][data-ua]")
          ) {
            applyLangToElement(parent, currentLang);
          }
        }

        if (mutation.type === "attributes") {
          const target = mutation.target;
          if (
            target &&
            target.matches &&
            target.matches("[data-en][data-ua]")
          ) {
            applyLangToElement(target, currentLang);
          }
        }
      });

      debounceTimer = null;
    }, 80);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ["data-en", "data-ua"],
  });
}
