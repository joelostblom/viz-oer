function Div(div)
  if div.classes:includes("ex-prompt") then
    -- return a callout instead of the Div
    return quarto.Callout({
      type = "ex-prompt",
      title = "Exercise",
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
end
