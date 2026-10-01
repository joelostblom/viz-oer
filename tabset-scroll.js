// Keep the clicked tab bar in place while Quarto synchronizes grouped tabsets.
// Do not replace Quarto's switching, keyboard handling, or saved preferences.
(() => {
  let anchor = null;
  let observer = null;
  let frame = 0;
  const root = document.documentElement;

  function release() {
    anchor = null;
    observer?.disconnect();
    observer = null;
    cancelAnimationFrame(frame);
    frame = 0;
    root.classList.remove("tabset-scroll-stabilizing");
  }

  function restorePosition() {
    if (!anchor) return;
    if (!anchor.element.isConnected || !anchor.element.getClientRects().length) {
      release();
      return;
    }

    const shift = anchor.element.getBoundingClientRect().top - anchor.top;
    if (Math.abs(shift) > 0.5) {
      window.scrollBy({ top: shift, left: 0, behavior: "instant" });
    }
  }

  function scheduleRestore() {
    if (!anchor || frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      restorePosition();
    });
  }

  function preserveTabPosition(tab) {
    const tabset = tab.closest(".panel-tabset");
    const tabBar = tab.closest(".nav-tabs");
    if (!tabset?.hasAttribute("data-group") || !tabBar) return;

    release();
    anchor = { element: tabBar, top: tabBar.getBoundingClientRect().top };
    root.classList.add("tabset-scroll-stabilizing");

    // Charts and images can resize after the click has finished. Observe each
    // preceding tabset as well as the current one: total page height alone may
    // not change if one panel grows while another shrinks.
    if (window.ResizeObserver) {
      observer = new ResizeObserver(scheduleRestore);
      for (const panel of document.querySelectorAll(".panel-tabset")) {
        if (
          panel.contains(tabBar) ||
          (panel.compareDocumentPosition(tabBar) & Node.DOCUMENT_POSITION_FOLLOWING)
        ) {
          observer.observe(panel);
        }
      }
      const content = document.getElementById("quarto-document-content");
      if (content) observer.observe(content);
    }
    scheduleRestore();
  }

  // Capture at window, before Bootstrap's delegated document-capture listener
  // activates this tab and Quarto's target listener synchronizes the others.
  window.addEventListener("click", (event) => {
    release();
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const tab = event.target instanceof Element
      ? event.target.closest('.panel-tabset .nav-tabs [role="tab"]')
      : null;
    if (tab && !tab.classList.contains("active")) preserveTabPosition(tab);
  }, true);

  // The grouped tab changes happen at the target, before this bubbling handler.
  // Correct immediately, then check again before the next paint.
  document.addEventListener("click", () => {
    restorePosition();
    scheduleRestore();
  });

  // Also cover Bootstrap tab activation from the keyboard.
  document.addEventListener("show.bs.tab", (event) => {
    if (!anchor && event.target instanceof Element) preserveTabPosition(event.target);
  }, true);
  document.addEventListener("shown.bs.tab", scheduleRestore);

  // Never keep pulling the reader back after they start scrolling, moving focus,
  // interacting with an exercise, or navigating elsewhere. No scroll events are
  // intercepted; the observer only compensates for layout changes until then.
  for (const type of ["wheel", "touchstart", "pointerdown", "keydown"]) {
    window.addEventListener(type, release, { capture: true, passive: true });
  }
  window.addEventListener("resize", release);
  window.addEventListener("pagehide", release);
})();
