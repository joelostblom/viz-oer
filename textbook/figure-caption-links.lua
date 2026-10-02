-- Quarto's HTML callout processor moves figcaption.childNodes with forEach.
-- Moving a node mutates that live list, skipping alternating children (links
-- and cross-references in particular). Emit one child containing the complete
-- caption, after Quarto has resolved references and rendered its custom AST.
function Blocks(blocks)
  if not quarto.doc.is_format("html") then return nil end

  local result = pandoc.Blocks({})
  local index = 1
  while index <= #blocks do
    local opening = blocks[index]
    local closing = nil
    if opening.t == "RawBlock" and opening.format == "html"
        and opening.text:match("^<figcaption[%s>]") then
      for next_index = index + 1, #blocks do
        local block = blocks[next_index]
        if block.t == "RawBlock" and block.format == "html"
            and block.text:match("^</figcaption>") then
          closing = next_index
          break
        end
      end
    end

    if closing then
      local content = pandoc.Blocks({})
      for caption_index = index + 1, closing - 1 do
        content:insert(blocks[caption_index])
      end
      -- Use a body-only writer, not the document's standalone HTML template.
      local html = pandoc.write(pandoc.Pandoc(content), "html", {
        wrap_text = "none",
        html_math_method = PANDOC_WRITER_OPTIONS.html_math_method
      })
      result:insert(pandoc.RawBlock("html", opening.text
        .. '<div class="figure-caption-content">' .. html
        .. "</div>" .. blocks[closing].text))
      index = closing + 1
    else
      result:insert(opening)
      index = index + 1
    end
  end
  return result
end
