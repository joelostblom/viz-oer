// Presentation controls, heading-first reveals, and returning to the chapter.
(() => {
  // Decks live in slides/ with the same filename as their reading-view chapter.
  const filename = window.location.pathname.split("/").pop();
  const chapter = new URL(`../${filename}`, window.location.href);

  const installCodeToggles = (deck) => {
    const query = new URLSearchParams(window.location.search);
    if (query.get("view") === "print" || query.has("print-pdf")) return;
    let codeId = 0;
    document.querySelectorAll(".reveal .slides .code-copy-outer-scaffold").forEach(scaffold => {
      if (scaffold.closest("aside.notes, .cell-output")
          || scaffold.classList.contains("slide-code-toggle-ready")) return;
      const source = scaffold.querySelector(":scope > div.sourceCode, :scope > pre");
      const copy = scaffold.querySelector(":scope > .code-copy-button");
      if (!source || !copy) return;
      if (!source.id) {
        let id;
        do { id = `slide-code-${++codeId}`; } while (document.getElementById(id));
        source.id = id;
      }
      source.classList.add("slide-code-source");
      const content = document.createElement("div");
      content.className = "slide-code-content";
      source.before(content);
      content.append(source);
      scaffold.classList.add("slide-code-toggle-ready");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "slide-code-toggle";
      button.setAttribute("aria-controls", source.id);
      button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 15 6-6 6 6"/></svg>';
      const setExpanded = (expanded) => {
        scaffold.classList.toggle("slide-code-collapsed", !expanded);
        content.inert = !expanded;
        button.setAttribute("aria-expanded", String(expanded));
        button.setAttribute("aria-label", expanded ? "Hide code" : "Show code");
        button.title = expanded ? "Hide code" : "Show code";
      };
      setExpanded(true);
      button.addEventListener("click", (event) => {
        setExpanded(button.getAttribute("aria-expanded") !== "true");
        deck.layout();
        if (event.detail) button.blur();
      });
      content.addEventListener("transitionend", (event) => {
        if (event.target === content && event.propertyName === "grid-template-rows") deck.layout();
      });
      // Keep native button activation from also advancing Reveal's fragments.
      button.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") event.stopPropagation();
      });
      copy.before(button);
    });
  };

  const headingFirst = () => {
    const deck = window.Reveal;
    if (!deck) return;
    installCodeToggles(deck);
    let footerTimer;
    const showTitleHint = () => {
      clearTimeout(footerTimer);
      const root = deck.getRevealElement();
      const onTitle = deck.getCurrentSlide()?.id === "title-slide";
      root.classList.toggle("show-title-hint", onTitle);
      if (onTitle) {
        footerTimer = setTimeout(() => root.classList.remove("show-title-hint"), 3000);
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
      deck.registerKeyboardShortcut("ESC, Q, O",
        "O: toggle overview. Esc/Q: close open tools; otherwise return to the chapter.");
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
    if (event.key !== "Escape" && event.key.toLowerCase() !== "q") return;
    const deck = window.Reveal;
    if (!deck?.isReady?.()) return;
    if (event.target instanceof Element
        && (event.target.isContentEditable
          || event.target.matches("input, textarea, select"))) return;

    // Dispatch Escape so Q follows the same contextual behavior, including
    // Reveal's own handlers for menus, help, and overview.
    if (event.key.toLowerCase() === "q") {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      event.target.dispatchEvent(new KeyboardEvent("keydown", {
        key: "Escape", code: "Escape", keyCode: 27, which: 27,
        bubbles: true, cancelable: true
      }));
      return;
    }

    // Let Reveal and its plugins handle Escape while their interfaces are open.
    // In particular, closing help must not immediately exit the presentation.
    if (deck.getPlugin("menu")?.isOpen() || deck.isOverview()
        || deck.getRevealElement().querySelector(".overlay")) return;

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
