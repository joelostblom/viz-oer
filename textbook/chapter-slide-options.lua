-- Run before Quarto turns tabsets into custom nodes, which discard attributes
-- on tab headings. Preserve those headings (including .slide-fragment) for the
-- later slide-selection filter. The textbook render does not use this filter.
function Div(div)
  if quarto.doc.is_format("revealjs") and (div.classes:includes("deep-dive")
      or div.classes:includes("column-margin") or div.classes:includes("slide-skip")) then
    -- Drop the entire optional section before callout processing or selection,
    -- including nested slide annotations and material destined for notes.
    return pandoc.List()
  end
  if quarto.doc.is_format("revealjs") and div.classes:includes("callout-warning") then
    -- Callout parsing consumes a leading Header as the box title. Preserve it
    -- as a normal heading for slide selection, without changing book callouts.
    div.classes = div.classes:filter(function(class)
      return class ~= "callout" and not class:match("^callout%-")
    end)
    div.classes:insert("slide-warning")
    local title = div.attributes["title"]
    if title and title ~= "" then
      div.content:insert(1, pandoc.Header(3,
        pandoc.utils.blocks_to_inlines(pandoc.read(title, "markdown").blocks)))
      div.attributes["title"] = nil
    end
    return div
  end
  if quarto.doc.is_format("revealjs") and div.classes:includes("panel-tabset") then
    div.classes = div.classes:filter(function(class) return class ~= "panel-tabset" end)
    div.classes:insert("slide-tabs")
    return div
  end
end

local references = nil
function Cite(cite)
  if not quarto.doc.is_format("revealjs") or #cite.citations ~= 1 then return nil end
  if references == nil then
    local file = io.open("slide-references.json", "r")
    references = file and quarto.json.decode(file:read("*a")) or {}
    if file then file:close() end
  end
  local reference = references[cite.citations[1].id]
  if reference then
    return pandoc.Link({pandoc.Str(reference.text)}, reference.url)
  end
end
