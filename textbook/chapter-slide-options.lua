-- Resolve heading format conditions in both views before Quarto builds sections.
-- For slides, also preserve tab-heading annotations before tabset processing.
function Header(heading)
  local show = heading.classes:includes("content-visible")
  local hide = heading.classes:includes("content-hidden")
  local when = heading.attributes["when-format"]
  local unless = heading.attributes["unless-format"]
  if not (show or hide) or not (when or unless) then return nil end

  local matches = (not when or quarto.doc.is_format(when))
    and (not unless or not quarto.doc.is_format(unless))
  local visible = show and matches or (not show and not matches)
  -- Remove only the heading, never the following section content.
  if not visible then return pandoc.List() end

  -- Consumed conditions must not later hide a generated slide section.
  heading.classes = heading.classes:filter(function(class)
    return class ~= "content-visible" and class ~= "content-hidden"
  end)
  heading.attributes["when-format"] = nil
  heading.attributes["unless-format"] = nil
  return heading
end

function Div(div)
  if quarto.doc.is_format("revealjs") and (div.classes:includes("deep-dive")
      or div.classes:includes("column-margin") or div.classes:includes("slide-skip")) then
    -- Drop the entire optional section before callout processing or selection,
    -- including nested slide annotations and material destined for notes.
    return pandoc.List()
  end
  if quarto.doc.is_format("revealjs") and div.classes:includes("slide-outcomes") then
    -- The slide supplies its own heading. Unpack the book's note before
    -- Quarto converts its title and border into a second, nested callout.
    return div:walk({Div = function(note)
      if note.classes:includes("callout-note") then
        local content = note.content
        if content[1] and content[1].t == "Header" then content:remove(1) end
        return content
      end
    end})
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
    div.classes = div.classes:filter(function(class)
      return class ~= "panel-tabset" and class ~= "slide-tabset"
    end)
    div.classes:insert("slide-tabs")
    if not div.classes:includes("slide-tabset-flat")
        and not div.classes:includes("slide-columns")
        and not div.classes:includes("slide-comparison") then
      div.classes:insert("slide-tabset")
    end
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
