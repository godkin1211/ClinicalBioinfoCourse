"""Audit Lesson 03 PDF content and create contact sheets from Poppler renders."""
from pathlib import Path
import re

import pdfplumber
from PIL import Image, ImageDraw
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
pdf_path = root / "output/pdf/lesson-03-materials.pdf"
source = (root / "lessons/lesson-03-materials.md").read_text()
reader = PdfReader(pdf_path)
compact = lambda text: re.sub(r"\s+", "", text)
text = compact("".join(page.extract_text() for page in reader.pages))
assert "\ufffd" not in text, "Replacement glyph in extracted text"
assert "奇美醫院精準醫學核心實驗室組長邱家軍" in text
assert "邱XX" not in text
headings = re.findall(r"^#{2,3} (.+)$", source, re.MULTILINE)
for heading in headings:
    assert compact(heading) in text, f"Missing heading: {heading}"
image_count = sum(len(page.images) for page in reader.pages)
assert image_count == 4, image_count
assert len(reader.outline) > 0, "Missing PDF bookmarks"

with pdfplumber.open(pdf_path) as pdf:
    for number, page in enumerate(pdf.pages, 1):
        # Physical page clipping check; visual inspection remains necessary.
        outside = [c for c in page.chars if c["text"].strip() and (
            c["x0"] < -1 or c["x1"] > page.width + 1
            or c["top"] < -1 or c["bottom"] > page.height + 1)]
        assert not outside, f"Text outside page {number}: {outside[:2]}"

images = sorted((root / "tmp/pdfs").glob("lesson03-*.png"))
assert len(images) == len(reader.pages), (len(images), len(reader.pages))
for start in range(0, len(images), 6):
    sheet = Image.new("RGB", (1800, 1760), "#dce2e6")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(images[start:start + 6]):
        with Image.open(path) as rendered:
            rendered = rendered.convert("RGB")
            rendered.thumbnail((580, 830))
            x, y = (index % 3) * 600 + 10, (index // 3) * 880 + 30
            sheet.paste(rendered, (x, y))
            draw.text((x, y - 20), f"Page {start + index + 1}", fill="black")
    sheet.save(root / f"tmp/pdfs/lesson03-contact-{start // 6 + 1}.png")
print(f"PASS: {len(reader.pages)} pages, {len(headings)} headings, "
      f"{image_count} images, author, bookmarks, text bounds and rendered pages.")
