-- Run before Quarto turns tabsets into custom nodes, which discard attributes
-- on tab headings. Preserve those headings (including .slide-fragment) for the
-- later slide-selection filter. The textbook render does not use this filter.
function Div(div)
  if quarto.doc.is_format("revealjs") and (div.classes:includes("deep-dive")
      or div.classes:includes("column-margin")) then
    -- Drop the entire optional section before callout processing or selection,
    -- including nested slide annotations and material destined for notes.
    return pandoc.List()
  end
  if quarto.doc.is_format("revealjs") and div.classes:includes("panel-tabset") then
    div.classes = div.classes:filter(function(class) return class ~= "panel-tabset" end)
    div.classes:insert("slide-tabs")
    return div
  end
end
