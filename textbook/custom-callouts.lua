local exercise_counter = 0  -- Global counter for exercises

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
end
