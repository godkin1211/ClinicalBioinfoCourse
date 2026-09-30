-- Handouts live in lessons/, generated Typst in tmp/pdfs/, PDFs in output/pdf/.
-- Typst absolute resource paths are relative to the configured project root.
function Image(image)
  if not image.src:match("^%a[%w+.-]*:") and not image.src:match("^/") then
    if image.src:sub(1, 3) == "../" then
      image.src = "/" .. image.src:sub(4)
    else
      image.src = "/lessons/" .. image.src
    end
  end
  return image
end

function Link(link)
  if not link.target:match("^%a[%w+.-]*:")
      and not link.target:match("^[/#]") then
    if link.target:sub(1, 3) == "../" then
      link.target = "../../" .. link.target:sub(4)
    else
      link.target = "../../lessons/" .. link.target
    end
  end
  return link
end
