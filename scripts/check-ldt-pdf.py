"""Check exported slides after Poppler rendering and create PDF contact sheets."""
from pathlib import Path
import re
import runpy
import unicodedata
import logging
import pdfplumber
from pypdf import PdfReader
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'output/playwright/ldt-20261024'
renders = [QA / f'pdf-{i:02d}.png' for i in range(1,34)]
assert all(p.is_file() for p in renders), 'Render all PDF pages with pdftoppm before this check.'
for start in range(0, len(renders), 12):
    sheet = Image.new('RGB', (1620, 1320), '#dce5df')
    draw = ImageDraw.Draw(sheet)
    for index, filename in enumerate(renders[start:start+12]):
        with Image.open(filename) as source:
            source = source.convert('RGB')
            source.thumbnail((520, 293))
            x, y = index % 3 * 540 + 10, index // 3 * 330 + 30
            sheet.paste(source, (x, y))
            draw.text((x, y-20), f'PDF page {start+index+1}', fill='black')
    sheet.save(QA / f'pdf-contact-{start//12+1}.png')

spec = runpy.run_path(str(ROOT / 'scripts/build-ldt-slides.py'))
spec['make_slides']()
reader = PdfReader(ROOT / 'output/pdf/ldt-20261024-bioinformatics.pdf')
assert len(reader.pages) == len(spec['SLIDES']) == 33
# Chrome's CJK subset fonts may extract compatibility radicals, e.g. ⽣ for 生.
compact = lambda s: re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))
for i, (page, slide) in enumerate(zip(reader.pages, spec['SLIDES']), 1):
    text = compact(page.extract_text())
    assert compact(slide['title'].replace('<br>', ' ')) in text, (i, 'missing title')
    assert f'{i:02d}/{len(reader.pages)}' in text, (i, 'missing page number')
    assert '\ufffd' not in text, (i, 'replacement glyph')
    assert abs(float(page.mediabox.width)-960) < 1
    assert abs(float(page.mediabox.height)-540) < 1
assert '奇美醫院精準醫學核心實驗室組長邱家軍' in compact(reader.pages[0].extract_text())
# Some Chrome font subsets omit FontBBox; visual page review supplements bounds.
logging.getLogger('pdfminer.pdffont').setLevel(logging.ERROR)
with pdfplumber.open(ROOT / 'output/pdf/ldt-20261024-bioinformatics.pdf') as pdf:
    for number, page in enumerate(pdf.pages, 1):
        outside = [c for c in page.chars if c['text'].strip() and (
            c['x0'] < -1 or c['x1'] > page.width+1 or
            c['top'] < -1 or c['bottom'] > page.height+1)]
        assert not outside, (number, 'text outside PDF page')

# Arithmetic audit of explicitly synthetic worked examples, not clinical validation.
assert sum([1400,1300,1250,50])/4 == 1000
assert 20*20 == 400*1 == 400
assert 20/400 == 1/(10*2) == 0.05
assert 1/400 == 0.0025
assert round(100*95/97,1) == 97.9
assert 19/20 == 0.95
print('PASS: 33 rendered pages; 16:9 dimensions; all titles/page numbers; speaker; glyph/text bounds; synthetic arithmetic.')
