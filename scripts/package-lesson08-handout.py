#!/usr/bin/env python3
"""Package the offline handout and an explicit allowlist of teaching inputs."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'output/slides/lesson-08-materials.html'
SOURCE = 'lessons/lesson-08-materials.md'
DEMO = 'demos/nextflow-qc/'
FILES = [
    SOURCE, 'Nextflow_new_features.md',
    *[DEMO + name for name in [
        'main.nf', 'nextflow.config', 'README.md', 'VALIDATION.md', 'verify.py',
        'bin/multiqc-seqera.py', 'conf/gmail.config', 'conf/workflow-status.txt',
        'data/samplesheet.csv', 'data/samplesheet-one.csv',
        'data/samplesheet-missing.csv', 'data/sampleA_R1.fastq',
        'data/sampleA_R2.fastq', 'data/sampleB_R1.fastq', 'data/sampleB_R2.fastq',
        'expected/fastqc_basic_stats.tsv',
    ]],
]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'):
            self.targets.append(attrs['href'])


def main():
    manifest = json.loads((ROOT / 'output/slides/lesson-08-materials-build.json').read_text())
    source_hash = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
    if source_hash != manifest['source_sha256']:
        raise ValueError('Markdown changed after HTML compilation; rebuild the handout first')
    # Move the HTML entrypoint to the package root; embedded QC data is untouched.
    html = re.sub(r'href="\.\./\.\./([^"]+)"', r'href="\1"', HTML.read_text())
    payload = {'index.html': html.encode()}
    payload.update({name: (ROOT / name).read_bytes() for name in FILES})
    payload['BUILD-INFO.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode()
    payload['README.txt'] = '''Nextflow 生物資訊工作流程講義：分享套件

1. 先將整個 ZIP 解壓縮，再用 Chrome 或 Edge 開啟 index.html。
2. 正文、流程圖、MultiQC 圖表與已保存的 Seqera AI 最終摘要均已內嵌。
   閱讀不需安裝 Nextflow、Docker，不需 token，也不會重新呼叫 AI。
3. 要執行練習，請依講義安裝工具，進入 demos/nextflow-qc 後執行指令。
   安裝、下載容器、AI 呼叫與 Gmail 寄信仍需網路及自己的核准憑證。
4. demos/ 含程式、設定與合成 FASTQ；lessons/ 含 Markdown 原稿。
   請保留解壓後目錄結構，才能使用 index.html 的程式及測試檔連結。
5. 本套件不含 token、Nextflow secrets store、.env、work/、.nextflow/、
   主機套件或暫存執行目錄。Gmail 通知未啟用，也未驗證實際送達。
6. QC 與 AI 摘要來自微型人工合成資料，不是臨床分析或檢驗認證。
7. 只需閱讀時，可單獨傳送 index.html；其他教材與程式連結則需要本套件。
8. SHA256SUMS.txt 可用於確認套件內容完整；BUILD-INFO.json 記錄來源雜湊。
   內嵌報告已替換個人路徑，只保留 AI 最終文字，並禁止 API 連線。
'''.encode()
    links = Links()
    links.feed(html)
    for target in links.targets:
        if target.startswith(('http:', 'https:', 'mailto:', '#')):
            continue
        file = target.split('#')[0]
        if file not in payload and not any(p.startswith(file.rstrip('/') + '/') for p in payload):
            raise ValueError(f'Missing linked package resource: {target}')
    payload['SHA256SUMS.txt'] = ''.join(
        f'{hashlib.sha256(data).hexdigest()}  {name}\n'
        for name, data in sorted(payload.items())
    ).encode()
    destination = ROOT / 'output/packages/nextflow-handout.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo('Nextflow-handout/' + name, date_time=(2026, 11, 3, 0, 0, 0))
            info.external_attr = (0o100755 if name.endswith('/multiqc-seqera.py') else 0o100644) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(payload)
        for name, data in payload.items():
            assert archive.read('Nextflow-handout/' + name) == data
    print(f'PASS: {destination} ({destination.stat().st_size:,} bytes, {len(payload)} files); all local HTML links included')


if __name__ == '__main__':
    main()
