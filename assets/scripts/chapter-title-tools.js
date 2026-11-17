// Keep the presentation action beside the title without changing title metadata.
(() => {
  const placePresentationLink = () => {
    const container = document.querySelector(".chapter-slide-link");
    const title = document.querySelector("#title-block-header h1.title");
    const link = container?.querySelector(".chapter-present-link");
    if (!title || !link) return;

    const row = document.createElement("div");
    row.className = "chapter-title-row";
    title.before(row);
    row.append(title, link);
    link.hidden = false;
    container.remove();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", placePresentationLink, { once: true });
  } else {
    placePresentationLink();
  }
})();
