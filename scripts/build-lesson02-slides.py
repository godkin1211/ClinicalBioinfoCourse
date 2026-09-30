"""Build the offline, learner-facing somatic genomics HTML deck (stdlib only)."""
from html import escape
from pathlib import Path
import math
import re

ROOT = Path(__file__).resolve().parents[1]
slides = []
SOURCES = {
    'benefits': ('NCI：biomarker testing', 'https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment'),
    'specimen': ('NCI：Biospecimen Best Practices, 2026', 'https://dctd.cancer.gov/data-tools-biospecimens/biospecimens-biobanks/resources/best-practices/biospecimen-resources/appendices/2026-4th-edition-best-practices.pdf'),
    'metrics': ('Picard：QC metrics', 'https://broadinstitute.github.io/picard/picard-metric-definitions.html'),
    'fastqc': ('FastQC：品質檢查', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/1%20Introduction/1.1%20What%20is%20FastQC.html'),
    'fastqc_quality': ('FastQC：品質圖', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html'),
    'fastqc_adapter': ('接頭', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/10%20Adapter%20Content.html'),
    'fastqc_gc': ('GC', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html'),
    'fastqc_dup': ('重複序列', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html'),
    'multiqc': ('MultiQC：報表彙整', 'https://docs.seqera.io/multiqc'),
    'library': ('Illumina：library quantification', 'https://support-docs.illumina.com/SHARE/ClusterOptimize/Content/SHARE/ClusterOptimize/LibraryQuantification.htm'),
    'mutect': ('GATK：Mutect2', 'https://gatk.broadinstitute.org/hc/en-us/articles/360037593851-Mutect2'),
    'filter': ('GATK：somatic workflow', 'https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2'),
    'igv': ('IGV：alignments', 'https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/'),
    'reference': ('IGV：reference', 'https://igv.org/doc/desktop/UserGuide/reference_genome/'),
    'bcf': ('BCFtools 文件', 'https://samtools.github.io/bcftools/bcftools.html'),
    'sam': ('SAMtools 文件', 'https://www.htslib.org/doc/samtools.html'),
    'maf': ('NCI GDC：MAF', 'https://docs.gdc.cancer.gov/Data/File_Formats/MAF_Format/'),
    'cn': ('Shen & Seshan, 2016：FACETS', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5027494/'),
    'liquid': ('Razavi et al., 2019', 'https://www.nature.com/articles/s41591-019-0652-7'),
    'tmb': ('Merino et al., 2020', 'https://pubmed.ncbi.nlm.nih.gov/32217756/'),
    'msi': ('Niu et al., 2014：MSIsensor', 'https://pubmed.ncbi.nlm.nih.gov/24371154/'),
    'msi_method': ('MSIsensor：方法文件', 'https://github.com/ding-lab/msisensor'),
    'hrd': ('Telli et al., 2016：HRD score', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6773427/'),
    'hrd_assay': ('FDA：GIS 檢測原理', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id=P190014S002'),
    'hrd_function': ('Cruz et al., 2018', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5961353/'),
    'sv': ('Manta：SV 方法', 'https://github.com/Illumina/manta'),
    'umi': ('fgbio：consensus reads', 'https://fulcrumgenomics.github.io/fgbio/tools/latest/CallDuplexConsensusReads.html'),
}


def refs(*keys):
    return ' · '.join(f'<a href="{SOURCES[k][1]}">{SOURCES[k][0]}</a>' for k in keys)


def add(topic, title, body, note='', kind=''):
    slides.append(dict(topic=topic, title=title, body=body, note=note, kind=kind))


def cards(items):
    return '<div class="cards">' + ''.join(f'<article><h3>{a}</h3><p>{b}</p></article>' for a, b in items) + '</div>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in r) + '</tr>' for r in rows) + '</tbody></table>'


def flow(items):
    return '<div class="flow">' + '<span class="arrow">→</span>'.join(f'<div>{x}</div>' for x in items) + '</div>'


def code(text):
    return '<pre><code>' + escape(text) + '</code></pre>'


def takeaway(text):
    return '<p class="takeaway">' + text + '</p>'


def answer(text):
    return '<details><summary>先想一想，再展開解析</summary><div class="answer">' + text + '</div></details>'


def command_steps(items):
    return '<div class="commands">' + ''.join(f'<article><h3>{label}</h3>{code(command)}<p>{desc}</p></article>' for label, command, desc in items) + '</div>'


def mixture_cells():
    cells = ''.join('<div class="cell tumor"><b>腫瘤</b><span>REF｜ALT</span></div>' if i == 0 else '<div class="cell"><b>正常</b><span>REF｜REF</span></div>' for i in range(10))
    return '<div class="cells" role="img" aria-label="十個二倍體細胞：一個腫瘤細胞帶一份 ALT，九個正常細胞無 ALT。共二十份 allele，只有一份 ALT。">' + cells + '</div>'


def read_schematic():
    # A deliberately selected subset of supporting reads, not a pileup screenshot.
    panels = []
    for label, biased in [('A：ALT 分散在讀段內部', False), ('B：ALT 集中在同方向末端', True)]:
        rows = []
        for i in range(6):
            left = (5 + i % 3 * 7) if not biased else 2
            width = 65 if not biased else 49
            direction = '→' if biased or i % 2 == 0 else '←'
            rows.append(f'<div class="read-row"><span>{direction}</span><i style="left:{left}%;width:{width}%"></i><b>T</b></div>')
        panels.append(f'<article class="read-panel"><h3>{label}</h3><p>同一候選位置 ↓</p><div class="read-stack">{"".join(rows)}</div></article>')
    return '<div class="read-comparison" role="img" aria-label="ALT 支持讀段形狀示意：A 含正反方向且 ALT 位於內部，B 全同方向且 ALT 接近末端；不是完整讀段或 IGV 截圖。">' + ''.join(panels) + '</div>'


def cn_bars():
    rows = []
    for p in (.2, .6, 1):
        value = math.log2((p * 6 + (1-p)*2)/2)
        rows.append(f'<div class="bar-row"><b>純度 {p:.0%}</b><div class="bar-track"><span style="width:{value/1.6*100:.3f}%"></span></div><strong>{value:.3f}</strong></div>')
    return '<div class="bar-chart" role="img" aria-label="同為腫瘤六份拷貝，純度20%、60%、100%時，log2 ratio分別為0.485、1.138、1.585。">' + ''.join(rows) + '<p class="axis-label">同一尺度：log₂ copy ratio，從 0 到 1.6</p></div>'


def load_explanations():
    """Read the deliberately small Markdown format; fail on missing/duplicate content."""
    source = (ROOT / 'lessons/lesson-02-slide-explanations.md').read_text(encoding='utf-8')
    result = {}
    for section in source.split('\n## ')[1:]:
        title, content = section.split('\n', 1)
        pieces = content.strip().split('\n### ')
        assert title not in result, f'Duplicate explanation: {title}'
        assert pieces[0].startswith('> ') and len(pieces) == 4, title
        example = pieces[0][2:].strip()
        paragraphs = []
        for piece in pieces[1:]:
            heading, text = piece.split('\n', 1)
            paragraphs.append(f'<h3>{escape(heading)}</h3><p>{escape(text.strip())}</p>')
        result[title] = (example, ''.join(paragraphs))
    return result


add('第二堂 · 癌症基因體', '癌症體細胞<br>基因體分析',
    '<p class="subtitle">從檢測目的到生物資訊證據</p><div class="hero">為什麼做 → 怎麼做 → 如何判讀</div><p class="speaker">講師：奇美醫院精準醫學核心實驗室組長邱家軍</p>',
    '高雄長庚臨床生物資訊系列課程 · 學員版 · 所有練習均為合成資料', 'cover')

add('為什麼做', '同一種癌症，不一定有相同的分子變化',
    cards([('病理與分期', '告訴我們癌症的類型、<br>形態與擴散程度。'), ('分子檢測', '補上哪些基因或路徑改變，<br>可能影響治療反應的線索。')])
    + flow(['相同癌別', '分子變化可能不同', '需要更細緻的分類'])
    + takeaway('基因檢測是補充資訊，不是取代病理、影像或臨床判斷。'),
    refs('benefits'))

add('能帶來什麼', '檢測的價值，是讓下一個決定更有依據',
    cards([('尋找機會', '在適用癌別與情境中，<br>尋找治療或臨床試驗線索。'), ('辨認限制', '特定變異可能提示某療法<br>較不容易有效，避免不適用的選擇。'), ('理解變化', '比較不同時間或病灶，<br>探索抗藥與腫瘤演化的線索。')])
    + takeaway('有分子線索 ≠ 有適用療法 ≠ 病人一定獲益；還需臨床證據與可近性。'),
    '縱向比較須控制採樣與分析差異；本課不提供個別治療建議。' + refs('benefits'))

add('檢測邊界', '先分清楚：這次檢測要回答哪一種問題？',
    table(['問題', '需要的資訊', '不能直接推論'], [
        ['腫瘤有哪些分子改變？', '腫瘤 DNA／RNA 或其他標記', '所有變異都與癌症有關'],
        ['是否帶有遺傳性癌症風險？', '合適的生殖系檢測與確認流程', '腫瘤檢出就等於遺傳'],
        ['陰性代表什麼？', '檢測範圍、檢體與偵測能力', '沒有腫瘤／沒有任何變異'],
    ]) + takeaway('今天聚焦「腫瘤體細胞分析」；不是一般人口癌症篩檢。'), refs('benefits'), 'compact')

add('學習方向', '沿著一份檢體，走完整條證據鏈',
    flow(['臨床問題', '檢體與製備', '資料 QC', '分析與判讀'])
    + cards([('前半段：資料從哪裡來？', '採到什麼、如何保存與製備，<br>決定後面能看見什麼。'), ('後半段：結論如何成立？', '先確認資料與模型是否適用，<br>再解讀變異與不確定性。')]),
    '聚焦生物資訊，不進行處方建議或正式臨床證據分級。方向鍵翻頁 · O 目錄 · F 全螢幕')

add('實務全貌', '真正的起點，不是拿到 FASTQ 才開始',
    flow(['釐清問題', '選檢測與檢體', '採樣／製備'])
    + flow(['定序與資料交接', 'QC／變異分析', '審核與結果溝通'])
    + cards([('臨床／病理／實驗室', '確認適用目的、檢體代表性，<br>執行合規採樣與檢測。'), ('生物資訊／判讀團隊', '事前確認資料需求；<br>事後回饋 QC、證據與限制。')]),
    '各角色合作；研究用流程不能直接視為經驗證的臨床檢測。' + refs('benefits', 'specimen'))

add('實務 · 選方法', '先問要找什麼，再選 panel、WES 或 WGS',
    table(['方法', '適合的問題／優勢', '必須確認'], [
        ['Targeted panel', '集中在選定基因／區域，常可分配較高深度', '基因清單、熱點或全外顯子？支援哪些事件？'],
        ['WES · 外顯子定序', '較廣泛探索蛋白編碼區變異', '捕獲不均；非編碼區與部分 SV 有限制'],
        ['WGS · 全基因體定序', '廣泛位置與結構變異證據', '成本／資料量／深度與低頻偵測的取捨'],
    ]) + takeaway('需要 RNA 融合或蛋白表現資訊時，可能須搭配 RNA 或其他檢測。'),
    '不存在對所有問題都最好的平台；範圍、事件類型及偵測能力須依方法驗證。', 'compact')

add('來源概念', '腫瘤檢出，不等於只存在於腫瘤',
    cards([('Germline · 生殖系', '源於生殖細胞／受精卵的變異<br>通常存在於多數體細胞'), ('Somatic · 體細胞', '生命歷程中後來產生的變異<br>可能僅存在部分組織或細胞')])
    + flow(['腫瘤檢體', 'Germline ＋ somatic ＋ 技術錯誤', '仍需區分來源'])
    + takeaway('判斷來源需要對照與證據；不能只看腫瘤中是否出現某個變異。'),
    '腫瘤純度、局部拷貝數、嵌合與抽樣都能改變觀察比例。' + refs('mutect'))

add('研究設計', 'Tumor–normal 與 tumor-only 差在哪？',
    table(['設計', '多了什麼資訊？', '仍缺什麼？'], [
        ['Tumor–normal<br>腫瘤＋同人正常', '比較個案本人的 allele 證據<br>協助區分 germline／somatic', '正常仍可能低覆蓋、污染<br>或帶有 somatic 變異'],
        ['Tumor-only<br>只有腫瘤', '利用族群頻率、技術背景<br>與模型縮小候選集合', '不能可靠區分所有<br>罕見 germline 與 somatic'],
    ]) + takeaway('不是「有 normal 就全解決」，也不是「沒有 normal 就無法分析」。'),
    '配對是同一個人，不只是同一癌別；資料與檢體紀錄必須一致。' + refs('mutect'))

add('檢體 · 採樣與保存', '採樣當下，就決定資料代表哪一個腫瘤',
    table(['收集與處理紀錄', '為什麼影響分析？'], [
        ['哪個病灶？哪個時間？治療前或後？', '不同區域與時間可能有不同變異組成'],
        ['固定／冷凍、處理延遲、保存與凍融', '改變核酸完整度與損傷背景'],
        ['組織／血漿／正常對照與身分追蹤', '決定訊號來源、配對與污染檢查'],
    ]) + takeaway('生物資訊可以發現異常，但無法把沒有採到的腫瘤細胞算回來。'),
    '依檢體與經驗證的 SOP 處理；不以通用時間或閾值取代院內規範。' + refs('specimen'), 'compact')

add('檢體 · 病理評估', '同樣一塊組織，腫瘤、壞死與正常成分不同',
    cards([('病理端先看', '確認有無腫瘤、分布及壞死；<br>需要時評估是否圈選或富集。'), ('生物資訊端接住', '保留病理估計比例與處理紀錄，<br>用來檢視低頻訊號與 CN 模型。')])
    + flow(['腫瘤成分較少', '腫瘤訊號可能被稀釋', '陰性判讀需更謹慎'])
    + takeaway('病理的細胞比例是線索，不必然等於基因體模型估計的 purity。'),
    '圈選與檢體適用性由病理／實驗室評估；生物資訊不代替切片判讀。' + refs('specimen', 'cn'))

add('製備 · 核酸萃取', '有 DNA，不代表有足夠可分析的 DNA',
    cards([('量是否足夠？', '用適當方法評估濃度與輸入量；<br>低量可能限制原始分子數。'), ('品質是否適用？', '檢查片段長度、完整度，<br>必要時評估可擴增性。')])
    + table(['交給分析端的資訊', '後續可能看到的影響'], [
        ['低輸入量／高 PCR 需求', '重複率較高、有效分子深度不足'],
        ['嚴重片段化／損傷', '短 insert、覆蓋偏差或假變異背景'],
    ]), '濃度、完整度、可用分子數不是同一件事；不可只憑單一 QC 值推斷。' + refs('specimen'), 'compact')

add('製備 · 文庫', '文庫把 DNA 變成可定序、可追蹤的分子',
    flow(['處理片段', '接上 adapter', '富集／擴增', '文庫 QC／上機'])
    + cards([('Sample index', '辨識讀段屬於哪個樣本；<br>必須與 sample sheet 一致。'), ('UMI（若有設計）', '標記原始分子，協助分組；<br>不是樣本 index 的同義詞。')])
    + takeaway('保存試劑／target 版本、PCR 與文庫 QC 紀錄；文庫大小與量都要評估。'),
    '概念流程；各種製備步驟不同，UMI 非所有方法都有。' + refs('library', 'umi'))

add('檢體影響', 'FFPE 與低輸入量，如何變成分析問題？',
    flow(['固定／保存', '片段化或 DNA 損傷', '文庫／PCR 放大', '讀段中的偏差'])
    + cards([('FFPE 損傷', '胞嘧啶脫胺可形成 C&gt;T／G&gt;A 假訊號。<br><strong>但 C&gt;T 本身不是 artifact 證明。</strong>'), ('起始分子不足', '同一來源被反覆讀取，depth 仍會增加。<br><strong>更多 reads 不一定是更多獨立證據。</strong>')]),
    'FFPE＝福馬林固定石蠟包埋；損傷與方向性需依文庫及流程評估。' + refs('filter'))

add('分子證據', '400 條 reads，不一定來自 400 個分子',
    '<div class="split"><article class="panel"><h3>假設：重複讀取</h3><p class="big">20 × 20</p><p>20 個原始分子<br>每個產生 20 條 reads</p></article><article class="panel"><h3>假設：獨立取樣</h3><p class="big">400 × 1</p><p>400 個原始分子<br>每個產生 1 條 read</p></article></div>'
    + takeaway('兩者 raw depth 都是 400；獨立分子數不同。UMI 可協助分組與 consensus。'),
    'UMI＝unique molecular identifier，分子識別標記。算例非本課 BAM 分子真值；UMI 不解決所有損傷或比對錯誤。' + refs('umi'))

add('資料交接', '送進 pipeline 前，先把樣本對照表補齊',
    table(['要保存的資訊', '影響哪個分析決定？'], [
        ['個案／檢體／定序 ID；normal 來源', '配對核對、重複樣本與污染判讀'],
        ['病灶、採樣時間、治療前後', '跨時間 VAF 與克隆比較'],
        ['FFPE／冷凍、DNA 輸入量、病理比例', '損傷背景、有效分子數與純度假設'],
        ['Panel／WES／WGS、target、reference、批次', '可分析範圍、資源相容性與結果比較'],
    ]), '病理 tumor cellularity 是重要線索，但不必然等於基因體模型估計的 purity。')

add('下機 QC · 讀段', '拿到資料，先確認「分對了嗎？讀好了嗎？」',
    table(['階段', '生物資訊檢查', '想排除的問題'], [
        ['拆分樣本', 'Index／sample sheet、讀段數與配對', '分錯樣本、漏檔或 R1／R2 不一致'],
        ['FASTQ 品質', '每個 cycle 的品質、N、adapter', '低品質末端、接頭讀入或定序異常'],
        ['跨樣本彙整', 'GC、長度與批次分布', '找離群樣本，再回查製備紀錄'],
    ]) + takeaway('FastQC 等工具產生訊號；MultiQC 可彙整，但警示不等於自動淘汰。'),
    '下機輸出經鹼基判讀／樣本拆分產生 FASTQ，依平台而異。' + refs('fastqc', 'multiqc'), 'compact')

add('下機 QC · FastQC 判讀', 'FastQC：先看圖形，再解讀警示',
    '<div class="fastqc-grid">'
    '<article><h3>① 各位置鹼基品質</h3><div class="module-name">Per base sequence quality</div>'
    '<p>橫軸 read 位置；縱軸 Q，留意末端下降。<br>Q20 ≈ 1%、Q30 ≈ 0.1% 鹼基錯誤機率。<br>這是鹼基品質，不是變異可信度。</p></article>'
    '<article><h3>② 接頭含量</h3><div class="module-name">Adapter Content</div>'
    '<p>橫軸 read 位置；縱軸累積含接頭比例。<br>末端上升，可能讀穿較短的 DNA 片段。<br>回查實際接頭序列與片段長度。</p></article>'
    '<article><h3>③ 每條 read 的 GC 分布</h3><div class="module-name">Per sequence GC content</div>'
    '<p>橫軸 GC%；縱軸 read 數，留意尖峰／多峰。<br>先對照 panel 與文庫設計，再看分布偏移。<br>偏離模型，不等於已證實污染。</p></article>'
    '<article><h3>④ 序列重複程度</h3><div class="module-name">Sequence Duplication Levels</div>'
    '<p>橫軸序列出現次數，留意高重複區偏多。<br>可能來自 PCR，也可能是靶向富集。<br>不等於獨立分子數或 BAM 去重率。</p></article></div>',
    '原始與處理後報告皆保留；按 E 閱讀詳解。' + refs('fastqc_quality', 'fastqc_adapter', 'fastqc_gc', 'fastqc_dup'), 'fastqc-slide')

add('下機 QC · 比對與覆蓋', '平均 500×，不代表每個目標位置都有 500×',
    table(['指標', '回答的問題'], [
        ['Mapping／MAPQ、insert size', '讀段能否可靠定位？片段分布是否異常？'],
        ['Duplicates／UMI 分子深度', '是否反覆讀同一分子？有多少有效證據？'],
        ['On-target、coverage breadth、均勻度', '讀到目標了嗎？多少目標達到要求的深度？'],
        ['身分 fingerprint／污染估計', '配對是否合理？有無其他來源混入？'],
    ]) + takeaway('看逐區域覆蓋與方法規格；平均深度不能替代可評估範圍。'),
    'Capture、amplicon、WGS 使用適合的指標；不同 filtering 定義的數字不可直接比較。' + refs('metrics'), 'compact')

add('QC · 回饋迴路', 'QC 的用途，是決定下一步，而不只是打勾',
    table(['觀察到的問題', '回查什麼？', '團隊可評估的下一步'], [
        ['讀段少、文庫仍有複雜度', '上機分配與資料產出', '是否補定序'],
        ['高重複、獨立分子不足', '輸入量與文庫製備', '重製文庫／另取檢體的可行性'],
        ['配對疑似錯誤或污染', '追蹤鏈、正常來源及批次', '暫停結果釋出、查明來源'],
    ]) + takeaway('先保留 QC 證據與原因；加深定序不一定能解決前分析問題。'),
    '此為排查框架，非自動決策規則；依方法驗證與院內 SOP，由責任人員審核。', 'compact')

add('分析 · 前處理', '從 FASTQ 到可用的比對證據',
    flow(['核對版本／檔案', '必要的讀段處理', '比對 reference', '排序／索引與 QC'])
    + cards([('非 UMI 文庫', '依方法辨識重複讀段與偏差；<br>不是把所有同位置 reads 一律刪除。'), ('UMI 文庫', '依設計擷取 UMI、分組與 consensus；<br>處理及重新比對順序依流程而定。')])
    + takeaway('Reference、target BED、資源版本與樣本 ID 一致，才有可比較的分析輸入。'),
    'BED 描述目標區間；標準 BED 起點為 0-based、終點不含。與 VCF 座標互換時須確認規則。' + refs('sam', 'umi'))

add('全貌', '一份 BAM，分成三條不同的分析路徑',
    flow(['FASTQ＋檢體資訊', 'QC／比對', 'BAM／CRAM＋索引'])
    + cards([('SNV／indel', '局部序列證據<br>Somatic calling → filtering'), ('CNV', '區域深度＋allele balance<br>校正 → 分段 → CN 模型'), ('SV', 'Split reads＋read pairs<br>斷點／局部組裝')])
    + takeaway('最後再整合 QC、註解與人工查證；不能用單一 caller 包辦所有事件。'),
    'SNV＝單鹼基變化；indel＝短插入／缺失；CNV＝拷貝數變化；SV＝結構變異。')

add('短變異原理', 'Somatic caller 不只是「數到幾條 ALT」',
    flow(['局部 reads', '候選 haplotypes', '比較真變異／錯誤模型', '候選 VCF'])
    + cards([('為何重建局部序列？', 'Indel 周圍可能有不同對齊方式。<br>局部組裝能比較完整候選序列。'), ('為何不固定期待 50%？', '純度與亞克隆讓 allele 比例改變。<br>腫瘤不是單一、均勻的二倍體樣本。')]),
    '以 Mutect2 為方法案例；haplotype＝同一條染色體上的相連 allele 組合。本課不執行 Mutect2。' + refs('mutect'))

add('正常參考', 'Normal 是參考檢體，不是無錯誤的真值',
    cards([('先查來源', '血液腫瘤／克隆性造血<br>可能使血液帶 somatic 變異'), ('再查品質', '鄰近組織可能混入腫瘤<br>正常資料也需 QC 與配對核對')])
    + '<div class="equation">Normal：0 / 200 ALT ≠ 完全不存在</div>'
    + '<p>獨立抽樣下，零次觀察的單側約 95% 上界：3 / 200 ≈ 1.5%。</p>',
    '3/n 是抽樣近似，不是臨床偵測極限；reads 若不獨立，此近似也受限。' + refs('liquid'))

add('分析資源', 'Matched normal、PoN、族群資料，不能互換',
    table(['資源', '回答的問題', '不能當成'], [
        ['Matched normal', '這個人非腫瘤檢體有哪些證據？', '絕對沒有污染的真值'],
        ['PoN · Panel of normals', '多份正常資料反覆出現哪些技術背景？', '這位個案的 germline 清單'],
        ['族群頻率資源', '某 allele 在參考族群中多常見？', '個案來源的直接證明'],
    ]) + takeaway('資料庫沒有收錄 ≠ 一定是 somatic；PoN 也要與平台及流程相容。'),
    refs('filter'))

add('流程責任', 'Calling、filtering、annotation，各管一件事',
    table(['步驟', '問題', '保留什麼？'], [
        ['Calling', '哪些位置值得成為候選？', '未篩選 VCF、模型統計'],
        ['Filtering', '哪些訊號有偏差或替代解釋？', 'FILTER 原因、污染／方向性模型'],
        ['Annotation', '落在哪個基因、轉錄本或已知條目？', '註解版本與來源'],
        ['Review／validation', '技術證據是否一致、可重現？', '人工紀錄及適切的追加驗證'],
    ]) + takeaway('跑完 caller 不是分析完成；PASS 也不等於已驗證。'),
    'Mutect2 後仍需 filtering；方向性與污染可提供額外資訊。' + refs('filter'), 'compact')

add('資料格式', 'VCF、MAF、SEG：不是同一張結果表',
    table(['檔案', '記錄的內容', '先核對'], [
        ['BAM／CRAM＋索引', '讀段與比對證據', 'Reference、read-group SM、配對樣本'],
        ['VCF／BCF', '事件與各樣本的 GT／AD／DP／AF 等', 'Header 定義；哪一欄才是 tumor？'],
        ['MAF', 'Mutation Annotation Format<br>常用於癌症 cohort 註解摘要', '不是 minor allele frequency<br>不能取代 BAM 讀段證據'],
        ['SEG／segmentation', '連續區段及其訊號值', '是 log₂ ratio，還是絕對 copy number？'],
    ]), 'AD 通常依 REF、ALT 排列；DP 未必等於 AD 總和；AF 定義依 caller。' + refs('bcf', 'maf'), 'compact')

add('CNV · 分析原理', '從 depth 到 copy number，中間還有模型',
    flow(['區域計數', 'GC／捕捉等校正', '相對訊號與分段', 'Purity／ploidy／CN'])
    + cards([('Segmentation · 分段', '把相鄰、變化相近的區域整合。<br>不是每個低 depth 點都叫 deletion。'), ('Allele-specific CN', '合看總量與 informative SNP 的平衡。<br>可幫助判斷哪個 allele 增加／流失。')])
    + takeaway('WES 捕捉範圍不連續；未校正的兩個基因深度不能直接拿來判 CNV。'),
    'Ploidy＝整體倍體背景；模型可能有多組合理解。' + refs('cn'))

add('CNV · LOH', '總量不變，也可能失去原本的雜合性',
    table(['同一原本 AB 的區域', '純腫瘤示意', '總 CN', 'B allele 比例'], [
        ['保留兩種 allele', 'A ＋ B', '2', '1/2'],
        ['流失 B，僅剩 A', 'A', '1', '0'],
        ['流失 B，但有兩份 A', 'A ＋ A', '2', '0'],
    ]) + takeaway('A＋A：copy-neutral LOH。只看總 copy ratio，可能漏掉 allele 的改變。'),
    'A/B 是 allele 代號，不一定是鹼基 A/B。真實腫瘤混入 normal 後，比例會往 0.5 靠近。' + refs('cn'))

add('SV · 斷點', '結構變異需要跨位置的證據',
    cards([('Split reads', '同一 read 的不同部分<br>指向不同位置'), ('Discordant pairs', '配對 reads 的距離、方向<br>或染色體關係不如預期'), ('Depth／assembly', '區域拷貝變化、局部組裝<br>可增加斷點支持')])
    + takeaway('一致斷點仍要排除重複序列、比對錯誤與文庫嵌合；DNA 重排不等於已表現的 RNA fusion。'),
    '本課 single-end toy BAM 無 paired-end／真實 SV 證據；此頁是方法概念。' + refs('sv'))

add('起始案例', '兩個 5% VAF，可信度相同嗎？',
    '<div class="split"><article class="panel"><h3>候選 A</h3><p class="big">20 / 400</p><p>ALT 正／反向：10 / 10<br>末端 ALT：0</p></article><article class="panel"><h3>候選 B</h3><p class="big">20 / 400</p><p>ALT 正／反向：20 / 0<br>末端 ALT：20</p></article></div>'
    + takeaway('兩者 VAF 都是 5%；支持訊號的「分布」卻不同。'),
    '合成案例；VAF＝ALT 支持數／納入計數的讀段總數。ALT＝相對 reference 的替代 allele。')

add('QC', '深度之外，還有五組證據要看',
    table(['檢查層次', '具體看什麼？', '可疑時回查'], [
        ['樣本', '配對、污染、批次、輸入量', '檢體與文庫紀錄'],
        ['讀段', 'Base quality、MAPQ、duplicates', '獨立分子與比對區域'],
        ['候選位置', 'ALT count、strand、read position', '方向／末端集中現象'],
        ['局部背景', '重複序列、indel、soft clipping', '替代比對或真實結構變化'],
        ['正常參考', '同位置深度、ALT 與來源', '缺乏證據，還是有排除證據？'],
    ]), 'Soft clipping＝讀段端部未納入比對的部分；不能看到 clipping 就一律刪除。', 'compact')

add('讀段形狀', '相同比例，支持訊號可以長得很不一樣',
    read_schematic() + takeaway('看 ALT 是否跨方向、跨位置分布；也要核對比對品質與獨立性。'),
    '箭頭＝比對方向，T＝ALT。僅選六條支持讀段的原創形狀示意，非完整 pileup／IGV 截圖，不能由圖計算 VAF。')

add('比例概念', 'VAF 的分母是 allele 證據，不是癌細胞',
    '<div class="equation">VAF = ALT 支持數 / 納入計數的總數</div>'
    + cards([('觀察到的數值', '例如 20 / 400 = 5%<br>受納入規則、抽樣及錯誤影響'), ('想知道的生物問題', '多少腫瘤細胞帶變異？<br>需要純度、CN 與模型才能推估')])
    + takeaway('VAF ≠ tumor purity；VAF ≠ cancer cell fraction（CCF）。'),
    '實際 FORMAT/AF 也可能是模型估計值；先查 header，不強迫等同 AD 比例。')

add('白話算例', '全部癌細胞都有變異，VAF 仍可只有 5%',
    '<p class="intro">假設 10 個細胞都為二倍體；只有 1 個是腫瘤，且帶 1 份 ALT。</p>'
    + mixture_cells()
    + '<div class="equation">1 份 ALT / 20 份 allele = 5%</div>'
    + takeaway('腫瘤純度 10%；帶變異的癌細胞比例卻是 100%（clonal）。'),
    '簡化混合模型：正常不帶 ALT、各 allele 等機率被讀到，沒有拷貝數差異或比對偏差。', 'model-slide')

add('實作 · 範圍', '本課做候選證據稽核，不跑完整 caller',
    '<div class="stats"><div><b>5 kb</b><span>人工 chrToy</span></div><div><b>3</b><span>人工候選 SNV</span></div><div><b>0</b><span>病人資料</span></div></div>'
    + cards([('會做', 'SAM → 排序／索引 BAM<br>查 VCF、計數 reads、瀏覽 IGV'), ('不會做', '真實 alignment／Mutect2<br>UMI、FFPE 化學損傷或 CNV／SV calling')])
    + takeaway('候選標記與讀段位置是人工指定；CN SEG 也是另一個獨立模型。'),
    '<a href="../../demos/lesson-02-somatic/README.md">合成資料說明與限制</a>')

add('實作 · 從 BAM 核對', '把相同的 5%，拆成可檢查的證據',
    code('samtools view tumor.bam | python3 ../audit_reads.py')
    + table(['事件／位置', 'Depth', 'ALT', '正／反 ALT', '末端 ALT'], [
        ['A · 500', '400', '20', '10 / 10', '0'],
        ['B · 1500', '400', '20', '20 / 0', '20'],
        ['D · 2500', '400', '200', '100 / 100', '0'],
    ]) + '<p>正常：A、B 為 0 / 200；D 為 100 / 200。</p>',
    '本次已重跑核對。腳本僅支援 150M；MAPQ/BQ≥20 為教學規則，末端指距任一端不足 5 bp。', 'compact')

add('案例判讀', 'A 與 B：不只寫「接受／拒絕」',
    table(['事件', '目前可支持', '還需要查什麼？'], [
        ['A · 5% VAF', '方向與位置較一致<br>可保留為研究候選', '獨立分子、比對背景、PoN<br>Normal 的偵測能力與追加驗證'],
        ['B · 同樣 5%', '方向／末端集中<br>技術上可疑，先回查', '損傷或文庫問題、替代比對<br>必要時重新製備或適切驗證'],
    ]) + takeaway('Hotspot 註解不能補足技術證據；多個 caller 同意也不是獨立驗證。'),
    'chrToy 無真實基因／hotspot 身分。B 僅為 FFPE-like 偏差示意，不能據此確定化學原因。')

add('案例判讀', 'C 與 D：別把相對訊號當成確定來源',
    cards([('C · 區段 log₂ ratio=0.485', '模型真值：p=20%、腫瘤 CN=6。<br>如果不知道真值，不能只由 ratio 反推 CN。'), ('D · Tumor／normal 都約 50%', '提供 germline-like 證據。<br>不能因出現在腫瘤 VCF 就當成 somatic。')])
    + takeaway('請記錄：目前判斷、支持證據、缺少資訊、下一步。'),
    'C 是獨立 SEG 模型；D 是 chrToy:2500。來源仍需檢體與配對核對，不是臨床分級。')

add('生物標記 · TMB', 'TMB：計算突變密度，不是直接數 VCF 行數',
    '<p class="intro">Tumor mutational burden（腫瘤突變負荷）：每 Mb 分析範圍內，符合規則的體細胞突變數。</p>'
    + flow(['取得候選突變', '依規則篩選／排除', '突變數 ÷ 分析 Mb'])
    + table(['計算環節', '生物資訊端必須確認'], [
        ['分子：哪些突變算一筆？', 'SNV／indel、同義／非同義的納入規則；排除 germline 與 artifact。'],
        ['分母：哪些區域能納入？', '依已驗證流程定義可分析 Mb；分子與分母必須對應同一範圍。'],
        ['輸出：數值能直接比較嗎？', '保存 mut/Mb、區域／QC 與版本；panel 差異須校準，不能只比數字。'],
    ]), 'TMB 可提供免疫治療相關線索，但不等於新抗原數或必然有效；不設定通用治療閾值。' + refs('tmb'), 'compact biomarker-slide')

add('生物標記 · MSI', 'MSI：比較微衛星長度，不是計算 indel 筆數',
    '<p class="intro">Microsatellite instability（微衛星不穩定）：短重複序列長度改變，常與錯配修復缺陷相關。</p>'
    + flow(['BAM＋微衛星位點', '比較重複長度分布', '彙整分數與分類'])
    + table(['分析環節', '生物資訊端必須確認'], [
        ['比較基準', 'Tumor–normal 比較；tumor-only 須用適配的基準或已驗證模型。'],
        ['位點與 QC', '足夠可評估位點及覆蓋；注意低腫瘤純度、PCR 滑動與比對誤差。'],
        ['輸出與判讀', '分數、可評估位點數、MSI-H／MSS 或無法判定；閾值依方法。'],
    ]), 'MSI 與 MMR 蛋白 IHC 看不同層次；不能以高 TMB 代替 MSI 判定。' + refs('msi', 'msi_method'), 'compact biomarker-slide')

add('生物標記 · HRD', 'HRD：從基因變異與基因體疤痕看修復缺陷',
    '<p class="intro">Homologous recombination deficiency（同源重組修復缺陷）：精確修復 DNA 雙股斷裂的能力受損。</p>'
    + flow(['廣泛 SNP／深度訊號', '校正／分段<br>各 allele 拷貝數', '疤痕評分＋BRCA 證據'])
    + table(['常見疤痕指標', '觀察的是什麼？'], [
        ['LOH · 雜合性喪失', '原本兩種 allele 的區域失去其中一種；不一定伴隨總 CN 減少。'],
        ['TAI · 端粒等位基因失衡', '兩種 allele 比例失衡的區段延伸至染色體末端。'],
        ['LST · 大尺度狀態轉換', '相鄰大型基因體區段間的拷貝數狀態轉換；依規則過濾小片段。'],
    ]), '疤痕 ≠ 當下功能或必然藥效；分數與閾值須依方法驗證。' + refs('hrd', 'hrd_assay', 'hrd_function'), 'compact biomarker-slide')

add('液態切片', '血漿中找到變異，不一定都來自腫瘤',
    flow(['血漿 cfDNA', '腫瘤＋其他組織來源', '低頻訊號＋錯誤控制', '來源判斷'])
    + cards([('cfDNA 與 ctDNA', 'cfDNA＝游離 DNA。<br>ctDNA＝其中來自腫瘤的部分。'), ('要查的限制', '起始分子數、腫瘤釋放量、CH。<br>陰性不等於沒有腫瘤變異。')])
    + takeaway('CH（克隆性造血）可提供非腫瘤來源的 somatic 訊號。'),
    '需要適合的正常／白血球對照與分析設計；此頁不是液態切片檢測建議。' + refs('liquid'))

add('結果 · 三層判讀', '從「偵測到」走到「有意義」，不能跳步',
    table(['層次', '要回答的問題', '不能省略的檢查'], [
        ['技術可信度', '訊號是真的嗎？方法能測到嗎？', '讀段、FILTER、覆蓋與追加驗證需求'],
        ['生物學意義', '影響哪個基因／功能？來源為何？', '轉錄本、變異類型、normal、CN 背景'],
        ['臨床適用性', '這個癌別與情境有什麼證據？', '來源與日期、適用條件、專業審核'],
    ]) + takeaway('結果同時交付「發現、可評估範圍與限制」；註解命中不等於可直接用藥。'),
    '疑似生殖系結果需依適當流程確認；陰性與資料不足分開表達。' + refs('benefits'), 'compact')

add('整合檢核', '回到 5% VAF：你還會要求哪些證據？',
    '<ol class="checks"><li>Normal=0/200，就能確認只存在腫瘤？</li><li>Sample index 相同，就代表同一個原始分子？</li><li>400× 就保證能可靠偵測 5%？</li><li>Log₂ copy ratio=0.485，就能指定絕對 CN？</li></ol>'
    + answer('都不能。零次觀察不證明不存在；sample index 只辨識樣本。還需有效分子、經驗證的偵測能力及純度／倍體模型。'),
    '先說明缺少的資訊，再提出下一步；不要把不確定性藏在二元結論中。')

add('帶走的框架', '每個候選事件，都保留一條證據鏈',
    flow(['問題與檢體', '製備與資料 QC', '分析與查證', '解讀與回饋'])
    + cards([('保留可重建的紀錄', 'Reference、目標區、版本、參數、原始候選與 FILTER。'), ('寫清楚結論邊界', '觀察到什麼？排除什麼？<br>哪些資訊仍缺少？下一步做什麼？')])
    + takeaway('流程成功 ≠ 候選已驗證；技術證據 ≠ 臨床行動。'),
    '以下為課後操作附錄；主課程不要求學員自行開發完整 pipeline。', 'closing')

# Optional appendices: operations and deeper models follow the core narrative.

add('附錄 A · 環境', '沿用第一堂環境，再準備 IGV',
    code('sudo apt update\nsudo apt install -y python3 samtools bcftools\npython3 --version\nsamtools --version\nbcftools --version')
    + '<p>以上在 Ubuntu Bash 執行；圖形判讀使用 IGV Desktop。<br>本課不需安裝 GATK、R、Conda、PLINK 或 Python 第三方套件。</p>',
    '<a href="../../lessons/lesson-02-materials.md">Windows／WSL 完整安裝說明</a> · <a href="https://igv.org/doc/desktop/DownloadPage/index.html">IGV 下載</a> · 受管制電腦先洽資訊部門。')

add('附錄 A · 交付檔案', '不要只帶 BAM，卻忘了 reference 與索引',
    table(['檔案', '用來做什麼？'], [
        ['reference.fa ＋ reference.fa.fai', '本例 chrToy 序列與索引'],
        ['tumor.bam／normal.bam ＋ 各自 .bai', '讀段證據與區域定位'],
        ['candidates.vcf.gz ＋ .tbi', '人工候選與索引'],
        ['tumor.evidence.tsv／normal.evidence.tsv', '完整計數，補足畫面 downsampling 限制'],
        ['copy_number.seg', '獨立 CN 模型；不可當成 toy BAM 的 CN 結果'],
    ]), '維持檔名與索引對應；Windows／WSL 路徑交接方式見學員教材。', 'compact')

add('附錄 · 實作 · 起跑', '先建立一份新的練習資料',
    command_steps([
        ('① 進入第二堂資料夾', 'cd ~/KCGMH_Cource_Series/demos/lesson-02-somatic', '專案路徑不同時，請修改此路徑。'),
        ('② 產生新資料，再進入目錄', 'python3 generate.py practice01\ncd practice01', 'practice01 必須尚未存在；重做時改用 practice02。'),
        ('③ 準備 BAM／VCF 與證據表', 'bash ../prepare.sh', '重跑會替換同名輸出；只在本課練習目錄執行。'),
    ]), 'Ubuntu／WSL Bash；不依賴第一堂輸出。安裝與工具版本檢查見附錄。', 'command-slide')

add('附錄 · 實作 · 讀 VCF', '先確認樣本與欄位，再讀數值',
    command_steps([
        ('① 列出樣本名', 'bcftools query -l candidates.vcf.gz', '確認 TUMOR／NORMAL，不假設第一個樣本必定是腫瘤。'),
        ('② 看欄位定義', 'bcftools view -h candidates.vcf.gz', 'AD、DP、AF 與 FILTER 的意義，要回到 header。'),
    ]) + table(['本例 TUMOR · A', '怎麼讀？'], [['AD=380,20；DP=400；AF=0.05', '380 REF＋20 ALT；人工設定 5%']]),
    '本例 GT、AF、ReviewBias／NormalEvidence 均由產生器指定，不是 Mutect2 推論。' + refs('bcf'), 'command-slide')

add('附錄 · 實作 · IGV', '回到讀段：位置、方向與周圍序列',
    flow(['載入 reference.fa', '載入兩份 BAM＋索引', '跳至 chrToy 位置', '查看候選與周圍'])
    + table(['區域', '觀察任務'], [
        ['chrToy:450–550', 'A：ALT 正反向與內部位置'],
        ['chrToy:1450–1550', 'B：同方向、讀段末端集中'],
        ['chrToy:2450–2550', 'D：normal 也有大量 ALT'],
    ]), '使用本課 chrToy reference，不是 hg19／hg38。IGV 可抽樣顯示，畫面數量不等於完整 BAM 計數。' + refs('igv', 'reference'))

add('附錄 B · BAM', '逐步理解 prepare.sh：建立比對檔',
    command_steps([
        ('Reference 索引', 'samtools faidx reference.fa', '建立 reference.fa.fai；不會改成真實人類 reference。'),
        ('轉格式並排序', 'samtools view -b tumor.sam | samtools sort -o tumor.bam', '-b 輸出 BAM；| 把結果交給 sort；不是執行 alignment。'),
        ('索引與基本結構檢查', 'samtools index tumor.bam\nsamtools quickcheck -v tumor.bam', '索引支援定位；quickcheck 不會證明候選事件正確。'),
    ]), 'Normal 執行相同步驟；prepare.sh 以迴圈處理兩份資料。' + refs('sam'), 'command-slide')

add('附錄 B · VCF', '逐步理解 prepare.sh：壓縮、索引、查詢',
    command_steps([
        ('壓縮人工候選檔', 'bcftools view -Oz -o candidates.vcf.gz candidates.vcf', '-Oz 輸出 BGZF 壓縮 VCF；不會新增 somatic calling。'),
        ('建立索引', 'bcftools index -t candidates.vcf.gz', '-t 建立 TBI；索引不是變異內容本身。'),
        ('查詢事件與各樣本證據', "bcftools query -f '%CHROM\\t%POS\\t%ID\\t%FILTER[\\t%SAMPLE:%AD:%DP:%AF]\\n' candidates.vcf.gz", '方括號對每個樣本重複輸出；\\t 為分隔，\\n 為換行。'),
    ]), refs('bcf'), 'command-slide')

add('附錄 B · 驗證', '看到 PASS，先問「驗證的是什麼」',
    code('python3 ../verify.py .\npython3 ../models.py')
    + cards([('verify.py', '核對合成資料的預期數值、<br>偏差形狀、樣本及索引檔。'), ('models.py', '重算 VAF／CN 混合模型，<br>以及獨立抽樣的理論機率。')])
    + takeaway('兩者都不會驗證真實 somatic caller 的臨床效能。'),
    '2026-09-27 重新執行：SAMtools 1.22、BCFtools 1.22；合成練習核對通過。')

add('附錄 · 方向性', 'Strand、orientation、duplex 是三回事',
    cards([('Read strand', 'Read 比對到 reference 的<br>正向或反向'), ('Pair orientation', '一起看 R1／R2 與配對方向<br>例如 F1R2／F2R1'), ('Duplex consensus', '辨識同一原始 DNA 分子雙股<br>再整合對應讀段證據')])
    + takeaway('正反向都有 ALT ≠ 已完成 duplex 驗證。'),
    '本課 single-end toy BAM 只展示 strand／read-end bias，不展示 F1R2 或 duplex。' + refs('umi', 'filter'))

add('附錄 · 混合模型', '把 VAF 的四個影響因素分開',
    '<div class="equation">預期 VAF = p × f × m / [p × C + (1 − p) × 2]</div>'
    + table(['符號', '意思', '分子／分母的角色'], [
        ['p', '模型中的腫瘤細胞比例（purity）', '腫瘤對混合物的貢獻'],
        ['f', 'CCF：帶變異的癌細胞比例', '多少癌細胞提供 ALT'],
        ['m', '帶變異癌細胞內的 ALT 拷貝數', '每個帶變異癌細胞提供幾份 ALT'],
        ['C', '此區域每個癌細胞的總拷貝數', '腫瘤＋正常的總 allele 貢獻'],
    ]),
    '假設正常二倍體且無 ALT，所有癌細胞此處 CN 一致、allele 等機率取樣。不是通用 CCF 反推公式。', 'compact')

add('附錄 · 模型比較', '單一 VAF，可能對應多個生物情境',
    table(['情境', 'p / f / m / C', '預期 VAF'], [
        ['二倍體、全部癌細胞帶一份 ALT', '0.6 / 1 / 1 / 2', '30%'],
        ['同上，但低純度', '0.1 / 1 / 1 / 2', '5%'],
        ['一半癌細胞帶一份 ALT', '0.6 / 0.5 / 1 / 2', '15%'],
        ['全部癌細胞帶一份 ALT、純度較低', '0.3 / 1 / 1 / 2', '15%'],
    ]) + takeaway('15% 不能單獨區分「一半癌細胞」與「全部癌細胞、較低純度」。'),
    '同一簡化模型的算例；不直接對應個別病人的克隆結構。')

add('附錄 · Copy number', '總拷貝數增加，VAF 不一定上升',
    '<p class="intro">固定 p=20%、f=100%、腫瘤總 CN=6；只改變 ALT 有幾份。</p>'
    + cards([('1 份 ALT ＋ 5 份 REF', '<span class="big">7.14%</span><br>0.2 × 1 / 2.8'), ('3 份 ALT ＋ 3 份 REF', '<span class="big">21.43%</span><br>0.2 × 3 / 2.8')])
    + takeaway('除了總 CN，還要知道哪一個 allele 被增加，以及增加幾份。'),
    '分母 2.8＝0.2×6＋0.8×2。模型未考慮亞克隆之間的 CN 差異。')

add('附錄 · 區域訊號', '同樣六份拷貝，低純度會稀釋訊號',
    '<p class="intro">以正常二倍體為基準：log₂ ratio = log₂{[p × 6 + (1 − p) × 2] / 2}</p>'
    + cn_bars()
    + takeaway('log₂ ratio 是相對訊號，不是「幾份拷貝」。0.485 不等於 CN 0.485。'),
    '獨立 CN 混合模型，不是 toy BAM depth 結果；真實流程的正規化基準與倍體可能不同。' + refs('cn'))

add('附錄 · 克隆比較', '治療後 VAF 上升，是否代表克隆擴張？',
    '<div class="split"><article class="panel"><h3>治療前</h3><p class="big">15%</p><p>純度 30%、CCF 100%<br>二倍體、單份 ALT</p></article><article class="panel"><h3>治療後</h3><p class="big">30%</p><p>純度 60%、CCF 100%<br>二倍體、單份 ALT</p></article></div>'
    + answer('此假設中 CCF 完全沒變；只是純度不同。真實比較還要查病灶、採樣、CN、覆蓋與不確定性。'),
    '這是反例，不是治療反應研究；clonal／subclonal 的判斷受方法解析度限制。', 'model-slide')

add('附錄 C · 抽樣模型', '多讀一些，比較容易抽到 ALT，但不等於 LOD',
    '<p class="intro">假設 reads 獨立、真實 ALT 機率 5%、完全沒有錯誤。</p>'
    + table(['讀段數 n', '至少看到 3 條 ALT 的理論機率'], [
        ['30', '18.78%'], ['100', '88.17%'], ['400', '接近 100%（不是數學上保證）'],
    ]) + '<div class="equation small">X ~ Binomial(n, 0.05)；P(X ≥ 3) = 1 − P(X ≤ 2)</div>'
    + takeaway('系統性錯誤、PCR 重複與 caller 規則不在此模型內；不能直接當 sensitivity 或 LOD。'),
    'LOD＝偵測極限，需適當材料與重複實驗驗證。程式四捨五入顯示 1.000000 不代表機率等於 1。', 'compact')

add('附錄 · Cohort · 分母', '「未測到」不能直接填成「沒有變異」',
    '<div class="split"><article class="panel"><h3>假設一個基因</h3><p class="big">3 / 8</p><p>10 位個案中，只有 8 位可評估；<br>其中 3 位有符合定義的事件。</p></article><article class="panel"><h3>應報告</h3><p class="big">37.5%</p><p>可評估者中的比例；<br>另列 2 位未能評估及原因。</p></article></div>'
    + takeaway('不是直接報 3/10；也不能把多個 transcript 註解算成多個獨立事件。'),
    '原創假設例。跨 panel／批次先統一可評估範圍、FILTER 與事件識別。' + refs('maf'))

add('附錄 C · 名詞速查', '把容易混用的名詞分開記',
    table(['名詞', '本課用法'], [
        ['VAF／CCF', 'Allele 支持比例／帶變異的癌細胞比例'],
        ['Purity／ploidy', '腫瘤混合比例／整體倍體背景'],
        ['CNV／SV', '拷貝數改變／結構變異；部分事件可同屬兩者'],
        ['PoN／UMI', '多份正常背景資源／原始分子識別標記'],
        ['MAF／SEG', '變異註解表／區域分段結果'],
    ]), '名詞不等於證據；還是要回查它的輸入、模型、欄位定義與版本。', 'compact')

add('參考與課後資源', '從課堂例子，回到可查證的方法文件',
    '<div class="refs"><p><a href="../../lessons/lesson-02-materials.md">第二堂完整學員教材</a> · <a href="../pdf/lesson-02-materials.pdf">既有 PDF 講義</a></p>'
    '<p><a href="../../demos/lesson-02-somatic/README.md">合成資料與操作腳本</a> · <a href="../../sources/lesson-02-slides-sources.md">投影片來源、範圍與數值核對</a></p>'
    f'<p>{refs("mutect", "filter", "maf")}</p><p>{refs("sam", "bcf", "igv")}</p><p>{refs("cn", "liquid", "tmb")}</p></div>',
    '方法與網址於 2026-09-27 核對；播放可離線，外部參考需網路，本機教材連結需保留專案結構。')


CSS = r'''
:root{--ink:#183b40;--teal:#087c83;--warm:#a94b27;--paper:#fbf9f3;--scale:1}
*{box-sizing:border-box}body{margin:0;background:#152d32;color:var(--ink);font-family:"PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
#stage{width:1280px;height:720px;position:absolute;left:50%;top:calc(50% - 25px);transform:translate(-50%,-50%) scale(var(--scale));transform-origin:center}
.slide{width:1280px;height:720px;padding:38px 60px 64px;background:var(--paper);position:relative;display:none;overflow:hidden}.slide.active{display:block}
.eyebrow{font-size:16px;font-weight:700;letter-spacing:.15em;color:var(--teal);margin-bottom:18px}h2{font-size:42px;line-height:1.24;letter-spacing:-.02em;margin:0 0 24px;font-weight:800}h3{font-size:27px;line-height:1.35;margin:0 0 16px}p,li{font-size:26px;line-height:1.5;margin:12px 0}.intro{font-size:24px;margin:0 0 20px}.content{height:480px}strong{color:var(--teal)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.cards:has(article:nth-child(3):last-child){grid-template-columns:repeat(3,minmax(0,1fr))}.cards article,.panel{padding:24px;background:#edf2ef;border-top:5px solid var(--teal);border-radius:3px}.cards p{margin:0;font-size:25px}.split{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}
.flow{display:flex;align-items:stretch;gap:12px;margin:18px 0 28px}.flow>div{flex:1;display:flex;align-items:center;justify-content:center;min-height:85px;padding:16px 10px;background:#e1edeb;font-size:25px;text-align:center;border-radius:5px}.arrow{align-self:center;color:var(--teal);font-size:28px}
.takeaway{border-left:6px solid var(--warm);padding:12px 18px;background:#f4e9df;margin-top:26px;font-size:26px;line-height:1.4}.big{display:inline-block;font-size:58px!important;color:var(--teal);font-weight:800;line-height:1.2;margin:14px 0 20px!important}.equation{font-size:32px;line-height:1.5;text-align:center;background:#e1edeb;padding:18px 12px;margin:20px 0 25px;color:var(--teal);font-weight:700}.equation.small{font-size:27px;padding:12px}
table{width:100%;border-collapse:collapse;font-size:24px;line-height:1.45}th{background:var(--ink);color:white;text-align:left;padding:13px 16px}td{padding:15px 16px;border-bottom:1px solid #cbd7d4}tr:nth-child(even) td{background:#eef2ec}.compact table{font-size:23px}.compact th,.compact td{padding:10px 14px}.compact .takeaway{font-size:24px;margin-top:20px}.compact .equation{font-size:29px;margin:0 0 18px;padding:14px}
pre{background:#193a40;color:#f3f7f4;padding:20px 24px;border-radius:6px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:21px;line-height:1.55;margin:14px 0 24px;font-family:Menlo,Consolas,monospace}code{font-family:Menlo,Consolas,monospace}.commands{display:grid;gap:17px}.commands h3{font-size:24px;margin:0 0 5px}.commands pre{margin:0 0 5px;padding:9px 16px;font-size:20px;line-height:1.4}.commands p{font-size:22px;margin:0;line-height:1.35}.command-slide table{font-size:23px;margin-top:20px}
footer{position:absolute;bottom:14px;left:60px;right:60px;display:flex;align-items:end;gap:24px;border-top:1px solid #b6cbc7;padding-top:10px;font-size:15px;line-height:1.45;color:#415b62}.source{flex:1}.page{white-space:nowrap;color:var(--teal);font-weight:800}a{color:var(--teal);text-underline-offset:4px}
details{margin-top:20px;background:#e7eeeb;border:1px solid #b3c9c4;border-radius:6px;padding:14px 20px;font-size:24px;line-height:1.4}summary{cursor:pointer;font-weight:700;color:var(--teal)}.answer{margin-top:12px}.checks{padding-left:32px}.checks li{margin-bottom:16px}.refs p{font-size:25px;margin:22px 0}
.cover{background:#193d42;color:#f9f7ef}.cover .eyebrow{color:#a8d6c6}.cover h2{font-size:72px;margin-top:28px;line-height:1.16}.cover .subtitle{font-size:36px;color:#cbe3d5}.hero{margin-top:34px;font-size:32px;color:#f0d3ae;padding:20px 0;border-top:2px solid #d6ac75;width:760px}.speaker{position:absolute;bottom:85px;font-size:23px}.cover footer,.cover .page{color:#c9dcd4}.closing{background:#e2ece5}
.stats{display:flex;gap:90px;margin:15px 0 30px}.stats b{display:block;font-size:64px;color:var(--teal)}.stats span{display:block;font-size:23px}
.cells{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.cell{padding:14px 8px;background:#e1e7e3;border:2px solid #80958f;border-radius:12px;text-align:center}.cell b{display:block;font-size:23px}.cell span{display:block;font-size:23px;margin-top:8px}.cell.tumor{background:#f4e9df;border-color:var(--warm);color:var(--warm)}
.bar-chart{padding:20px 16px;background:#edf2ef}.bar-row{display:grid;grid-template-columns:170px 1fr 100px;align-items:center;gap:20px;margin:14px 0 24px;font-size:27px}.bar-track{height:42px;background:#dce5e0}.bar-track span{display:block;height:100%;background:var(--teal)}.axis-label{font-size:21px;margin:0;text-align:center}
.read-comparison{display:grid;grid-template-columns:1fr 1fr;gap:30px}.read-panel{background:#edf2ef;padding:18px}.read-panel h3{font-size:25px;margin-bottom:8px}.read-panel>p{font-size:20px;margin:4px 0;text-align:center}.read-stack{border-top:2px solid #8fa6a1}.read-row{height:32px;position:relative}.read-row>span{position:absolute;left:0;font-size:24px;line-height:32px}.read-row i{display:block;position:absolute;top:13px;height:8px;background:#658a87}.read-row b{position:absolute;left:49%;top:3px;background:#a94b27;color:white;font-size:19px;padding:1px 5px;line-height:24px}
nav{position:fixed;bottom:0;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:12px;height:54px;background:#0e262b;color:white;font-size:14px}button{font:inherit;border:1px solid #8fb1ac;background:#23454b;color:white;border-radius:6px;padding:8px 16px;cursor:pointer}button:hover{background:#345e63}button:disabled{opacity:.4;cursor:default}button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #dc843d;outline-offset:3px}#status{min-width:85px;text-align:center}dialog{width:min(940px,92vw);max-height:86vh;border:0;border-radius:12px;background:var(--paper);color:var(--ink);padding:28px}dialog::backdrop{background:#10282bcf}.menuhead{display:flex;justify-content:space-between;align-items:center}#toc{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}#toc button{text-align:left;background:#e2ece8;color:var(--ink);font-size:17px;padding:12px}#toc button[aria-current=true]{background:var(--ink);color:white}.help{font-size:16px}noscript{display:block;padding:30px;color:white}body.nojs #stage{position:static;transform:none;width:100%;height:auto}body.nojs .slide{display:block;margin-bottom:20px}body.nojs nav{display:none}
@media print{@page{size:1280px 720px;margin:0}body{background:white;-webkit-print-color-adjust:exact;print-color-adjust:exact}#stage{position:static;transform:none;width:1280px;height:auto}.slide{display:block!important;break-after:page;page-break-after:always}.slide:last-child{break-after:auto}nav,dialog{display:none!important}details:not([open])>div{display:block!important}summary{display:none}.answer{margin-top:0}}
.enriched .cards article{padding:18px 24px}.enriched .flow{margin:14px 0 18px}.enriched .takeaway{margin-top:12px}.enriched .walkthrough{font-size:24px;line-height:1.45;margin:12px 0 0;padding:10px 18px;border-left:5px solid var(--teal);background:#e7eeeb}.walkthrough b{color:var(--teal)}.enriched .commands{gap:12px}
.model-slide .cells{gap:10px}.model-slide .cell{padding:8px}.model-slide .equation{padding:10px 12px;margin:10px 0 14px}.model-slide .intro{margin-bottom:12px}.model-slide .panel{padding:16px 24px}.model-slide .big{margin:8px 0 10px!important}.model-slide details{margin-top:12px}
.enriched.compact .equation.small{padding:10px}
.biomarker-slide .flow>div{min-height:76px;padding:10px}.biomarker-slide .intro{margin-bottom:14px}
.fastqc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 20px}.fastqc-grid article{min-width:0;padding:12px 18px;background:#edf2ef;border-top:4px solid var(--teal)}.fastqc-grid h3{font-size:25px;line-height:1.3;margin:0 0 2px}.fastqc-grid .module-name{font-size:18px;line-height:1.3;color:#415b62;margin-bottom:8px}.fastqc-grid p{font-size:22px;line-height:1.4;margin:0;overflow-wrap:anywhere}.fastqc-slide.enriched .walkthrough{font-size:23px;margin-top:16px;padding:10px 18px}
#explain{width:min(1100px,94vw);padding:32px 42px}#explain h2{font-size:32px;margin:16px 0 24px}#explain h3{font-size:25px;margin:26px 0 8px}#explain p{font-size:24px;line-height:1.75;margin:8px 0}#explain .explain-source{font-size:16px;border-top:1px solid #b6cbc7;padding-top:18px}#explain .menuhead h3{margin:0}.reading-link{font-size:18px}
'''

JS = r'''
document.body.classList.remove('nojs');
const slides=[...document.querySelectorAll('.slide')],menu=document.querySelector('#menu'),explain=document.querySelector('#explain');
let current=0;
function fit(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1280,(innerHeight-68)/720));}
function go(index,write=true){current=Math.max(0,Math.min(slides.length-1,index));slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current);});document.querySelector('#status').textContent=`${current+1} / ${slides.length}`;document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;document.querySelectorAll('#toc button').forEach((b,i)=>b.setAttribute('aria-current',i===current));if(write)history.replaceState(null,'',`#slide-${current+1}`);}
function fromHash(){const n=Number(location.hash.replace('#slide-',''));go(Number.isInteger(n)&&n>0?n-1:0,false);}
function showExplanation(){document.querySelector('#explain-title').textContent=`${current+1} / ${slides.length} · ${slides[current].dataset.title}`;document.querySelector('#explain-body').replaceChildren(slides[current].querySelector('template').content.cloneNode(true));document.querySelector('#reading-link').href=`lesson-02-explanations.html#page-${current+1}`;explain.showModal();explain.scrollTop=0;}
async function full(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){document.querySelector('#status').textContent='請用瀏覽器全螢幕';}}
document.querySelector('#prev').onclick=()=>go(current-1);document.querySelector('#next').onclick=()=>go(current+1);document.querySelector('#overview').onclick=()=>menu.showModal();document.querySelector('#close').onclick=()=>menu.close();document.querySelector('#fullscreen').onclick=full;document.querySelector('#print').onclick=()=>window.print();
document.querySelector('#explanation').onclick=showExplanation;document.querySelector('#explain-close').onclick=()=>explain.close();
slides.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${String(i+1).padStart(2,'0')} · ${s.dataset.title}`;b.onclick=()=>{go(i);menu.close();};document.querySelector('#toc').appendChild(b);});
document.addEventListener('keydown',e=>{if(menu.open||explain.open||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea'))return;if(e.key===' '&&e.target.closest('button,summary,a'))return;let next=null;if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key))next=current+1;if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key))next=current-1;if(e.key==='Home')next=0;if(e.key==='End')next=slides.length-1;if(next!==null){e.preventDefault();go(next);}if(e.key.toLowerCase()==='f')full();if(e.key.toLowerCase()==='o')menu.showModal();if(e.key.toLowerCase()==='e')showExplanation();});
window.addEventListener('resize',fit);window.addEventListener('hashchange',fromHash);fit();fromHash();
'''


def main():
    sections = []
    readings = []
    explanations = load_explanations()
    assert set(explanations) == {s['title'].replace('<br>', ' ') for s in slides}
    for i, slide in enumerate(slides, 1):
        title = escape(slide['title'].replace('<br>', ' '), quote=True)
        example, explanation = explanations[slide['title'].replace('<br>', ' ')]
        worked = f'<p class="walkthrough"><b>理解這一頁｜</b>{escape(example)}</p>'
        body = slide['body'] + (worked if i != 1 else '')
        expanded = worked + explanation + f'<p class="explain-source">{slide["note"]}</p>'
        sections.append(f'<section class="slide enriched {slide["kind"]} {"active" if i == 1 else ""}" id="slide-{i}" data-title="{title}" aria-label="第 {i} 張：{title}"><header class="eyebrow">LESSON 02 / {slide["topic"]}</header><h2>{slide["title"]}</h2><div class="content">{body}</div><template>{expanded}</template><footer><div class="source">{slide["note"]}</div><div class="page">{i:02d} / {len(slides):02d}</div></footer></section>')
        readings.append(f'<article id="page-{i}"><h2>{i:02d} · {title}</h2>{expanded}<a href="lesson-02-somatic.html#slide-{i}">回到這張投影片</a></article>')
    html = '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第二堂｜癌症體細胞基因體分析</title><meta name="description" content="高雄長庚臨床生物資訊系列第二堂，學員版離線 HTML 投影片"><style>' + CSS + '</style></head><body class="nojs"><noscript>JavaScript 未啟用；以下顯示全部投影片。</noscript><main id="stage">' + ''.join(sections) + '</main><nav aria-label="投影片導覽"><button id="prev" aria-label="上一張">← 上一張</button><span id="status" aria-live="polite"></span><button id="next" aria-label="下一張">下一張 →</button><button id="overview">目錄 O</button><button id="fullscreen">全螢幕 F</button><button id="print">列印全部</button></nav><dialog id="menu" aria-labelledby="menu-title"><div class="menuhead"><h3 id="menu-title">第二堂 · 投影片目錄</h3><button id="close">關閉</button></div><p class="help">方向鍵／空白鍵翻頁 · Home／End 首末頁 · Esc 關閉目錄<br>HTML 可離線播放；實作需要完整專案與工具。</p><div id="toc"></div></dialog><script>' + JS + '</script></body></html>'
    output = ROOT / 'output/slides/lesson-02-somatic.html'
    html = html.replace('<button id="fullscreen">', '<button id="explanation">逐頁詳解 E</button><button id="fullscreen">')
    html = html.replace('<script>', '<dialog id="explain" aria-labelledby="explain-title"><div class="menuhead"><a class="reading-link" id="reading-link" href="lesson-02-explanations.html" target="_blank" rel="noopener">閱讀／列印全部詳解 ↗</a><button id="explain-close">關閉 Esc</button></div><h2 id="explain-title"></h2><div id="explain-body"></div></dialog><script>', 1)
    html = html.replace('JavaScript 未啟用；以下顯示全部投影片。', 'JavaScript 未啟用；以下顯示全部投影片。<a href="lesson-02-explanations.html">閱讀全部詳解</a>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding='utf-8')
    reading_css = 'body{max-width:980px;margin:40px auto;padding:0 28px;background:#fbf9f3;color:#183b40;font-family:"PingFang TC","Microsoft JhengHei",sans-serif}h1{font-size:34px}h2{font-size:30px;line-height:1.5}h3{font-size:23px;margin:28px 0 8px}p{font-size:22px;line-height:1.85;margin:10px 0}article{padding:30px 0;border-bottom:1px solid #b6cbc7;scroll-margin-top:20px}.walkthrough{padding:16px;background:#e7eeeb;border-left:5px solid #087c83}.explain-source{font-size:16px}a{color:#087c83}nav{line-height:2;font-size:18px}nav a{display:block}@media print{body{margin:0;max-width:none}nav{display:none}article{break-before:page;border:0}p{font-size:12pt}h2{font-size:18pt}h3{font-size:14pt}.explain-source{font-size:10pt}}'
    toc = ''.join(f'<a href="#page-{i}">{i:02d} · {escape(s["title"].replace("<br>", " "))}</a>' for i, s in enumerate(slides, 1))
    reading_html = '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第二堂｜逐頁詳解</title><style>' + reading_css + '</style></head><body><h1>癌症體細胞基因體分析 · 逐頁詳解</h1><p>與投影片逐頁對應的學員閱讀版。數值均為教學假設或合成資料，不是病人檢測結果。可使用瀏覽器列印完整說明。</p><nav aria-label="詳解目錄">' + toc + '</nav>' + ''.join(readings) + '</body></html>'
    output.with_name('lesson-02-explanations.html').write_text(reading_html, encoding='utf-8')
    print(f'{len(slides)} slides → {output}')
    for i, slide in enumerate(slides, 1):
        print(f'{i:02d} {slide["title"].replace("<br>", " ")}')


if __name__ == '__main__':
    main()
