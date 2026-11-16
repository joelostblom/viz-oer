local exercise_counter = 0 -- Global counter for exercises

local function deep_dive_title(div)
  local title = pandoc.Inlines({pandoc.Str("Deep"), pandoc.Space(), pandoc.Str("dive")})
  local promoted = {}
  -- Only inspect direct headings, not labels inside nested tabs or exercises.
  for index, block in ipairs(div.content) do
    if block.t == "Header" then
      promoted[#promoted + 1] = index
      local label = pandoc.text.lower(pandoc.utils.stringify(block.content))
      local generic = label == "deep dive" or label == ""
      if not generic then
        title:insert(pandoc.Str(":"))
        title:insert(pandoc.Space())
      end
      local content = generic and pandoc.Inlines({}) or block.content
      if block.identifier ~= "" then
        -- Keep heading links on the visible title, outside the collapsed body.
        title:insert(pandoc.Span(content, pandoc.Attr(block.identifier)))
      else
        title:extend(content)
      end
      if not generic then break end
    end
  end
  for index = #promoted, 1, -1 do
    div.content:remove(promoted[index])
  end
  return title
end

function Div(div)
  if div.classes:includes("ex-prompt") then
    exercise_counter = exercise_counter + 1
    local numbered_title = "Exercise " .. exercise_counter

    -- return a callout instead of the Div
    return quarto.Callout({
      type = "ex-prompt",
      title = numbered_title,
      collapse = false,
      icon = false,
      content = { div },
    })
  end

  if div.classes:includes("ex-solution") then
    return quarto.Callout({
      type = "ex-solution",
      title = "Solution",
      collapse = true,
      icon = false,
      content = { div },
    })
  end

  if div.classes:includes("ex-hint") then
    return quarto.Callout({
      type = "ex-hint",
      title = "Hint",
      collapse = true,
      icon = false,
      content = { div },
    })
  end

  if div.classes:includes("deep-dive") then
    return quarto.Callout({
      type = "deep-dive",
      title = deep_dive_title(div),
      collapse = true,
      icon = false,
      content = { div },
    })
  end
end
