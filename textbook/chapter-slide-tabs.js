// Coordinate Quarto's native tabs with Reveal's navigation and PDF export.
(() => {
  const query = new URLSearchParams(location.search);
  const printing = query.get("view") === "print" || query.has("print-pdf");
  const languages = new Map();
  let restoring = false;
  let installed = false;

  const directTabs = (widget) => [...widget.querySelectorAll(':scope > [role="tablist"] [role="tab"]')];
  const directPanels = (widget) => [...widget.querySelectorAll(':scope > .tab-content > [role="tabpanel"]')];

  function cloneWithCanvases(node) {
    const copy = node.cloneNode(true);
    const original = node.querySelectorAll("canvas");
    copy.querySelectorAll("canvas").forEach((canvas, index) => {
      canvas.getContext("2d").drawImage(original[index], 0, 0);
    });
    return copy;
  }

  function printVariants(page, choices = new Map(), labels = []) {
    const widget = [...page.querySelectorAll(".panel-tabset")]
      .find(tabset => !tabset.closest("aside.notes"));
    if (!widget) return [{page, labels}];
    const tabs = directTabs(widget);
    const panels = directPanels(widget);
    if (!panels.length) return [{page, labels}];
    const group = widget.dataset.group;
    const preferred = group && choices.get(group);
    const matched = preferred && tabs.some(tab => tab.textContent.trim() === preferred);
    const variants = [];
    panels.forEach((pane, index) => {
      const label = tabs[index].textContent.trim();
      if (matched && preferred !== label) return;
      const copy = cloneWithCanvases(page);
      const target = [...copy.querySelectorAll(".panel-tabset")]
        .find(tabset => !tabset.closest("aside.notes"));
      const selected = directPanels(target)[index];
      selected.hidden = false;
      selected.removeAttribute("role");
      selected.removeAttribute("aria-labelledby");
      selected.classList.add("slide-tab-print-content");
      target.replaceWith(selected);
      const next = new Map(choices);
      if (group) next.set(group, label);
      variants.push(...printVariants(copy, next, labels.includes(label) ? labels : [...labels, label]));
    });
    return variants;
  }

  function uniqueIds(node, prefix) {
    const ids = new Map();
    node.querySelectorAll("[id]").forEach(element => {
      ids.set(element.id, prefix + element.id);
      element.id = prefix + element.id;
    });
    node.querySelectorAll("*").forEach(element => {
      for (const attr of [...element.attributes]) {
        let value = attr.value.replace(/url\(#([^)]*)\)/g, (match, id) => ids.has(id) ? `url(#${ids.get(id)})` : match);
        if (["href", "xlink:href"].includes(attr.name) && value.startsWith("#") && ids.has(value.slice(1))) {
          value = "#" + ids.get(value.slice(1));
        } else if (["aria-labelledby", "aria-describedby", "aria-controls", "for"].includes(attr.name)) {
          value = value.split(" ").map(id => ids.get(id) || id).join(" ");
        }
        if (value !== attr.value) element.setAttribute(attr.name, value);
      }
    });
  }

  async function expandPrintTabs(deck) {
    if (document.documentElement.dataset.slideTabsPrint) return;
    document.documentElement.dataset.slideTabsPrint = "preparing";
    if (document.readyState !== "complete") await new Promise(resolve => window.addEventListener("load", resolve, {once: true}));
    await document.fonts.ready;
    await Promise.all([...document.images].map(image => image.decode().catch(() => {})));
    // Vega paints asynchronously; preserve its rendered canvas when cloning pages.
    await new Promise(requestAnimationFrame);
    await new Promise(requestAnimationFrame);
    let variantId = 0;
    const added = [];
    document.querySelectorAll(".pdf-page").forEach(page => {
      if (!page.querySelector(".panel-tabset")) return;
      const variants = printVariants(page);
      variants.forEach(({page: copy, labels}) => {
        const slide = copy.querySelector("section");
        if (labels.length) {
          const label = document.createElement("p");
          label.className = "slide-tab-print-label";
          label.textContent = labels.join(" / ");
          const heading = slide.querySelector(":scope > h1, :scope > h2");
          if (heading) heading.after(label);
          else slide.prepend(label);
        }
        uniqueIds(copy, `tab-print-${++variantId}-`);
        added.push(copy);
      });
      page.replaceWith(...variants.map(variant => variant.page));
    });
    await new Promise(requestAnimationFrame);
    added.forEach(page => {
      const slide = page.querySelector("section");
      const height = parseFloat(page.style.height);
      const padding = 2 * parseFloat(slide.style.top || 0);
      const count = Math.max(1, Math.ceil((slide.scrollHeight + padding) / height));
      page.style.height = `${height * Math.min(count, deck.getConfig().pdfMaxPagesPerSlide || count)}px`;
    });
    document.querySelectorAll(".pdf-page .slide-number-pdf").forEach((number, index) => {
      number.textContent = String(index + 1);
    });
    document.documentElement.dataset.slideTabsPrint = "ready";
  }

  function install() {
    const deck = window.Reveal;
    if (!deck || installed) return;
    installed = true;
    if (printing) {
      deck.on("pdf-ready", () => expandPrintTabs(deck));
      if (document.querySelector(".pdf-page")) expandPrintTabs(deck);
      return;
    }

    const initialize = () => {
      let teaching = new WeakMap();
      let revealed = new WeakMap();
      let pointerTab = null;
      document.querySelectorAll('.panel-tabset [role="tabpanel"] .fragment').forEach(fragment => {
        fragment.classList.add("tabset-reveal");
        fragment.dataset.tabsetIndex = fragment.dataset.fragmentIndex || "0";
      });
      const teachingPath = (element) => {
        let pane = element.closest('[role="tabpanel"]');
        while (pane) {
          const state = teaching.get(pane.closest(".panel-tabset"));
          if (pane.hidden || state?.pane !== pane) return false;
          pane = pane.parentElement.closest('[role="tabpanel"]');
        }
        return true;
      };
      const rememberReveals = () => {
        deck.getCurrentSlide()?.querySelectorAll(".fragment").forEach(fragment => {
          revealed.set(fragment, fragment.classList.contains("visible"));
        });
      };
      const lockTeaching = (fragment) => {
        let pane = fragment.closest('[role="tabpanel"]');
        while (pane) {
          const widget = pane.closest(".panel-tabset");
          const state = teaching.get(widget);
          if (state?.pane === pane) {
            state.locked = true;
            const label = directTabs(widget).find(tab => tab.hash === "#" + pane.id);
            if (widget.dataset.group && label) languages.set(widget.dataset.group, label.textContent.trim());
          }
          pane = pane.parentElement.closest('[role="tabpanel"]');
        }
      };
      const synchronize = () => {
        const slide = deck.getCurrentSlide();
        if (!slide) return;
        slide.querySelectorAll(".tabset-reveal").forEach(fragment => {
          const active = teachingPath(fragment);
          fragment.classList.toggle("fragment", active);
          if (active) fragment.dataset.fragmentIndex = fragment.dataset.tabsetIndex;
          else fragment.classList.remove("visible", "current-fragment");
        });
        deck.syncFragments(slide);
        // Restore the teaching fragments, rather than copying a preview's cursor.
        const visible = [...slide.querySelectorAll(".fragment")].filter(fragment => revealed.get(fragment));
        const progress = visible.length ? Math.max(...visible.map(fragment => Number(fragment.dataset.fragmentIndex))) : -1;
        deck.navigateFragment(progress);
        deck.layout();
      };
      const enter = () => {
        restoring = true;
        teaching = new WeakMap();
        revealed = new WeakMap();
        const slide = deck.getCurrentSlide();
        slide.querySelectorAll(".panel-tabset").forEach(widget => {
          const preferred = languages.get(widget.dataset.group);
          const link = directTabs(widget).find(tab => tab.textContent.trim() === preferred);
          if (link && link.getAttribute("aria-selected") !== "true") link.click();
          teaching.set(widget, {pane: directPanels(widget).find(pane => !pane.hidden), locked: false});
        });
        restoring = false;
        synchronize();
        // Restoring a language is programmatic, not a request to focus tab controls.
        if (document.activeElement.matches?.('[role="tab"]')) document.activeElement.blur();
      };
      document.addEventListener("tabby", event => {
        if (restoring) return;
        const link = event.detail.tab;
        const widget = link.closest(".panel-tabset");
        if (!deck.getCurrentSlide().contains(widget)) return;
        rememberReveals();
        const state = teaching.get(widget);
        if (state && !state.locked && teachingPath(widget)) {
          state.pane = event.detail.content;
          if (widget.dataset.group) languages.set(widget.dataset.group, link.textContent.trim());
        }
        synchronize();
        window.dispatchEvent(new Event("resize"));
      });
      document.addEventListener("pointerdown", event => {
        pointerTab = event.target.closest?.('[role="tab"]') || null;
      }, true);
      document.addEventListener("click", event => {
        const tab = event.target.closest?.('[role="tab"]');
        if (!tab || tab !== pointerTab) return;
        pointerTab = null;
        // Tabby focuses clicked links. After a pointer click, arrows should
        // advance the presentation; deliberate keyboard focus still owns them.
        queueMicrotask(() => { if (document.activeElement === tab) tab.blur(); });
      }, true);
      document.addEventListener("keydown", event => {
        const link = event.target.closest?.('[role="tab"]');
        if (!link || event.ctrlKey || event.metaKey || event.altKey
            || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        const tabs = [...link.closest('[role="tablist"]').querySelectorAll('[role="tab"]')];
        const index = tabs.indexOf(link);
        const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1
          : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
        tabs[next].click();
        tabs[next].focus();
      }, true);
      deck.on("slidechanged", enter);
      deck.on("fragmentshown", event => {
        (event.fragments || [event.fragment]).forEach(lockTeaching);
        rememberReveals();
      });
      deck.on("fragmenthidden", rememberReveals);
      enter();
    };
    // Tabby assigns its roles on DOMContentLoaded; wait for those handlers too.
    if (deck.isReady()) requestAnimationFrame(initialize);
    else deck.on("ready", () => requestAnimationFrame(initialize));
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", install, {once: true});
  else install();
})();
