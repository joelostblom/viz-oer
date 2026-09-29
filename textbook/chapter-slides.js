// Escape returns to the chapter, rather than opening Reveal's slide overview.
(() => {
  const chapter = document.querySelector('meta[name="chapter-url"]');
  if (!chapter) return;

  const headingFirst = () => {
    const deck = window.Reveal;
    if (!deck) return;
    const resetFragments = () => {
      const slide = deck.getCurrentSlide();
      if (!slide) return;
      slide.classList.add("resetting-fragments");
      deck.navigateFragment(-1);
      // Commit the hidden state before re-enabling fades for the next advance.
      void slide.offsetHeight;
      requestAnimationFrame(() => slide.classList.remove("resetting-fragments"));
    };
    deck.on("ready", resetFragments);
    deck.on("slidechanged", resetFragments);
    if (deck.isReady()) resetFragments();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", headingFirst, { once: true });
  } else {
    headingFirst();
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    event.preventDefault();
    event.stopImmediatePropagation();

    const destination = new URL(chapter.content, document.baseURI);
    const slide = window.Reveal?.getCurrentSlide()?.id;
    // Section IDs are shared by the chapter and deck. Synthetic slides have
    // no corresponding chapter anchor, so those return to the chapter top.
    if (slide && slide !== "title-slide" && slide !== "learning-outcomes"
        && !slide.startsWith("visualization-continued-")) {
      destination.hash = slide;
    }
    window.location.assign(destination.href);
  }, true);
})();
