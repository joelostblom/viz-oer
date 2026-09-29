// Escape dismisses Reveal's UI first, and exits only from a normal slide.
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
    const onReady = () => {
      resetFragments();
      deck.registerKeyboardShortcut("ESC, O",
        "O: toggle overview. Esc: close open tools; otherwise return to the chapter.");
    };
    deck.on("ready", onReady);
    deck.on("slidechanged", resetFragments);
    if (deck.isReady()) onReady();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", headingFirst, { once: true });
  } else {
    headingFirst();
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const deck = window.Reveal;
    if (!deck?.isReady?.()) return;

    // Let Reveal and its plugins handle Escape while their interfaces are open.
    // In particular, closing help must not immediately exit the presentation.
    if (deck.getPlugin("menu")?.isOpen() || deck.isOverview()
        || deck.getRevealElement().querySelector(".overlay")) return;
    if (event.target instanceof Element
        && (event.target.isContentEditable
          || event.target.matches("input, textarea, select"))) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    // A paused/black screen is also a temporary mode, not a chapter exit.
    if (deck.isPaused()) {
      deck.togglePause(false);
      return;
    }

    const destination = new URL(chapter.content, document.baseURI);
    const slide = deck.getCurrentSlide()?.id;
    // Section IDs are shared by the chapter and deck. Synthetic slides have
    // no corresponding chapter anchor, so those return to the chapter top.
    if (slide && slide !== "title-slide" && slide !== "learning-outcomes"
        && !slide.startsWith("visualization-continued-")) {
      destination.hash = slide;
    }
    window.location.assign(destination.href);
  }, true);
})();
