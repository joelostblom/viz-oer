// Escape dismisses Reveal's UI first, and exits only from a normal slide.
(() => {
  // Decks live in slides/ with the same filename as their reading-view chapter.
  const filename = window.location.pathname.split("/").pop();
  const chapter = new URL(`../${filename}`, window.location.href);

  const headingFirst = () => {
    const deck = window.Reveal;
    if (!deck) return;
    let footerTimer;
    const showTitleHint = () => {
      clearTimeout(footerTimer);
      const root = deck.getRevealElement();
      const onTitle = deck.getCurrentSlide()?.id === "title-slide";
      root.classList.toggle("show-title-hint", onTitle);
      if (onTitle) {
        footerTimer = setTimeout(() => root.classList.remove("show-title-hint"), 5000);
      }
    };
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
      showTitleHint();
      deck.registerKeyboardShortcut("ESC, O",
        "O: toggle overview. Esc: close open tools; otherwise return to the chapter.");
    };
    deck.on("ready", onReady);
    deck.on("slidechanged", () => {
      resetFragments();
      showTitleHint();
    });
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

    const destination = new URL(chapter.href);
    const current = deck.getCurrentSlide();
    const slide = current?.dataset.chapterAnchor ?? current?.id;
    // Section IDs are shared by the chapter and deck. Synthetic slides have
    // no corresponding chapter anchor, so those return to the chapter top.
    if (slide && slide !== "title-slide" && slide !== "learning-outcomes"
        && !slide.startsWith("visualization-continued-")) {
      destination.hash = slide;
    }
    window.location.assign(destination.href);
  }, true);
})();
