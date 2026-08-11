/**
 * Ініціалізує скорочення текстів у програмних картках
 */
export function initTrimText(limit = 230) {
  const paragraphs = document.querySelectorAll(".program-info-m p");
  paragraphs.forEach((p) => {
    const originalText = p.textContent.trim();

    if (originalText.length > limit) {
      const trimmedText = originalText.slice(0, limit).trim() + "…";
      p.textContent = trimmedText;
    }

    ["data-en", "data-ua"].forEach((attr) => {
      const value = p.getAttribute(attr);
      if (value && value.length > limit) {
        const trimmed = value.slice(0, limit).trim() + "…";
        p.setAttribute(attr, trimmed);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTrimText(230);
});
