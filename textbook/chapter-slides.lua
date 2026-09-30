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
  local supporting_blocks = pandoc.List()
  local notes = pandoc.List()
  local current_title = nil
  local current_anchor = ""
  local visual_count = 0
  local keep_content_together = false
  local continuation = 0

  local function flush_notes()
    if #notes > 0 then
      output:insert(pandoc.Div(notes, pandoc.Attr("", {"notes"})))
      notes = pandoc.List()
    end
  end

  local function start_slide(title, identifier, chapter_anchor)
    flush_notes()
    current_title = title
    current_anchor = chapter_anchor or identifier or ""
    visual_count = 0
    keep_content_together = false
    -- The shortcuts footer belongs only to Quarto's generated title slide.
    output:insert(pandoc.Header(2, title,
      pandoc.Attr(identifier or "", {}, {
        footer = "false", ["chapter-anchor"] = current_anchor
      })))
  end

  local function capitalize_paragraph(block)
    local found = false
    return block:walk({
      traverse = "topdown",
      Str = function(str)
        if found then return nil end
        for offset, codepoint in utf8.codes(str.text) do
          local char = utf8.char(codepoint)
          local upper = pandoc.text.upper(char)
          if upper ~= pandoc.text.lower(char) then
            str.text = str.text:sub(1, offset - 1) .. upper .. str.text:sub(offset + #char)
            found = true
            return str
          end
        end
      end,
      -- Keep leading identifiers/formulas literal, rather than changing code
      -- or capitalizing the word that follows it (e.g. `x` is a variable).
      Code = function() found = true end,
      Math = function() found = true end,
      Note = function(note) return note, false end,
      Image = function(image) return image, false end
    })
  end

  local function show_text(blocks, capitalize)
    local fragment = pandoc.Div(blocks,
      pandoc.Attr("", {"slide-content", "fragment", "fade-in"}))
    if capitalize then
      local content = pandoc.List()
      local items = pandoc.List()
      local function flush_bullets()
        if #items > 0 then
          content:insert(pandoc.BulletList(items))
          items = pandoc.List()
        end
      end
      for _, block in ipairs(blocks) do
        if block.t == "BulletList" or block.t == "OrderedList" then
          flush_bullets()
          -- Preserve list type, starting number, numbering style, and nesting.
          content:insert(block)
        else
          items:insert(pandoc.List({block}))
        end
      end
      flush_bullets()
      fragment.content = content
      -- walk returns a transformed copy, preserving the chapter/notes wording.
      fragment = fragment:walk({Para = capitalize_paragraph, Plain = capitalize_paragraph})
    end
    output:insert(fragment)
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

  local function highlighted_notes(block)
    local function emphasize(inlines)
      -- Avoid double-bold markup when an excerpt already contains emphasis.
      local content = pandoc.Span(inlines):walk({
        Strong = function(strong) return strong.content end
      }).content
      return pandoc.Strong(content)
    end
    local function emphasize_paragraph(paragraph)
      paragraph.content = pandoc.Inlines({emphasize(paragraph.content)})
      return paragraph
    end
    -- Transform only the notes copy. Semantic bold also works in Reveal's
    -- separate speaker window, which does not inherit our slide stylesheet.
    local wrapper = pandoc.Div({block}):walk({
      traverse = "topdown",
      Div = function(div)
        if div.classes:includes("slide-text") then
          return div:walk({Para = emphasize_paragraph, Plain = emphasize_paragraph}), false
        end
      end,
      Span = function(span)
        if span.classes:includes("slide-text") then
          span.content = pandoc.Inlines({emphasize(span.content)})
          return span, false
        end
      end
    })
    -- Keep explanatory footnotes inside the notes instead of letting Reveal
    -- collect them into visible footers on otherwise heading-only slides.
    return wrapper.content[1]:walk({
      Note = function(note)
        local text = pandoc.Inlines({pandoc.Str("(")})
        text:extend(pandoc.utils.blocks_to_inlines(note.content))
        text:insert(pandoc.Str(")"))
        return pandoc.Span(text)
      end
    })
  end

  local function process_blocks(blocks, parent_anchor)
    for _, block in ipairs(blocks) do
      if block.t == "Div" and (block.classes:includes("hidden")
          or block.classes:includes("quarto-auto-generated-content")) then
        -- Preserve Quarto's hidden payload containers (including the footer)
        -- for its later rendering passes instead of flattening them into notes.
        supporting_blocks:insert(block)
      elseif block.t == "Header" then
        if block.classes:includes("slide-skip") then
          -- Omit this heading and its slide break, not the following content.
        elseif block.classes:includes("slide-fragment") and current_title then
          local heading = block:clone()
          heading.level = 3 -- Below slide-level, so it cannot start a slide.
          heading.classes:extend({"slide-heading", "fragment", "fade-in"})
          output:insert(heading)
          -- A leading Header makes Pandoc render this notes Div as a visible
          -- section instead of Reveal's hidden aside. Use a label instead.
          notes:insert(pandoc.Para({pandoc.Strong(block.content)}))
          visual_count = 0
          keep_content_together = true
        else
          start_slide(block.content, block.identifier, parent_anchor)
        end
      elseif block.t == "Div" and block.classes:includes("slide-outcomes") then
        start_slide("Learning outcomes", "learning-outcomes", "")
        show_text(block.content)
      elseif block.t == "Div" and block.classes:includes("slide-text") then
        if not current_title then
          start_slide("Introduction", "introduction", "")
        end
        show_text(block.content, true)
        notes:insert(highlighted_notes(block))
      elseif block.t == "Div" and (block.classes:includes("slide-visual")
          or block.classes:includes("slide-fragment")) then
        local title = block.attributes["slide-title"]
        local same_slide = block.classes:includes("slide-fragment")
        if same_slide then
          if not current_title then
            start_slide("Visualization", "visualization", "")
          end
          if title then
            block.content:insert(1, pandoc.Header(3, {pandoc.Str(title)},
              pandoc.Attr("", {"slide-heading"})))
          end
        elseif title then
          continuation = continuation + 1
          start_slide(title, "visualization-continued-" .. continuation, current_anchor)
        elseif not current_title then
          start_slide("Visualization", "visualization", "")
        elseif visual_count > 0 and not keep_content_together then
          continuation = continuation + 1
          start_slide(current_title, "visualization-continued-" .. continuation, current_anchor)
        end
        local code_chart = block.classes:includes("slide-code-chart")
        block.classes = pandoc.List({"slide-media", "fragment", "fade-in"})
        if code_chart then block.classes:insert("slide-code-chart") end
        output:insert(block)
        visual_count = visual_count + 1
      elseif block.t == "Div" then
        -- Flatten exercise callouts, margin notes, and tabsets. Their selected
        -- visuals become slides, not hidden content inside a callout or tab.
        for _, entry in ipairs({{"ex-prompt", "Exercise"}, {"ex-hint", "Hint"}, {"ex-solution", "Solution"}}) do
          if current_title and block.classes:includes(entry[1]) then
            notes:insert(pandoc.Para({pandoc.Strong({pandoc.Str(entry[2])})}))
          end
        end
        -- Return from nested slides to a visible outer section in the chapter,
        -- rather than an anchor inside a collapsed solution or inactive tab.
        process_blocks(block.content, parent_anchor or current_anchor)
      elseif current_title then
        for _, selection in ipairs(selected_spans(block)) do
          show_text({selection}, true)
        end
        notes:insert(highlighted_notes(block))
      end
    end
  end
  process_blocks(doc.blocks)
  flush_notes()
  output:extend(supporting_blocks)
  doc.blocks = output
  doc.meta.toc = false
  doc.meta["number-sections"] = false
  return doc
end
