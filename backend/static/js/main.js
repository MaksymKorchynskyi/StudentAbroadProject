// main.js - додаємо імпорт та ініціалізацію

import { initLanguageSwitcher } from "./modules/language-switcher.js?v=2";
import { initScrollIndicator } from "./modules/scroll-indicator.js?v=3";
import { initCustomSelects } from "./modules/custom-select.js?v=2";
import { initCountryFilter } from "./modules/country-filter.js?v=2";
import { initAddUniversity } from "./modules/add-university.js?v=2";
import { initFAQ } from "./modules/faq.js?v=2";
import { initSlider } from "./modules/slider-mobile.js?v=5";
import { modalBtnClose } from "./modules/modal.js?v=2";
import { burgerMenu } from "./modules/burger-menu.js?v=2";
import { initProgramSearch } from "./modules/program-search.js?v=2";
import { initTrimText } from "./modules/trimProgramText.js?v=2";

document.addEventListener("DOMContentLoaded", () => {
  initLanguageSwitcher();
  initScrollIndicator();
  initCustomSelects();
  initCountryFilter();
  initAddUniversity();
  modalBtnClose();
  initSlider();
  burgerMenu();
  initFAQ();
  initProgramSearch();
  initTrimText()
});
