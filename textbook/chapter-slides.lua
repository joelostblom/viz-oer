-- Keep chapter prose in the book; select headings and visuals for Reveal.js.
function Pandoc(doc)
  if not doc.meta["chapter-slides"] then
    return doc
  end
  if not quarto.doc.is_format("revealjs") then
    if quarto.doc.is_format("html") then
      local url = pandoc.utils.stringify(doc.meta["chapter-slides"])
      local icon = pandoc.RawInline("html", [[<svg xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
        <rect x="3" y="3" width="18" height="13" rx="1"/>
        <path d="M12 16v5m-4 0h8m-9-10 3-4 3 2 3-3"/>
        </svg>]])
      local link = pandoc.Link({icon}, url, "Present slides",
        pandoc.Attr("", {"chapter-present-link"}, {["aria-label"] = "Present slides", hidden = ""}))
      doc.blocks:insert(1, pandoc.Div({pandoc.Plain({link})},
        pandoc.Attr("", {"chapter-slide-link"})))
    end
    return doc
  end

  local output = pandoc.List()
  local notes = pandoc.List()
  local current_title = nil
  local visual_count = 0
  local continuation = 0

  local function flush_notes()
    if #notes > 0 then
      output:insert(pandoc.Div(notes, pandoc.Attr("", {"notes"})))
      notes = pandoc.List()
    end
  end

  local function start_slide(title, identifier)
    flush_notes()
    current_title = title
    visual_count = 0
    output:insert(pandoc.Header(2, title, pandoc.Attr(identifier or "")))
  end

  local function show_text(blocks)
    output:insert(pandoc.Div(blocks,
      pandoc.Attr("", {"slide-content", "fragment", "fade-in"})))
  end

  local function selected_spans(block)
    local selections = pandoc.List()
    block:walk({
      traverse = "topdown",
      Span = function(span)
        if span.classes:includes("slide-text") then
          selections:insert(pandoc.Para(span.content))
          -- Nested selections belong to the same fragment, not a duplicate.
          return span, false
        end
      end
    })
    return selections
  end

  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" then
      start_slide(block.content, block.identifier)
    elseif block.t == "Div" and block.classes:includes("slide-outcomes") then
      start_slide("Learning outcomes", "learning-outcomes")
      show_text(block.content)
    elseif block.t == "Div" and block.classes:includes("slide-text") then
      if not current_title then
        start_slide("Introduction", "introduction")
      end
      show_text(block.content)
      notes:insert(block)
    elseif block.t == "Div" and block.classes:includes("slide-visual") then
      if not current_title then
        start_slide("Visualization", "visualization")
      elseif visual_count > 0 then
        -- Give multiple visual blocks separate slides rather than overflowing.
        continuation = continuation + 1
        start_slide(current_title, "visualization-continued-" .. continuation)
      end
      block.classes = pandoc.List({"slide-media", "fragment", "fade-in"})
      output:insert(block)
      visual_count = visual_count + 1
    elseif current_title then
      for _, selection in ipairs(selected_spans(block)) do
        show_text({selection})
      end
      -- Retain the full paragraph as notes, including the selected excerpt.
      notes:insert(block)
    end
  end
  flush_notes()
  doc.blocks = output
  doc.meta.toc = false
  doc.meta["number-sections"] = false
  return doc
end
