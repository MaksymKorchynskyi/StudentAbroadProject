export function initSlider() {
  const path = window.location.pathname;
  const allowedPages = ["uni-list.html", "program-list.html"];
  const isAllowed = allowedPages.some(
    (page) => path.endsWith(page) || path === `/${page}`
  );

  if (!isAllowed) {
    return;
  }

  // --- Визначення типу карток ---
  const programCards = document.querySelectorAll(
    ".program-card-m:not(.no-results-message-mobile):not(#no-filter-results-mobile)"
  );
  const isProgramPage = path.endsWith("program-list.html");
  const cardSelector = programCards.length
    ? ".program-card-m"
    : ".university-card-m";

  // --- Вибір стрілок ---
  const prevArrow = document.querySelector(
    isProgramPage ? ".slider__arrow--left-p" : ".slider__arrow--left"
  );
  const nextArrow = document.querySelector(
    isProgramPage ? ".slider__arrow--right-p" : ".slider__arrow--right"
  );

  // Основні елементи слайдера
  const track = document.querySelector(".slider__track");
  const indicators = document.querySelectorAll(".slider__indicator");
  const indContainer = document.querySelector(".slider__indicators");

  if (!track) {
    return;
  }

  // --- Стан слайдера ---
  let currentIndex = 0;
  let isAnimating = false;
  let activeCards = [];

  // --- Селектор для оригінальних (не-клонованих) карток ---
  const originalCardSelector = `${cardSelector}:not(.no-results-message-mobile):not(#no-filter-results-mobile):not([data-clone="true"])`;

  /**
   * Збирає лише ВИДИМІ оригінальні картки (не клони, не display:none)
   */
  function getVisibleOriginalCards() {
    const allOriginals = Array.from(track.querySelectorAll(originalCardSelector));
    return allOriginals.filter(
      (card) => card.style.display !== "none" && window.getComputedStyle(card).display !== "none"
    );
  }

  /**
   * Видаляє всі клоновані елементи з треку
   */
  function removeClones() {
    const clones = track.querySelectorAll('[data-clone="true"]');
    clones.forEach((clone) => clone.remove());
  }

  /**
   * Ховає/показує UI елементи слайдера (стрілки, індикатори)
   */
  function setSliderUIVisibility(visible) {
    if (prevArrow) prevArrow.style.display = visible ? "" : "none";
    if (nextArrow) nextArrow.style.display = visible ? "" : "none";
    if (indContainer) indContainer.style.display = visible ? "" : "none";
  }

  /**
   * Оновлює індикатори слайдера
   */
  function updateIndicators() {
    if (!indicators.length) return;

    let indicatorIndex;
    if (currentIndex >= activeCards.length) {
      indicatorIndex = 0;
    } else if (currentIndex < 0) {
      indicatorIndex = indicators.length - 1;
    } else {
      indicatorIndex = currentIndex % indicators.length;
    }

    indicators.forEach((indicator, index) => {
      indicator.classList.toggle("active", index === indicatorIndex);
    });
  }

  /**
   * Оновлює позицію слайдера з анімацією
   */
  function updateSlider() {
    if (isAnimating) return;

    isAnimating = true;
    track.style.transition = "transform 0.4s ease-in-out";
    track.style.transform = `translateX(-${(currentIndex + 1) * 100}%)`;

    updateIndicators();

    setTimeout(() => {
      isAnimating = false;

      if (currentIndex >= activeCards.length) {
        track.style.transition = "none";
        currentIndex = 0;
        track.style.transform = `translateX(-${(currentIndex + 1) * 100}%)`;
      } else if (currentIndex < 0) {
        track.style.transition = "none";
        currentIndex = activeCards.length - 1;
        track.style.transform = `translateX(-${(currentIndex + 1) * 100}%)`;
      }
    }, 400);
  }

  function goToNextSlide() {
    if (isAnimating) return;
    currentIndex++;
    updateSlider();
  }

  function goToPrevSlide() {
    if (isAnimating) return;
    currentIndex--;
    updateSlider();
  }

  /**
   * Головна функція перебудови слайдера.
   * Викликається при зміні фільтрів або при ініціалізації.
   */
  function rebuildSlider() {
    // 1. Видалити старі клони
    removeClones();

    // 2. Зібрати лише видимі картки
    activeCards = getVisibleOriginalCards();

    // 3. Скинути позицію
    currentIndex = 0;
    isAnimating = false;
    track.style.transition = "none";

    // 4. Edge case: 0 видимих карток
    if (activeCards.length === 0) {
      setSliderUIVisibility(false);
      track.style.transform = "translateX(0)";
      return;
    }

    // 5. Edge case: 1 видима картка — показати без слайдера
    if (activeCards.length === 1) {
      setSliderUIVisibility(false);
      track.style.transform = "translateX(0)";
      return;
    }

    // 6. Показати UI елементи
    setSliderUIVisibility(true);

    // 7. Клонувати першу і останню видимі картки для безкінечного ефекту
    const firstClone = activeCards[0].cloneNode(true);
    const lastClone = activeCards[activeCards.length - 1].cloneNode(true);
    firstClone.setAttribute("data-clone", "true");
    lastClone.setAttribute("data-clone", "true");

    // 8. Додати клони в трек
    track.appendChild(firstClone);
    track.insertBefore(lastClone, activeCards[0]);

    // 9. Встановити початкову позицію (перша оригінальна картка = індекс 1 через prepended clone)
    track.style.transform = `translateX(-100%)`;

    // 10. Оновити індикатори
    updateIndicators();
  }

  // --- НАВІГАЦІЙНІ СТРІЛКИ ---
  if (prevArrow) prevArrow.addEventListener("click", goToPrevSlide);
  if (nextArrow) nextArrow.addEventListener("click", goToNextSlide);

  // --- СВАЙПИ ---
  let startX = 0;
  let endX = 0;

  track.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX;
  }, { passive: true });

  track.addEventListener("touchend", (e) => {
    endX = e.changedTouches[0].clientX;
    handleSwipe();
  });

  function handleSwipe() {
    const swipeThreshold = 50;
    const diffX = startX - endX;

    if (Math.abs(diffX) > swipeThreshold) {
      if (diffX > 0) goToNextSlide();
      else goToPrevSlide();
    }
  }

  // --- СЛУХАЧ CustomEvent від фільтрів ---
  document.addEventListener("filter-changed", () => {
    rebuildSlider();
  });

  // --- ІНІЦІАЛІЗАЦІЯ ---
  rebuildSlider();
}
