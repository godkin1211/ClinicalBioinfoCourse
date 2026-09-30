"""Render contact sheets from Poppler PNGs and audit PDF text/links."""
from pathlib import Path
from PIL import Image, ImageDraw
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
for lesson in ('01', '02'):
    reader = PdfReader(root / f'output/pdf/lesson-{lesson}-materials.pdf')
    text = ''.join(''.join(page.extract_text().split()) for page in reader.pages)
    for phrase in ['Windows', '邱XX', '附錄', 'python3']:
        assert phrase in text, (lesson, phrase)
    assert '\ufffd' not in text
    images = sorted((root / 'tmp/pdfs').glob(f'lesson{lesson}-*.png'))
    for start in range(0, len(images), 6):
        sheet = Image.new('RGB', (1800, 1760), '#dce2e6')
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(images[start:start+6]):
            im = Image.open(path).convert('RGB')
            im.thumbnail((580, 830))
            x, y = (i % 3)*600 + 10, (i//3)*880 + 30
            sheet.paste(im, (x,y))
            draw.text((x,y-20), path.name, fill='black')
        sheet.save(root / f'tmp/pdfs/contact-{lesson}-{start//6+1}.png')
    print(f'Lesson {lesson}: {len(reader.pages)} pages; text checks passed')
