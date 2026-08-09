export function initSlider() {
  const path = window.location.pathname;
  const allowedPages = ["uni-list.html", "program-list.html"];
  const isAllowed = allowedPages.some(
    (page) => path.endsWith(page) || path === `/${page}`
  );

  if (!isAllowed) {
    console.log("Slider initialization skipped: not on allowed pages");
    return;
  }

  // --- ОРИГІНАЛ ---
  const cards = document.querySelectorAll(".university-card-m:not(.no-results-message-mobile):not(#no-filter-results-mobile)");

  // --- ВИБІР АКТИВНИХ КАРТОК ---
  const programCards = document.querySelectorAll(".program-card-m:not(.no-results-message-mobile):not(#no-filter-results-mobile)");
  const activeCardsNodeList = programCards.length ? programCards : cards;
  const cardSelector = programCards.length
    ? ".program-card-m"
    : ".university-card-m";

  // --- ВИБІР ПРАВИЛЬНИХ СТРІЛОК ---
  const isProgramPage = path.endsWith("program-list.html");
  const prevArrow = document.querySelector(
    isProgramPage ? ".slider__arrow--left-p" : ".slider__arrow--left"
  );
  const nextArrow = document.querySelector(
    isProgramPage ? ".slider__arrow--right-p" : ".slider__arrow--right"
  );

  // Основні елементи слайдера
  const track = document.querySelector(".slider__track");
  const indicators = document.querySelectorAll(".slider__indicator");

  // Початкові змінні
  let currentIndex = 0;
  let isAnimating = false;

  // Перевірка наявності потрібних елементів
  if (!track || activeCardsNodeList.length === 0) {
    if (prevArrow) prevArrow.style.display = 'none';
    if (nextArrow) nextArrow.style.display = 'none';
    const indContainer = document.querySelector('.slider__indicators');
    if (indContainer) indContainer.style.display = 'none';
    return;
  }

  // Якщо тільки 1 картка, не потрібно ініціалізувати слайдер (стрілки і індикатори ховаємо)
  if (activeCardsNodeList.length === 1) {
    if (prevArrow) prevArrow.style.display = 'none';
    if (nextArrow) nextArrow.style.display = 'none';
    const indContainer = document.querySelector('.slider__indicators');
    if (indContainer) indContainer.style.display = 'none';
    return;
  }

  if (!indicators.length) {
    return;
  }

  const activeCards = Array.from(activeCardsNodeList);

  // Клонуємо перший і останній слайди для безкінечного ефекту
  const firstClone = activeCards[0].cloneNode(true);
  const lastClone = activeCards[activeCards.length - 1].cloneNode(true);

  // Додаємо клони в трек
  track.appendChild(firstClone);
  track.insertBefore(lastClone, activeCards[0]);

  // Всі слайди всередині треку
  const allSlides = Array.from(track.querySelectorAll(cardSelector));
  const totalSlides = allSlides.length;

  console.log("Slider init:", {
    page: path,
    cardSelector,
    totalSlides,
    arrows: { prev: !!prevArrow, next: !!nextArrow },
  });

  // Початкове зміщення треку
  track.style.transform = `translateX(-${100}%)`;

  // === ФУНКЦІЇ СЛАЙДЕРА ===

  function updateIndicators() {
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

  // --- НАВІГАЦІЙНІ СТРІЛКИ ---
  if (prevArrow) prevArrow.addEventListener("click", goToPrevSlide);
  if (nextArrow) nextArrow.addEventListener("click", goToNextSlide);

  // --- СВАЙПИ ---
  let startX = 0;
  let endX = 0;

  if (track) {
    track.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
    });

    track.addEventListener("touchend", (e) => {
      endX = e.changedTouches[0].clientX;
      handleSwipe();
    });
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diffX = startX - endX;

    if (Math.abs(diffX) > swipeThreshold) {
      if (diffX > 0) goToNextSlide();
      else goToPrevSlide();
    }
  }

  // --- ІНІЦІАЛІЗАЦІЯ ---
  updateIndicators();
}
