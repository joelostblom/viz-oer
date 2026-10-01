-- Knitr omits source blocks when echo is false. Disable Vega's action menu
-- for those illustrative charts before embedding, keeping sliders/tooltips.
function Div(div)
  if not div.classes:includes("cell") then return nil end

  local has_code = false
  div:walk({CodeBlock = function(block)
    if block.classes:includes("cell-code")
        or block.classes:includes("pyodide")
        or block.classes:includes("webr") then
      has_code = true
    end
  end})
  if has_code then return nil end

  return div:walk({RawBlock = function(block)
    if block.format ~= "html" then return nil end
    -- Altair's to_html() emits its embed options as one JSON declaration.
    block.text = block.text:gsub("(\n%s*var%s+embedOpt%s*=%s*)([^\n]+);",
      function(prefix, json)
        local options = quarto.json.decode(json)
        options.actions = false
        return prefix .. quarto.json.encode(options) .. ";"
      end)
    return block
  end})
end
