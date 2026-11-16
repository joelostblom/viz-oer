// Quarto relocates callout captions into the margin beside the whole callout.
// Keep their text aligned with the actual figure, including after resizing or
// expanding an exercise. Normal figure captions retain Quarto's own layout.
(() => {
  const initialize = () => {
    const captions = document.querySelectorAll(
      'figcaption.quarto-float-fig, .margin-figure-caption'
    );
    for (const caption of captions) {
      if (caption.querySelector('.figure-caption-label')) continue;
      const walker = document.createTreeWalker(caption, NodeFilter.SHOW_TEXT);
      let text;
      while ((text = walker.nextNode()) && !text.textContent.trim()) {}
      if (!text) continue;
      const match = text.textContent.match(/^\s*(Figure\s+[^\s:]+):\s*/u);
      if (!match) continue;
      const label = document.createElement('strong');
      label.className = 'figure-caption-label';
      label.textContent = match[1];
      text.textContent = text.textContent.slice(match[0].length);
      text.before(label);
    }

    const relocated = [...document.querySelectorAll('.margin-figure-caption[id]')]
      .map(caption => ({caption, figure: document.getElementById(caption.id.replace(/-caption$/, ''))}))
      .filter(({figure}) => figure);
    // Multiple captions following one callout otherwise occupy separate grid
    // rows: the second starts below the entire callout. Give them a single
    // margin column, keeping each caption's collapse classes and accessible ID.
    const calloutCaptions = new Map();
    for (const entry of relocated) {
      let owner = entry.figure;
      while (owner && owner.parentElement !== entry.caption.parentElement) {
        owner = owner.parentElement;
      }
      if (!owner?.matches('.callout')) continue;
      if (!calloutCaptions.has(owner)) calloutCaptions.set(owner, []);
      calloutCaptions.get(owner).push(entry.caption);
    }
    for (const captions of calloutCaptions.values()) {
      if (captions.length < 2) continue;
      const column = document.createElement('div');
      column.className = 'column-margin figure-caption-group';
      captions[0].before(column);
      for (const caption of captions) {
        caption.classList.remove('column-margin');
        column.append(caption);
      }
    }
    const layout = () => {
      for (const {caption, figure} of relocated) {
        caption.classList.add('figure-caption-positioned');
        caption.hidden = figure.getClientRects().length === 0;
        if (caption.hidden) continue;
        const current = parseFloat(caption.style.paddingTop) || 0;
        const captionBox = caption.getBoundingClientRect();
        const figureBox = figure.getBoundingClientRect();
        // Quarto can retain a right margin below the sidebar's 992px
        // breakpoint. Use the rendered geometry, including reader mode.
        const besideFigure = captionBox.left >= figureBox.right - 1;
        const desired = besideFigure
          ? Math.max(0, figureBox.top - captionBox.top)
          : 0;
        if (Math.abs(current - desired) > 0.5) caption.style.paddingTop = `${desired}px`;
      }
    };
    let pending = false;
    const schedule = () => {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        layout();
      });
    };
    if (relocated.length) {
      const observer = new ResizeObserver(schedule);
      observer.observe(document.body);
      for (const {figure} of relocated) observer.observe(figure);
      window.addEventListener('resize', schedule);
      document.addEventListener('load', schedule, true);
      for (const event of ['shown.bs.collapse', 'hidden.bs.collapse', 'shown.bs.tab']) {
        document.addEventListener(event, schedule);
      }
      document.fonts?.ready.then(schedule);
      schedule();
    }
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, {once: true});
  } else {
    initialize();
  }
})();
