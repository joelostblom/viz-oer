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

  -- The book takes its title from the chapter's H1. Reuse that heading as
  -- Reveal's title metadata, rather than adding a duplicate content slide.
  for index, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 then
      doc.meta.title = pandoc.MetaInlines(block.content)
      doc.meta.pagetitle = pandoc.utils.stringify(block.content)
      doc.blocks:remove(index)
      break
    end
  end

  local output = pandoc.List()
  local supporting_blocks = pandoc.List()
  local notes = pandoc.List()
  local current_title = nil
  local current_anchor = ""
  local visual_count = 0
  local keep_content_together = false
  local reveal_with_heading = false
  local reveal_group = 0
  local continuation = 0
  local current_slide_index = nil

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
    reveal_with_heading = false
    -- The shortcuts footer belongs only to Quarto's generated title slide.
    output:insert(pandoc.Header(2, title,
      pandoc.Attr(identifier or "", {}, {
        footer = "false", ["chapter-anchor"] = current_anchor
      })))
    current_slide_index = #output
  end

  local function reveal_title_with_content()
    reveal_group = reveal_group + 1
    local heading = output[current_slide_index]
    -- Header attributes belong to the slide section in Reveal; animate an
    -- inner span so only the title shares the content's reveal step.
    heading.content = pandoc.Inlines({pandoc.Span(heading.content,
      pandoc.Attr("", {"fragment", "fade-in"},
        {["slide-reveal-group"] = tostring(reveal_group)}))})
    reveal_with_heading = reveal_group
  end

  local function set_columns(heading, block)
    heading.attributes["slide-columns"] = "true"
    local widths = block.attributes["slide-widths"]
    if widths then
      local first, second = widths:match("^%s*([%d%.]+)%s*,%s*([%d%.]+)%s*$")
      local left, right = tonumber(first), tonumber(second)
      if not left or not right or left <= 0 or right <= 0
          or left == math.huge or right == math.huge then
        error('slide-widths must contain two positive numbers, e.g. slide-widths="40,60"')
      end
      heading.attributes["style"] = string.format(
        "--slide-left-width: %gfr; --slide-right-width: %gfr;", left, right)
    end
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

  local function text_fragment(blocks, capitalize)
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
    return fragment
  end

  local function show_text(blocks, capitalize)
    local fragment = text_fragment(blocks, capitalize)
    if reveal_with_heading then
      fragment.attributes["slide-reveal-group"] = tostring(reveal_with_heading)
      reveal_with_heading = false
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
          reveal_with_heading = false
          if block.classes:includes("slide-with-content") then
            reveal_group = reveal_group + 1
            heading.attributes["slide-reveal-group"] = tostring(reveal_group)
            reveal_with_heading = reveal_group
          end
          output:insert(heading)
          -- A leading Header makes Pandoc render this notes Div as a visible
          -- section instead of Reveal's hidden aside. Use a label instead.
          notes:insert(pandoc.Para({pandoc.Strong(block.content)}))
          visual_count = 0
          keep_content_together = true
        else
          start_slide(block.content, block.identifier, parent_anchor)
          if block.classes:includes("slide-with-content") then
            reveal_title_with_content()
          end
        end
      elseif block.t == "Div" and block.classes:includes("slide-outcomes") then
        start_slide("Learning outcomes", "learning-outcomes", "")
        local excerpts = selected_spans(block)
        if #excerpts > 0 then
          show_text(excerpts, true)
          notes:insert(highlighted_notes(block))
        else
          show_text(block.content)
        end
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
            local heading = pandoc.Header(3, {pandoc.Str(title)},
              pandoc.Attr("", {"slide-heading"}))
            if output[current_slide_index].attributes["slide-columns"] then
              -- Align the second title with the first column's heading while
              -- retaining a single reveal step for this title and its content.
              reveal_group = reveal_group + 1
              heading.classes:extend({"fragment", "fade-in"})
              heading.attributes["slide-reveal-group"] = tostring(reveal_group)
              reveal_with_heading = reveal_group
              output:insert(heading)
            else
              block.content:insert(1, heading)
            end
          end
        elseif title then
          continuation = continuation + 1
          start_slide(title, "visualization-continued-" .. continuation, current_anchor)
          if block.classes:includes("slide-with-content") then
            reveal_title_with_content()
          end
        elseif not current_title then
          start_slide("Visualization", "visualization", "")
        elseif visual_count > 0 and not keep_content_together then
          continuation = continuation + 1
          start_slide(current_title, "visualization-continued-" .. continuation, current_anchor)
        end
        if block.classes:includes("slide-columns")
            or block.classes:includes("slide-comparison") then
          set_columns(output[current_slide_index], block)
        end
        -- Keep nested text selections' bullet formatting, but let the outer
        -- visual own their animation so heading and text reveal together.
        block = block:walk({Div = function(div)
          if div.classes:includes("slide-text") then
            notes:insert(highlighted_notes(div))
            local text = text_fragment(div.content, true)
            text.classes = pandoc.List({"slide-content"})
            return text
          end
        end})
        block.classes = pandoc.List({"slide-media", "fragment", "fade-in"})
        if reveal_with_heading then
          block.attributes["slide-reveal-group"] = tostring(reveal_with_heading)
          reveal_with_heading = false
        end
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
        local first_output = #output + 1
        process_blocks(block.content, parent_anchor or current_anchor)
        if block.classes:includes("slide-columns")
            or block.classes:includes("slide-comparison") then
          for index = first_output, #output do
            if output[index].t == "Header" and output[index].level == 2 then
              set_columns(output[index], block)
              break
            end
          end
        end
      elseif current_title then
        for _, selection in ipairs(selected_spans(block)) do
          show_text({selection}, true)
        end
        notes:insert(highlighted_notes(block))
      end
    end
  end
  -- A nested fragment holds all results from a cell, so its source can be
  -- discussed before revealing the answer. This pass also handles cells
  -- selected inside a larger .slide-visual wrapper.
  doc = doc:walk({Div = function(div)
    local option = div.attributes["slide-output-fragment"]
      or div.attributes["data-slide-output-fragment"]
    if option ~= "true" then return nil end
    local content = pandoc.List()
    local results = pandoc.List()
    for _, child in ipairs(div.content) do
      if child.t == "Div" and (child.classes:includes("cell-output")
          or child.classes:includes("cell-output-display")) then
        results:insert(child)
      else
        content:insert(child)
      end
    end
    if #results > 0 then
      content:insert(pandoc.Div(results,
        pandoc.Attr("", {"fragment", "fade-in", "slide-answer"})))
      div.content = content
      return div
    end
  end})
  process_blocks(doc.blocks)
  flush_notes()
  output:extend(supporting_blocks)
  doc.blocks = output
  -- Assign every fragment in reading order, sharing an index only for a
  -- heading/content pair. Multiple pairs on one slide must remain separate.
  local fragment_index = 0
  local group_indices = {}
  local function index_fragment(element)
    if element.classes:includes("fragment") then
      local group = element.attributes["slide-reveal-group"]
      local index = group and group_indices[group]
      if index == nil then
        index = fragment_index
        fragment_index = fragment_index + 1
        if group then group_indices[group] = index end
      end
      element.attributes["fragment-index"] = tostring(index)
      element.attributes["slide-reveal-group"] = nil
      return element
    end
  end
  doc = doc:walk({
    traverse = "topdown",
    Header = function(heading)
      if heading.level == 2 then
        fragment_index = 0
        group_indices = {}
      end
      return index_fragment(heading)
    end,
    Div = function(div)
      if div.classes:includes("notes") then return div, false end
      return index_fragment(div)
    end,
    Span = index_fragment
  })
  doc.meta.toc = false
  doc.meta["number-sections"] = false
  return doc
end
