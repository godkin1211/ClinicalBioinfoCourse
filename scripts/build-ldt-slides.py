"""Build the 2026-10-24 LDT introduction: offline HTML, notes and original SVGs.

Reuses Lesson 03's established presentation controls and visual foundation.
All numerical graphics below are explicitly synthetic teaching examples.
No clinical analysis or analytical validation is performed by this script.
"""
from base64 import b64encode
from html import escape
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/slides'
FIG = ROOT / 'figures/ldt-20261024'
BASE = runpy.run_path(str(ROOT / 'scripts/build-lesson03-slides.py'))
SLIDES = []
SOURCES = {
    'jct': ('醫策會 LDTs 簡介', 'https://www.jct.org.tw/np-1304-1.html'),
    'apply': ('衛福部申請須知：115/03/13', 'https://dep.mohw.gov.tw/DOMA/cp-5177-65615-106.html'),
    'lab': ('衛福部認證資格：115/03/19', 'https://dep.mohw.gov.tw/DOMA/cp-5177-65471-106.html'),
    'security': ('衛福部資通系統切結書', 'https://dep.mohw.gov.tw/DOMA/cp-5177-82803-106.html'),
    'training': ('衛福部人員訓練須知', 'https://dep.mohw.gov.tw/DOMA/cp-5177-77135-106.html'),
    'roy': ('AMP/CAP：生物資訊流程驗證，2018', 'https://pubmed.ncbi.nlm.nih.gov/29154853/'),
    'jennings': ('AMP/CAP：腫瘤 NGS 驗證，2017', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6941185/'),
    'giab': ('NIST：GIAB FAQ', 'https://www.nist.gov/programs-projects/faqs-genome-bottle'),
    'fastqc': ('FastQC：逐位置品質', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html'),
    'mutect': ('GATK：somatic 分析流程', 'https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2'),
    'igv': BASE['SOURCES']['igv'],
    'deseq': BASE['SOURCES']['deseq'],
    'sam': ('SAM／BAM 格式', 'https://www.htslib.org/doc/sam.html'),
    'umi': ('fgbio：分子共識', 'https://fulcrumgenomics.github.io/fgbio/tools/latest/CallDuplexConsensusReads.html'),
}


def refs(keys):
    return ' · '.join(f'<a href="{SOURCES[k][1]}" target="_blank" rel="noopener noreferrer">{SOURCES[k][0]}</a>' for k in keys.split())


def add(topic, title, body, takeaway, notes, origin, sources='', kind=''):
    SLIDES.append(dict(topic=topic, title=title, body=body, takeaway=takeaway,
                       notes=notes, origin=origin, sources=sources, kind=kind))


def cards(*items):
    return '<div class="cards">' + ''.join(f'<article><h3>{h}</h3><p>{p}</p></article>' for h, p in items) + '</div>'


def table(headers, rows):
    return BASE['table'](headers, rows)


def flow(*items):
    return BASE['flow'](*items)


def p(text):
    return f'<p>{text}</p>'


def text(x, y, label, size=24, color='#183b40', anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(str(label))}</text>'


def rect(x, y, w, h, color='#e1edeb', stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="{stroke}"/>'


def line(x1, y1, x2, y2, color='#496568', width=2, dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'


def svg(name, title, elements, width=700, height=380):
    FIG.mkdir(parents=True, exist_ok=True)
    result = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" fill="#fffdf8"/><g font-family="PingFang TC,Microsoft JhengHei,sans-serif">{elements}</g></svg>'
    (FIG / name).write_text(result)
    return result


def figure(name, alt, explanation):
    data = b64encode((FIG / name).read_bytes()).decode()
    return f'<div class="ldt-figure"><img src="data:image/svg+xml;base64,{data}" alt="{escape(alt)}"><article>{explanation}</article></div>'


def make_figures():
    # FastQC-like summary, not actual FastQC output or validation data.
    s = text(65, 28, '人工示意：每個 read 位置的品質分布', 25)
    for q in [0, 10, 20, 30, 40]:
        y = 300 - q * 6
        s += line(65, y, 665, y, '#d6e1df') + text(52, y + 7, q, 20, anchor='end')
    vals = [(1, 35), (25, 36), (50, 35), (75, 33), (100, 29), (125, 23), (150, 18)]
    points = []
    for i, (pos, median) in enumerate(vals):
        x, y = 95 + i * 88, 300 - median * 6
        spread = 12 + i * 3
        s += line(x, y - spread - 8, x, y + spread + 8)
        s += rect(x - 16, y - spread / 2, 32, spread, '#f3d885', '#596b6c')
        s += line(x - 16, y, x + 16, y, '#a94b27', 3) + text(x, 328, pos, 20, anchor='middle')
        points.append(f'{x},{y+3}')
    s += f'<polyline points="{" ".join(points)}" fill="none" stroke="#287aa7" stroke-width="3"/>'
    s += text(8, 45, 'Q', 24) + text(350, 363, 'read 內的位置（不是基因體座標）', 23, anchor='middle')
    svg('quality.svg', '人工品質箱形圖：read 末端品質逐漸下降', s)

    s = text(50, 28, '相同平均深度 1000×；低覆蓋區卻不同', 25)
    for j, values in enumerate([[1000]*4, [1400, 1300, 1250, 50]]):
        x0 = 65 + j * 330
        s += text(x0 + 125, 65, ['樣本 A', '樣本 B'][j], 25, anchor='middle')
        for i, value in enumerate(values):
            x, h = x0 + i * 66, value / 7
            s += rect(x, 290-h, 45, h, '#087c83' if value >= 200 else '#a94b27')
            s += text(x+22, 280-h, value, 18, anchor='middle') + text(x+22, 320, f'區{i+1}', 20, anchor='middle')
        s += line(x0-8, 290, x0+258, 290)
        s += line(x0-8, 290-200/7, x0+258, 290-200/7, '#a94b27', 2, '5 4')
    s += text(350, 360, '虛線 200× 僅為教學標記；四區假設等長', 21, anchor='middle')
    svg('coverage.svg', '四個等長區域的覆蓋比較，樣本 B 第四區只有 50 倍', s)

    s = text(30, 35, '兩種方式都得到 400 reads', 28)
    for j in range(2):
        x0 = 30 + j*345
        s += text(x0, 80, ['20 分子 × 每個讀 20 次', '400 分子 × 每個讀 1 次'][j], 24)
        for i in range(20):
            x, y = x0 + (i % 5)*53, 120 + (i // 5)*38
            s += rect(x, y, 38, 22, '#a94b27' if i == 0 else '#087c83')
        s += text(x0, 302, ['1 個分子錯誤 → 20/400', '1 個分子錯誤 → 1/400'][j], 22)
        s += text(x0, 341, ['表觀 5%', '表觀 0.25%'][j], 28, '#a94b27')
    s += text(375, 277, '右側僅畫出其中 20 個分子', 18)
    svg('molecules.svg', '等量擴增假設下，一個原始分子對兩種文庫的影響不同', s)

    s = text(25, 35, '10 個細胞：1 個腫瘤細胞＋9 個正常細胞', 25)
    for i in range(10):
        x, y = 30+(i%5)*132, 65+(i//5)*118
        s += rect(x, y, 110, 92, '#f4e9df' if i == 0 else '#e1edeb')
        s += text(x+55, y+30, '腫瘤' if i == 0 else '正常', 21, anchor='middle')
        s += text(x+55, y+65, 'REF/ALT' if i == 0 else 'REF/REF', 19, anchor='middle')
    s += text(350, 324, 'ALT 共 1 份 ÷ 全部 allele 20 份＝5%', 27, anchor='middle')
    s += text(350, 363, '前提：全為二倍體、等量 DNA 貢獻、沒有拷貝數變化', 20, anchor='middle')
    svg('vaf-mixture.svg', '二倍體混合示意：10% 腫瘤細胞可對應 5% VAF', s)

    s = text(35, 27, '只畫出兩案例各 20 條 ALT reads；REF reads 未畫', 23)
    for j in range(2):
        x0 = 35 + j*350
        s += text(x0+145, 66, ['A：方向及位置較分散', 'B：同向且集中末端'][j], 23, anchor='middle')
        s += line(x0+150, 86, x0+150, 313, '#a94b27', 2, '4 4')
        for i in range(20):
            y = 92+i*11
            start = x0+20+(i%5)*17 if j==0 else x0+20
            end = x0+215+(i%4)*13 if j==0 else x0+158
            s += line(start, y, end, y, '#72969b', 5)
            s += rect(x0+147, y-4, 6, 8, '#a94b27')
            s += text(end+9, y+5, '→' if j==1 or i<10 else '←', 18)
        s += text(x0+145, 353, '20/400＝5% VAF', 25, anchor='middle')
    svg('read-evidence.svg', '人工 ALT 讀段排列：兩個 5% VAF 有不同偏差模式', s)

    s = text(30, 32, '同一基因，總量與組裝方式是兩個問題', 25)
    rows = [('形式 A', [1,2,3], 100), ('形式 B', [1,3], 230)]
    for label, exons, y in rows:
        s += text(20, y+28, label, 24)
        s += line(155, y+16, 660, y+16, '#739192', 3)
        for exon in exons:
            x = 160+(exon-1)*195
            s += rect(x, y-10, 110, 52, '#087c83')+text(x+55, y+25, f'E{exon}', 26, '#ffffff', 'middle')
    s += '<path d="M215 218 Q410 187 605 218" fill="none" stroke="#a94b27" stroke-width="4"/>'
    s += text(410, 183, 'E1–E3 junction', 23, '#a94b27', 'middle')
    s += text(350, 330, 'E1 內的 read：支持基因表現；跨 E1–E3：支持局部跳躍', 21, anchor='middle')
    s += text(350, 367, '概念圖，非實際基因座標；不是 DNA 缺失的直接證據', 20, anchor='middle')
    svg('splicing.svg', '可變剪接示意：同一基因有包含或跳過 E2 的 RNA 形式', s)

    s = text(40, 30, '人工稀釋測試：每濃度測試 20 次', 25)
    for value in [0, 50, 100]:
        y = 295-value*2.1
        s += line(75, y, 660, y, '#cbd9d6', 1, '4 3')+text(62, y+6, f'{value}%', 20, anchor='end')
    for i, (vaf, count) in enumerate(zip(['0.5%','1%','2%','5%','10%'],[4,14,19,20,20])):
        x, y = 110+i*125, 295-(count/20*100)*2.1
        s += f'<circle cx="{x}" cy="{y}" r="8" fill="#087c83"/>'
        s += text(x, y-14, f'{count}/20', 21, anchor='middle')+text(x, 327, vaf, 22, anchor='middle')
    s += text(350, 367, '輸入 VAF；點為觀察檢出率，不是已確認的 LoD', 22, anchor='middle')
    svg('lod.svg', '合成稀釋例子：低濃度檢出率下降，19/20 不足以單獨證明偵測極限', s)

    s = text(30, 35, '相同比對檔，不同軟體／參數可能得到不同候選', 25)
    for x, y, w, h, label in [(25,95,180,80,'固定測試資料'), (270,65,185,65,'現行版本 v1'),(270,175,185,65,'候選版本 v2'),(515,95,160,145,'差異審查')]:
        s += rect(x,y,w,h)+text(x+w/2,y+h/2+8,label,23,anchor='middle')
    s += line(205,135,260,100)+line(205,135,260,205)+line(455,100,505,135)+line(455,205,505,185)
    s += text(350,290,'新增／消失／VAF／註解／QC 差異，都要有原因',24,anchor='middle')
    s += text(350,337,'通過預設標準 → 核准上線；失敗 → 保留 v1 並排查',23,anchor='middle')
    svg('versions.svg', '版本更新前的回歸測試與差異審查概念流程', s)


def make_slides():
    add('2026.10.24 · 生物資訊入門', 'LDTs 的生物資訊<br>從檢體訊號到可信的檢測結果',
        '<p class="subtitle">看懂資料、品質與證據，不必先會寫程式</p><p class="hero">檢測範圍 → 資料品質 → 分析證據 → 驗證與追溯</p><p class="speaker">奇美醫院精準醫學核心實驗室組長邱家軍</p>', '',
        '這堂課整合原系列前三堂內容，以基因體與轉錄體的檢測情境說明生物資訊。LDTs 是 laboratory developed tests，中文為實驗室開發檢測；它不是某一種定序技術，也不是單一軟體。\n\n本課讓沒有程式經驗的學員能提出正確問題：測了什麼、資料夠不夠、分析如何得到答案、答案的限制在哪裡。主課程 30 頁，另有 4 頁備查。示意數字不代表臨床放行規則，也不代表本課完成了檢測驗證。',
        '整合 Lesson 01–03；新增 LDT 品質主線', 'jct', 'cover')

    add('01 · 先從問題出發', '兩份報告都寫 5%：你會一樣相信嗎？',
        cards(('同樣的數字', '兩個候選位點都有 400 條納入計算的 reads，其中 20 條支持 ALT，因此都是 5% VAF。'),
              ('不同的證據', 'A 的支持分布較分散；B 的支持都來自同一方向、集中在讀段末端。還能直接當作同等可信嗎？'))
        +p('Read 是一次讀出的短序列；ALT 是相對參考序列的替代形式。VAF（變異等位基因頻率）是支持 ALT 的讀段比例，不是「真實的機率」。'),
        '生物資訊的工作不是把數字算出來，而是保留「為什麼可以相信它」的證據。',
        '這是延伸第二堂的人工案例，不是兩位真實病人的結果。400 條 reads 的分母必須先知道如何篩選，是否已處理重複、低品質與重疊配對。20/400 是一個觀察比例；光靠比例無法判斷真偽、來源或臨床重要性。\n\nA 也不能直接宣布通過；較好的分布只是其中一項支持。B 則需要排查方向偏差、末端品質、比對、文庫設計與原始分子是否獨立。課程最後會用同一案例練習如何交付有依據的結論。', 'L02：案例與讀段證據', 'mutect')

    add('01 · 生物資訊的角色', '從「測得到」到「有幫助」，中間有三道問題',
        flow('分析效能<br>測量是否可靠？','臨床效度<br>與疾病是否相關？','臨床效益<br>能否改善決策？')
        +cards(('生物資訊直接影響分析效能', '讀段對錯位置、漏掉變異、算錯分母或套錯版本，都可能改變檢測結果。'),
               ('技術可靠仍不等於有臨床效益', '找到變異後，仍需疾病背景、適應症與證據評估；軟體 PASS 不代表一定可用藥。')),
        '本課聚焦分析證據與品質；不以演算法分數取代臨床判斷。',
        '分析效能關心測量是否正確、可重複，以及在什麼條件下會失敗。臨床效度關心檢測結果與目標疾病或狀態的關聯。臨床效益則關心使用檢測後，是否能帶來有意義的決策或健康結果改善。這三者不能互換。\n\n例如準確偵測到一個罕見序列差異，只完成了測量層級的一部分；若沒有足夠疾病或治療證據，不能自動形成用藥建議。驗證生物資訊流程是必要的一環，但不是完整臨床效益研究的替代品。', 'L01：平台限制；L02：技術可信度；L03：推論界線', 'roy jennings')

    add('01 · 臺灣 LDTs 脈絡', '實驗室認證、施行計畫與流程驗證，不是同一件事',
        table(['層次','關心什麼','生物資訊如何配合'],[
            ['實驗室資格','執行單位具備適用的品質與能力條件','人員、文件、設備／系統及紀錄管理'],
            ['檢測施行計畫','醫療機構申請的用途、項目與施行內容','說明方法、分析範圍、限制與合作分工'],
            ['分析方法的驗證','這套流程在聲稱條件下能否可靠產生結果','實測性能、QC、異常處理與變更評估'],
        ])+p('LDTs＝實驗室開發檢測。醫策會提供審查資訊；衛福部 2026/03 更新申請須知與認證資格。'),
        '技術建議不等於臺灣法定條文；本課不是申請核准或訓練時數採認的證明。',
        '醫策會簡介指出，自行開發的檢測已納入臺灣特管辦法的管理脈絡。衛福部 115 年 3 月 13 日的申請資訊說明，醫療機構施行 LDTs 應擬定施行計畫並經核准；115 年 3 月 19 日另有實驗室認證資格公告。這些行政層次不能以「買了軟體」或「實驗室有某一認證」概括取代。\n\n本頁只用於定位生物資訊工作，不逐條解釋個案適用法規。國際 AMP/CAP 文件是技術建議，不直接當作臺灣法規。資料查核日為 2026-10-15；實際申請、變更與人員訓練採認仍應依主管機關最新公告及機構核准內容辦理。', '新增：臺灣官方制度脈絡', 'apply lab', 'compact')

    add('02 · 先寫清楚檢測規格', '選軟體之前，先定義「我們承諾測到什麼」',
        table(['必須定義','人工範例：FFPE 腫瘤 DNA panel'],[
            ['檢體與用途','接受何種組織與品質？要回答哪個臨床問題？'],
            ['目標範圍','哪些基因、外顯子、座標及版本屬於可報告範圍？'],
            ['事件與性能','SNV、短 indel、CNV、SV 分別有什麼驗證證據？'],
            ['例外與輸出','低輸入、覆蓋不足或結果不確定時，如何處理及揭露？'],
        ]),
        '「做了 NGS」太籠統；檢測能力必須連同檢體、區域、變異類型與流程版本一起說。',
        'Intended use 是預期用途，包含對象、檢體、問題與如何使用結果。Reportable range 是經定義而可報告的範圍，不是儀器偶然讀到的所有位置。兩者應在開發及驗證之前清楚界定。\n\n一套針對 FFPE 小型 DNA 變異建立的流程，不能因為程式也輸出了 CNV，就宣稱具有同樣可靠的 CNV 檢測能力；由組織擴充到血漿，也會改變低濃度、污染與背景錯誤問題。新增聲稱需要相應證據，不能只修改報告文字。', 'L01：選平台；L02：研究設計；新增驗證定位', 'jennings')

    add('02 · 技術選擇', 'Array、Panel、WES、WGS：涵蓋更多，不等於每處都更可靠',
        table(['平台','怎麼量測','對結果的主要限制'],[
            ['SNP array','用探針量測預設位點的等位基因訊號','可看基因型／部分 CNV；不是全面找新序列變異'],
            ['Targeted panel','集中定序選定基因或區域','可聚焦深度；目標以外通常不能評估'],
            ['WES 全外顯子','捕捉並定序設計中的外顯子等區域','捕捉不均；不是每個 exon 都有足夠覆蓋'],
            ['WGS 全基因體','較廣地讀取基因體序列','重複區仍困難；各類事件仍需專用方法'],
        ]),
        '選擇依預期用途與已驗證能力；RNA-seq 則回答表現、剪接或部分融合等不同問題。',
        '第一堂的比較可濃縮為：不同技術取得的是不同訊號。SNP array 利用已設計的探針，不是像定序一樣直接觀察所有可能的新序列；Panel、WES 和 WGS 的差別首先是目標設計與採樣範圍，而不是一個由差到好的排行榜。\n\n在固定資源下，涵蓋更廣可能需要在深度、成本、解讀負擔與周轉時間間取捨。測到某個位置也不等於達到某種低頻變異的偵測能力。應看每個目標區的有效覆蓋、序列環境及經驗證的變異類型。', 'L01：1.1、WES/WGS 選擇', '', 'compact')

    add('02 · 訊號從哪裡來', '儀器讀到的是短片段，不是完整的基因答案',
        flow('DNA／RNA<br>抽取核酸','文庫製備<br>片段＋接頭','定序<br>讀出序列','Reads<br>再由軟體重建')
        +cards(('Library＝可被定序的分子集合', '接頭讓分子進入定序流程；sample index 協助分開混合上機的樣本，不是基因名稱。'),
               ('Read＝一次讀出的序列', 'Paired-end 從同一片段兩端讀取；R1、R2 不是兩位病人，也不一定是兩個獨立分子。')),
        '原始分子、PCR 複本、reads 是不同層次；生物資訊必須知道文庫怎麼做。',
        '高通量定序同時讀取大量分子片段。為了讓儀器辨識，核酸經片段化、接頭添加或其他平台特定製備步驟成為文庫；RNA 常先轉成 cDNA 再進行定序。因此分析不是憑空找基因，而是根據取得的片段與參考資料推估來源。\n\nSample index 標識樣本；UMI 則用於標識原始分子家族，兩者目的不同。Paired-end 的兩端可能提供定位或結構訊息，但若兩端重疊，不能把同一個分子的同一位置不加考慮地當成兩份獨立支持。', 'L01：定序資料；L02：文庫；L03：3.4–3.5')

    add('02 · 檔案不是附件而已', 'FASTQ → BAM／CRAM → VCF：每一步留下不同證據',
        table(['檔案','內容與用途','不能把它當成什麼'],[
            ['FASTQ','每條 read 的序列與逐鹼基品質','尚未告訴你位於哪個基因'],
            ['BAM／CRAM','比對位置、方向、配對、序列與品質','比對成功不代表位置一定正確'],
            ['VCF','候選變異、樣本欄位、品質與 FILTER','沒有一列不等於那個位置是正常'],
            ['FASTA／BED／GTF','參考序列／目標區間／基因與轉錄本註解','這些是分析依據，不是病人實測資料'],
        ]),
        '結果表方便閱讀，卻不能取代原始讀段、比對證據、QC 與流程紀錄。',
        'FASTQ 的品質分數描述儀器對每個鹼基判讀的信心。BAM／CRAM 加上定位與比對資訊後，才能回查某候選變異附近的讀段。VCF 以事件為單位摘要，DP、AD、AF 等欄位的定義應回到 header 與工具文件，不應只按縮寫猜測。\n\nFASTA 是序列參考，文字 BED 常標示分析目標區，GTF 標示基因與轉錄本結構。索引加速區域查詢，不會新增測量證據。CRAM 解碼可能依賴相符的參考序列；只留下結果試算表會使後續稽核與再分析失去重要依據。', 'L01：2.3；L02：3.3；L03：第四章', 'sam', 'compact')

    add('02 · 容易忽略的錯誤', '資料內容沒壞，也可能配錯人、用錯地圖',
        cards(('身分核對：檔案屬於誰？', '串接個案、檢體、文庫及定序 ID；核對 tumor–normal 配對。SNP fingerprint 是多個基因型特徵的比對，不靠單一 SNP 判斷。'),
               ('版本核對：座標代表哪裡？', 'GRCh37 與 GRCh38 不可直接混用；FASTA、目標 BED、GTF 與註解版本應相容。改掉檔名不會轉換座標。'))
        +p('Checksum（校驗碼）可檢查傳輸前後檔案是否一致，但無法證明採檢時沒有配錯病人。'),
        '先確認身分與座標，再看漂亮的品質分數；否則可能精確地分析了錯誤的資料。',
        'Metadata 是描述資料背景的資訊，例如檢體來源、採樣時間、批次與分析版本。這不是可有可無的行政欄位，而是決定分析能否正確解讀的必要輸入。\n\n相同個案可能有不同病灶與時間點，不能因姓名相同就任意配對。參考基因體也不是「正常人的唯一序列」，而是比對及報告的座標基準。即使都標示 GRCh38，仍需核對實際 FASTA、contig 與輔助序列。重新定位座標、更新註解或變更參考都應依受控流程驗證。', 'L01：reference；L02：樣本表；L03：5.1', 'roy')

    add('03 · 品質從檢體開始', '軟體可以識別風險，不能補回沒有進來的分子',
        table(['前分析問題','為什麼影響結果','生物資訊可以做什麼'],[
            ['FFPE 損傷','固定與保存可使 DNA 斷裂或產生損傷','查看片段、替換型態與方向偏差；不能將所有 C>T 都刪除'],
            ['低輸入／低腫瘤含量','獨立分子少；正常細胞稀釋腫瘤訊號','評估有效深度、分子數與低頻訊號限制'],
            ['RNA 降解／文庫差異','可讀到的 RNA 區段與類型改變','對照 RIN／DV200、3′ 偏差、rRNA 與建庫設計'],
        ]),
        'QC 異常要回到檢體與文庫；補定序不一定能改善低輸入或系統性損傷。',
        'FFPE 是福馬林固定石蠟包埋；胞嘧啶脫胺可能導致 C>T 或互補方向 G>A 的假訊號，但真實變異也可以是相同替換，因此必須合併更多證據。\n\nRNA 的 RIN 反映整體 RNA 完整度的相關特徵；DV200 是長於 200 個核苷酸的 RNA 片段比例，兩者不是同一個分數。可接受範圍需依檢測用途與方法建立。生物資訊可提示損傷、混合與覆蓋問題，卻不能把已降解或從未抽到的分子重建成真正的實驗證據。', 'L02：4.1；L03：3.1–3.3', 'jennings', 'compact')

    add('03 · 三層 QC', '整批成功 ≠ 每個樣本成功 ≠ 每個位置都可判讀',
        flow('Run 層級<br>儀器／批次／對照','Sample 層級<br>身分／污染／分子量','Locus 層級<br>目標覆蓋／比對／偏差')
        +cards(('每一層都有自己的放行條件', '整批定序正常，某個樣本仍可能輸入不足；樣本平均深度足夠，關鍵 exon 仍可能沒有可用證據。'),
               ('異常必須對應行動', '依事前規則決定重抽取、重建庫、補測、限制可報告範圍或判為無法判定，並保留核准紀錄。')),
        '品質控制是有證據的決策，不是一個總合格率或滿版綠燈。',
        'Run 是一次定序批次；sample 是單一檢體或文庫；locus 是特定位置或區域。三個層級可以同時出現不同狀態，因此不能只用總 reads 數或整批 Q30 放行所有結果。\n\nQC 門檻應與驗證聲稱、檢體與變異類型連動，且事前訂定。發現異常後要留下原始報表、原因分析、處理與複核，而不是反覆調整參數直到通過。品質趨勢也可用來發現試劑、設備或軟體更新後的漂移。', 'L01：QC；L02：下機 QC；L03：第五章', 'roy jennings')

    add('03 · 看圖練習', 'FastQC：先看座標與分布，不要只看 PASS／FAIL',
        figure('quality.svg','人工 FastQC 類型品質圖，橫軸為讀段位置，尾端品質下降',
            '<h3>這張圖怎麼看？</h3><p>橫軸是 read 內的位置；縱軸 Q 越高，估計的鹼基錯誤率越低。</p><p>箱體：25–75 百分位；紅線：中位數；藍線：平均值。</p><p>末端下降時，核對接頭、讀長與保留量，再評估修剪。這不是臨床放行標準。</p>'),
        'Q30 約對應 0.1% 的單鹼基判讀錯誤率，不代表「這個變異 99.9% 真實」。',
        '本圖為人工箱形圖，不是執行 FastQC 得到的報表。真正 FastQC 的每個位置彙整許多 reads；箱體顯示 25–75 百分位，鬚線是 10–90 百分位。不能把藍色平均線當成某條 read 的品質。\n\nBase quality 問鹼基是否讀對；mapping quality 問定位是否可信，兩者不同。Adapter content、GC、序列重複及過度代表序列也要一起檢查。RNA 高表現基因或 amplicon 文庫可能自然產生大量重複序列，不能一見警示就判檢體失敗。修剪後還要確認可用讀段及定位能力，不能只追求燈號變綠。', 'L02：FastQC；L03：5.2', 'fastqc', 'fig')

    add('03 · 區域品質', '平均 1000×，仍可能漏掉最重要的區域',
        figure('coverage.svg','合成等長區段：樣本 A 全為1000倍；B為1400、1300、1250、50倍',
            '<h3>平均值掩蓋缺口</h3><p>四個等長區域中，A 與 B 的平均深度都是 1000×。</p><p>B 的區域 4 只有 50×；其他位置再深，也無法補償此處缺乏證據。</p><p>應查看每個目標的有效覆蓋，以及達到已驗證要求的比例。</p>'),
        '報告陰性之前，先問「這個位置在這份檢體中，是否真的具備足夠偵測能力？」',
        'Coverage 可以描述某位置的覆蓋深度，也可能描述符合條件的目標區比例，讀報表時應確認分母。原始 read depth 不一定等於通過品質、去除重複或 UMI 共識後的有效深度。\n\n這個例子故意使用四個等長區域，讓平均值可直接算術平均；真實 exon 長度不同時，需依實際定義加權。圖中 200× 虛線只是教學標記，不能作為通用門檻。即使超過某深度，重複序列、低複雜度、indel 與系統性錯誤仍可能限制判讀。', 'L01：coverage；L02：有效深度', 'jennings', 'fig')

    add('03 · 獨立證據', '400 reads，可能只是 20 個原始分子被重複讀取',
        figure('molecules.svg','等量擴增人工示意：20個分子各20次與400個分子各1次',
            '<h3>為什麼會放大錯誤？</h3><p>PCR（聚合酶連鎖反應）擴增 DNA 時，也可能複製原始分子上的錯誤。</p><p>左例每個分子等量擴增：一個錯誤分子就能貢獻 5% reads。</p><p>UMI 用分子標記追蹤讀段家族；但不能自動修正所有早期損傷或比對錯誤。</p>'),
        '重複讀取增加的是讀段數，不一定增加獨立分子；UMI 不是萬能除錯器。',
        '此算例假設每個原始分子等量擴增與讀取。20 個分子各讀 20 次時，一個帶錯誤的分子可產生 20/400＝5% 的表觀訊號；400 個分子各讀一次時，一個分子只占 1/400＝0.25%。真實 PCR 並非完全等量，偏差可能更複雜。\n\nUMI 是 unique molecular identifier，標記與原始分子相關的識別碼，協助聚合同家族 reads 並建立 consensus。須核對標記加入時間、碰撞、家族大小與共識規則。正反方向都有 reads 不等於 duplex consensus；後者需要辨識同一原始 DNA 雙股的對應證據。', 'L02：4.2、獨立分子問題；L03：3.4', 'umi', 'fig')

    add('04 · 分析到底在做什麼', '比對、判定、篩選、註解：四個步驟回答不同問題',
        table(['步驟','白話問題','需要避免的誤解'],[
            ['Alignment 比對','這條 read 最可能來自哪個位置？','對得上不等於唯一、正確地定位'],
            ['Calling 候選判定','差異較像真實變異，還是背景錯誤？','不是只計算 ALT 是否超過固定比例'],
            ['Filtering 篩選','哪些候選有污染、偏差或低品質疑慮？','刪除所有失敗列會遺失稽核理由'],
            ['Annotation 註解','對應哪個基因、轉錄本與已知資料？','資料庫有收錄不會讓錯誤讀段變真'],
        ]),
        '先有可靠的測量證據，再討論生物意義；流程跑完不是品質驗證完成。',
        'Caller 會依模型整合序列、品質、局部組裝與背景資訊，並非單純投票表決。Germline 與 somatic 的模型假設可能不同，不能只把腫瘤樣本套進預設二倍體基因型模型。\n\n以 Mutect2 為例，候選產生之後仍要進行適用的篩選，污染與方向性資訊可以影響結果。Annotation 再把已定義的序列事件連到基因、轉錄本、族群與疾病資料。必須記錄參考、資料庫及轉錄本版本；變更註解也可能改變報告，即使原始 reads 不變。', 'L01：定序流程；L02：3.1–3.3', 'mutect', 'compact')

    add('04 · 腫瘤分析的背景', 'Tumor-only 不是「只把 normal 那一步省掉」',
        cards(('Tumor–normal：同一人的配對比較', '正常檢體提供個體原有變異的證據，協助區分 germline 與腫瘤特有訊號；仍須核對來源、深度及污染。'),
               ('Tumor-only：留下更多來源不確定性', '可用族群頻率、技術背景及模型篩選，但不能可靠排除所有 germline。資料庫沒收錄不等於 somatic。'))
        +p('Germline 與 somatic 描述變異的來源；50% 與 5% 則是觀察比例，不能直接互相對號入座。'),
        '正常檢體也要選對：血液腫瘤或克隆性造血時，血液不一定是理想 normal。',
        'Matched normal 是同一人的非腫瘤參考檢體，而非任意一份正常人資料。Panel of normals（PoN）彙整多份正常樣本的技術背景，目的與個人的 germline 比較不同，不能互相取代。\n\n腫瘤內同時存在原有 germline 與後天 somatic 變異；純度、拷貝數、嵌合與抽樣都可能改變 VAF。Normal 沒有看到 ALT 也要考慮是否有足夠深度。涉及潛在 germline 發現，需依既定同意、回報及專業協作程序處理，不能只由分析者單憑比例決定。', 'L02：第一、二章', 'mutect')

    add('04 · 比例的分母', 'VAF 是 allele 的讀取比例，不是癌細胞百分比',
        figure('vaf-mixture.svg','一個腫瘤雜合細胞與九個正常二倍體細胞共二十份allele',
            '<h3>這裡的腫瘤含量是 10%</h3><p>每個細胞有兩份該位置的 DNA。腫瘤細胞只帶一份 ALT，因此 ALT 占 1/20。</p><p>雖然 VAF 是 5%，這個例子中所有腫瘤細胞都帶有變異。</p><p>真實結果還受 CN、亞克隆與比對偏差影響，不能直接反推純度。</p>'),
        '低 VAF 可以是低腫瘤含量，也可以有其他解釋；不可只看一個比例判斷克隆性。',
        'Allele 是同一位置的不同序列形式。簡化模型中，二倍體腫瘤細胞有一份 REF 與一份 ALT，正常細胞則兩份都為 REF。十個細胞共有二十份 allele，其中一份為 ALT；在等量採樣假設下預期 VAF 為 5%。\n\n這個例子只用來分開「細胞數比例」與「allele 比例」。若腫瘤有擴增、缺失或多個亞克隆，分母會改變；病理估計的 tumor cellularity 也不一定等於模型中的 DNA purity。單一 VAF 不足以同時推定純度、拷貝數和 cancer cell fraction。', 'L02：第五章', '', 'fig')

    add('04 · 回查原始證據', '兩個 5% VAF：看讀段排列，才能找到隱藏的偏差',
        figure('read-evidence.svg','人工排列比較：A方向分散，B同向且ALT在末端；未畫REF讀段',
            '<h3>IGV 可以協助人工回查</h3><p>A 的 ALT 位置與方向較分散；B 需排查末端品質、接頭、比對與方向性問題。</p><p>還要核對定位品質 MAPQ、附近 indel／重複序列、獨立分子及 normal 證據。</p><p>某些文庫設計本來有方向限制，不能套用一刀切的排除規則。</p>'),
        '這是警示模式，不是真偽裁決；IGV 截圖本身也不能取代經驗證的判讀規則。',
        'IGV 是沿基因體座標檢視 reads、參考與註解的工具。本圖不是實際 IGV 輸出，而是畫出二十條支持 ALT 的人工讀段；其餘三百八十條 REF 讀段省略。紅色標記是候選位置，箭頭表示比對方向。\n\n偏差可能來自接頭殘留、定序錯誤、DNA 損傷、附近 indel、重複序列或設計限制。觀察到偏差應觸發查核，不能自行把所有同向支持刪掉。A 雖較合理，仍需完整 QC 與規則；B 若不能排除疑慮，應依流程處理不確定性及補測需求，而非強行放行。', 'L02：低 VAF、方向與末端偏差', 'mutect', 'fig')

    add('04 · 不同變異需要不同證據', 'SNV、CNV、SV：不能用同一個分數保證全部',
        table(['事件','核心證據','常見影響因素'],[
            ['SNV／短 indel','鹼基替換、短插入缺失；局部序列與讀段支持','品質、比對、背景錯誤與低 VAF'],
            ['CNV 拷貝數變化','區域深度＋allele balance → 校正與分段','捕捉／GC 偏差、純度、倍體與參考基準'],
            ['SV 結構變異','Split reads、配對距離／方向、局部組裝等','重複區、斷點是否被捕捉、讀長與深度'],
        ])+p('例如區域讀段變多，可能是 DNA 拷貝增加，也可能只是捕捉效率較高；先校正，再建模。'),
        '不同事件類型須分別評估檢測能力；「SNV 驗證通過」不代表 CNV／融合也通過。',
        'SNV 是單一鹼基差異，indel 是插入或缺失。CNV 看的是一段 DNA 的相對或絕對拷貝量，通常先把不同區段的技術偏差與參考基準處理好，再將連續相似訊號分段，最後在純度與倍體假設下推估拷貝數。\n\nSV 包含較大的缺失、插入、倒位或重排等。跨斷點 reads 與異常配對能提供結構線索；但未覆蓋的斷點可能無法偵測。RNA 中看到融合接合可支持有表達的融合轉錄本，仍需專用流程與驗證，不能只靠 DNA SNV caller 或一般 gene counts 表處理。', 'L01：CNV/SV；L02：分析支線', 'jennings', 'compact')

    add('05 · RNA 增加了哪種資訊', 'DNA 問序列；RNA 還能問「表現多少、如何接合」',
        figure('splicing.svg','人工E1-E2-E3與E1-E3的可變剪接示意',
            '<h3>Exon 與 junction 是什麼？</h3><p>Exon 是成熟 RNA 保留的區段；junction 是區段接合的位置。</p><p>Alternative splicing 讓同一基因產生不同 RNA 形式，總量不變也可能換了形式。</p><p>跨 E1–E3 的讀段支持局部跳躍；不直接證明 DNA 刪掉 E2。</p>'),
        '只有 gene count matrix，通常無法還原已丟失的接合位置；剪接要保留相應證據。',
        'RNA 剪接會移除內含子並連接外顯子。外顯子不全是蛋白質編碼區，也可能包含 UTR。可變剪接是採用不同接合位置或區段組合，不必然產生功能不同的蛋白質。\n\n完全落在共用 exon 的 read 可以支持基因有表現，卻無法區分兩個 RNA 形式。跨 E1–E3 的 read 對局部結構更具辨識力，因此剪接分析需要 splice-aware alignment、junction 或轉錄本層級資訊。融合 RNA 也需跨接合證據、適當濾除及獨立驗證，不能把任何少量新 junction 都當作臨床事件。', 'L03：11.1、11.4', 'igv', 'fig')

    add('05 · RNA 的分析限制', 'RNA-seq 的 QC、分母與研究設計都會改變答案',
        cards(('先確認到底量到什麼 RNA', 'Poly(A) 富集與 rRNA 去除取得的 RNA 母體不同；股向設定錯誤會影響歸屬。高比對率也可能主要來自 rRNA。'),
               ('再區分探索與臨床檢測', 'Counts 是計數，TPM 是相對豐度；DESeq2 等方法不能把 TPM 直接當 raw counts。批次與細胞組成也會造成表現差異。'))
        +p('差異表現是比較群組；若要用於單一病人分類，必須另定模型、閾值、適用對象與獨立驗證。'),
        '「顯著基因」不是已驗證 biomarker；p 值與漂亮熱圖不能直接變成 LDT 的性能聲稱。',
        'RNA 的文庫設計決定哪些分子更容易被觀察。Reverse-stranded 文庫的 R1 常與原始 RNA 方向相反，工具設定應依實際方法核對，不能只憑檔名猜。比對後還需檢查可歸屬基因比例、rRNA、gene-body coverage 與 junction 支持。\n\n正規化是處理深度與組成差異，不是自動消除所有批次效應。差異表現通常須有獨立生物重複，並考慮多重檢定。若建立臨床表現分數，必須鎖定輸入、前處理、模型與閾值，使用適當且獨立的樣本驗證；不能在同批挑出基因又用同批宣稱預測能力。', 'L03：第三、五、七、九、十章', 'deseq')

    igv_data = b64encode((ROOT / 'figures/lesson-03-igv/SL_Sashimi1.png').read_bytes()).decode()
    add('05 · 真實介面圖例', 'Sashimi plot：弧線是局部接合證據，不是完整 RNA',
        f'<div class="ldt-figure"><img class="igv-image" src="data:image/png;base64,{igv_data}" alt="IGV 官方SLC25A3範例，heart、kidney、liver三軌"><article><h3>圖中三個元素</h3><p>山峰：逐位置 coverage。<br>弧線：splice junction。<br>數字：跨接合點的 reads 數。</p><p>紅／藍／綠是三個組織軌道，不是在這裡表示正反股。</p><p>三軌縱軸上限不同；不能直接比較峰高。弧線數字也不是 PSI。</p></article></div>',
        '先核對尺度、分子支持與每個樣本，再談差異；肉眼圖形不能替代正式驗證。',
        '這張圖片引用 IGV 官方文件，為 SLC25A3 的 heart、kidney、liver 軌道；不是本課或院內分析結果。圖中三軌上限不同，因此相同高度不等於相同深度。弧線數字是局部 junction 的支持 reads，不是完整分子數，也不是自動校正後的剪接比例。\n\nPSI（percent spliced in）描述可區分形式中選擇包含事件的比例，估計時要考慮事件定義、計數及有效長度。單一局部接合無法證明遠端事件位於同一條 RNA。原圖、來源與引用界線沿用第三堂來源紀錄。', 'L03：第 51 頁、11.8', 'igv', 'fig')

    add('06 · 怎麼知道流程可靠', '驗證不是「跑得出結果」，而是量化對與錯',
        table(['人工測試：200 個預先定義的 SNV 測試位置','參考有變異','參考無變異'],[
            ['流程判定有變異','95：真陽性 TP','2：假陽性 FP'],
            ['流程判定無變異','5：假陰性 FN','98：真陰性 TN'],
        ])+p('分析靈敏度＝95/100＝95%；精確率 precision＝95/97≈97.9%。<br>本例特異度＝98/100＝98%，只適用於這組預先定義的測試位置。'),
        '這些是人工算例，不是本實驗室性能；分析靈敏度也不是疾病的臨床診斷敏感度。',
        '靈敏度關心已知陽性中有多少被找到；precision 關心報出陽性中有多少與參考一致。特異度需要明確定義陰性機會，不能任意拿整個基因體的龐大參考鹼基當分母，掩蓋實際錯誤。\n\n真實參考標準也可能有不確定性；若沒有足夠的真值依據，應使用適當的符合率及差異調查，而非直接稱所有不一致都是流程錯誤。性能需分檢體、事件類型、VAF 與困難序列環境報告，並考慮樣本量與信賴區間。重複測量的穩定性也要另外評估。', '新增：驗證指標；承接 L01–03 QC', 'roy jennings', 'compact')

    add('06 · 低頻檢測', 'LoD 不是軟體裡填了 1%，就能穩定測到 1%',
        figure('lod.svg','人工稀釋資料，各濃度20次；檢出率不是實驗室實際性能',
            '<h3>LoD＝偵測極限</h3><p>在指定檢體、輸入、事件及流程下，達到預先定義檢出機率的最低可檢出量。</p><p>圖中 2% 檢出 19/20 次，觀察值為 95%；有限重複仍有統計不確定性。</p><p>不能單靠此點，就宣告所有基因、indel、CNV 都有 2% LoD。</p>'),
        '需要適當濃度、重複、背景與變異類型的驗證；單次看到低頻訊號不等於建立 LoD。',
        'LoD 是 limit of detection。它與軟體最低 AF 參數、報告閾值或定量能力不是同一概念。某個訊號低於一般報告範圍仍可能偶然被看到，但不代表同等條件下可以穩定檢出。\n\n人工例子每濃度只做二十次；19/20 是樣本觀察比例，不會消除信賴區間。驗證計畫應事前訂定目標性能、樣本數與接受規則，涵蓋真實檢體背景及影響因素；SNV 的稀釋結果不能直接外推到其他事件。圖示用於理解驗證問題，不提供通用臨床數字。', '新增：偵測極限；L02：抽樣與有效深度', 'jennings', 'fig')

    add('06 · 驗證範圍', '真實檢體與 in silico 測試，負責檢查不同環節',
        flow('端到端<br>檢體 → 報告','資料層測試<br>FASTQ／BAM → 結果','共同回查<br>差異、失敗與限制')
        +cards(('端到端驗證看整體檢測', '涵蓋抽取、建庫、儀器、分析與報告；安排代表性檢體、變異、濃度、批次及操作條件。'),
               ('In silico 補充演算法的挑戰', '已知真值資料或人工植入變異可測特定程式問題，但無法完整模擬抽取失敗、FFPE 損傷與所有文庫偏差。')),
        'GIAB 等參考資料有指定 benchmark 區域與適用類型；不能把區域外都當成確定陰性。',
        'In silico 指在電腦資料層進行的測試。它可以增加難取得事件的測試覆蓋，也適合版本回歸，但只能驗證實際進入測試的部分。從 BAM 開始的測試，不會驗證 FASTQ 比對之前的程序。\n\nNIST 的 Genome in a Bottle 提供參考樣本、變異及 benchmark 區域，應連同版本、參考與基因體情境使用。一般 germline benchmark 也不會自動驗證低 VAF 腫瘤、RNA 或所有結構變異。應結合合適的實體材料、陰性及陽性對照、重複性／再現性測試與不一致調查。', '新增：LDT 分析驗證設計', 'giab roy')

    add('06 · 流程上線以後', '更新軟體、參數或資料庫，都可能改變答案',
        figure('versions.svg','概念回歸測試：固定資料平行比較現行及候選版本，審查差異後核准',
            '<h3>把變更當成可追溯事件</h3><p>固定測試集，對照新舊版本的候選、數值、QC 與報告內容。</p><p>依變更風險決定所需的測試及再驗證；記錄理由與核准。</p><p>保留舊版本與回復方案，不在正式個案上直接試最新版。</p>'),
        'Container 固定部分軟體環境，但不能代替資料版本、參數紀錄或效能驗證。',
        '回歸測試是用已知測試資料確認修改後沒有破壞原有行為；除了期待改善的案例，也要涵蓋陰性、困難區及既有邊界案例。資料庫或轉錄本改版可能改變命名及註解，即使 variant calling 本身未變。\n\nNextflow 等流程管理器可以協調執行及紀錄，container 可以封裝環境，但兩者都不保證分析正確。應保存程式版本、參數、reference、目標區、註解、輸入校驗碼與執行紀錄。測試通過後才依機構程序核准切換；涉及施行計畫內容的變更另依適用行政要求辦理。', 'L01–03：可重現資料包；新增變更管理', 'roy apply', 'fig')

    add('07 · 報告與限制', '「未檢出」與「無法判定」，必須分開說',
        table(['情境','可以表達','不應過度推論'],[
            ['目標及品質均符合規格','在已驗證範圍與本檢體條件下未檢出符合規則的事件','不能說此基因完全正常或排除所有疾病'],
            ['關鍵區域覆蓋不足','該區域無法可靠評估，依程序說明限制／補測','不能因 VCF 沒有記錄就稱陰性'],
            ['候選證據矛盾','依規則複核、補充檢測或標示無法確定','不能只因資料庫是 hotspot 就放行'],
        ]),
        '可追溯報告應連回方法、範圍、限制與審核；「沒找到」與「沒能力找」不是同一件事。',
        'No-call 指某位置或項目沒有足夠條件作出可靠判定，不等同陰性。某些檢測可依規則只限制局部可報告範圍，另一些情境可能需要整份重測；這必須由事前驗證與 SOP 定義，而非看到結果後臨時決定。\n\n報告應清楚說明檢體、方法、參考與轉錄本、涵蓋範圍、相關性能限制及必要 QC 限制。技術可信度、致病性與可治療性是不同評估層次。若需要其他方法確認，應選擇對該事件與濃度有足夠能力的方法，不預設任一傳統方法都能確認低頻結果。', 'L01：陰性限制；L02：證據審核；L03：推論界線', 'jennings', 'compact')

    add('07 · 品質紀錄與資料安全', '資料交出去，責任與證據不能一起消失',
        cards(('最低可追溯資料包', '樣本對照表、原始檔與校驗碼、QC、程式／參數／資料庫版本、篩選原因、複核及報告紀錄。保存與刪除依核准制度。'),
               ('委外、雲端與 AI 都要受控', '確認存取權限、傳輸／儲存保護、紀錄、備份復原及服務分工。移除姓名不代表基因資料可以任意上傳。'))
        +p('AI 可協助草擬程式或檢查清單；輸出仍須實際驗證，不能自行修改 QC、排除樣本或核發報告。'),
        '委外與商用軟體可以分工，不會自動取代檢測單位的品質與審核責任。',
        '資料追溯是能回答誰、何時、用什麼資料與版本、作出什麼改動，以及由誰審核。備份不只要存在，也要確認能復原。權限應限於工作必要範圍；可識別基因資料需要依機構及適用規範管理。\n\n衛福部另有 LDTs 相關儀器及資通系統使用切結書資訊，顯示工具與資料安全也是制度中的重要面向。本頁不逐條解釋設備或服務資格；實際使用前需由負責單位核對。AI 產生的文字或程式不能當作已執行證據，資料外傳、變更及結果核發仍需人工審核。', 'L01–03：紀錄與輸出；新增資安／責任界線', 'security roy')

    add('07 · 回到最初案例', '看到 5% VAF，先走完五個問題再下結論',
        table(['問題','本案例應回查的證據'],[
            ['1. 在聲稱範圍內嗎？','檢體、區域、事件類型、濃度是否落在驗證範圍'],
            ['2. 資料身分正確嗎？','檢體與檔案 ID、tumor–normal、參考與目標版本'],
            ['3. 證據夠且獨立嗎？','有效深度、分子家族、ALT 品質與局部比對'],
            ['4. 有何矛盾與偏差？','方向／末端偏差、FFPE、污染、normal 支持'],
            ['5. 下一步如何被核准？','按 SOP 複核、補測、限制回報或無法判定並留紀錄'],
        ]),
        'A 不能只因圖較漂亮就放行；B 不能只因同向就刪除。兩者都回到驗證過的規則。',
        '這五題可以當作學員自我檢核。先確認事件是否在檢測聲稱與當次可判讀範圍內，再確認資料正確與獨立支持，而不是先查一個基因資料庫就決定臨床意義。\n\n如果 B 的偏差是已知文庫設計造成，可能需要依該設計專屬的證據與規則評估；若是無法解釋的品質問題，就需要暫停或限制判讀。無論最後接受、排除或無法判定，都應保留資料、依據與核准紀錄，讓下一位人員能重建判斷過程。', '整合 L01–03；人工教學案例', '', 'compact')

    add('主課程總結 · 討論', '一份可信的 LDT 結果，要能回答這六件事',
        cards(('量測與證據', '① 測的是什麼、哪些沒有測？<br>② 檢體與各目標的品質是否足夠？<br>③ 結論由哪些獨立訊號支持？'),
               ('性能與責任', '④ 這種檢體／事件的能力是否驗證？<br>⑤ 能否重建版本、參數與人工改動？<br>⑥ 限制、異常與核發責任是否清楚？'))
        +p('討論：若平均深度、FastQC 與軟體 FILTER 都通過，你還會要求看哪一份證據，才願意接受「未檢出」？'),
        '生物資訊不是報告前的黑盒子，而是檢測品質的一部分。',
        '可用前頁案例回答討論題：目標區域的有效覆蓋、獨立分子、文庫與檢體背景、可報告範圍及驗證限制，都是總合格率無法取代的資訊。沒有單一指標能保證所有事件類型。\n\n這堂課的目的不是讓學員記住所有軟體名稱，而是能與實驗室、生物資訊及臨床團隊對話。後四頁是問題延伸與參考資料，不需要逐頁講完；完整指令安裝、統計推導及軟體操作仍可回到原系列前三堂教材閱讀。', '整合總結')

    add('備查 A · Array', 'BAF 與 LRR：比例與總訊號要一起看',
        table(['觀察量','白話意思','判讀限制'],[
            ['BAF：B allele frequency','校正後 B 等位基因相對訊號；典型二倍體群聚接近 0、0.5、1','A／B 是平台指定的 allele 標籤，不固定代表 A/T/G/C'],
            ['LRR：Log R Ratio','總訊號相對參考預期值的 log₂ 比值；0 代表接近該基準','上升／下降可提示拷貝增減，也受噪音與校正影響'],
            ['長區段缺乏雜合','可能是連續純合或其他造成 allele 不平衡的情境','ROH 不等於單倍體；要合併總訊號與區域證據'],
        ]),
        'Array 是訊號模型；保留強度資訊才能回查，只有 AA／AB／BB 無法還原所有證據。',
        'BAF 與 LRR 的定義及校正依平台而異。BAF 約 0.5 表示兩種 allele 的相對訊號接近，不會決定總訊號必須多強；兩杯水各一半，可以是總量 100 mL，也可以是 200 mL。LRR 則比較總訊號與參考預期。\n\n因此長區域沒有 AB 時，仍要區分總量是否減少、拷貝中性純合及其他混合情境。ROH 是連續純合區段，不代表該區只剩一份染色體。實際 LDT 聲稱需依該平台、探針密度與分析方式建立性能，不能把概念圖當確診依據。', 'L01：BAF／LRR、ROH', '', 'compact')

    add('備查 B · RNA 研究設計', '疾病與批次完全重疊，軟體無法把兩者分開',
        table(['設計','批次 1','批次 2','能否分開估計疾病與批次？'],[
            ['完全混雜','全是對照','全是病例','不能；觀察到的差異有兩種重疊解釋'],
            ['較合理配置','含病例與對照','也含病例與對照','有機會；仍需足夠重複及合適模型'],
        ])+cards(('Covariate：模型中的變數', '例如年齡、批次、治療；是否放入模型需依研究設計與問題決定。'),
                 ('Confounding：效應難以區分', '例如病例全部使用另一種建庫方式；單靠事後校正不能創造缺少的對照。')),
        '多讀同一個病人不會變成更多病人；模型與臨床分類器都需要適當的獨立驗證。',
        'Covariate 通常指納入模型解釋變異的變數；confounding 描述欲估效應與其他因素纏在一起的問題。兩者不互斥，也不是所有共變數都是混雜因子。\n\n若疾病組與批次完全一致，設計矩陣無法分開這兩個效應。即使畫出分得很漂亮的 PCA 或熱圖，也不能知道看見的是疾病還是批次。正規化處理計數尺度，batch adjustment 處理可估計的技術差異，兩者不能修復缺失的研究設計。', 'L03：2.2–2.5、8–10', 'deseq', 'compact')

    add('備查 C · 複合 biomarker', 'TMB、MSI、HRD：名稱相同，不代表方法可互換',
        table(['指標','主要在量什麼','必須查核的限制'],[
            ['TMB 腫瘤突變負荷','符合規則的體細胞變異數／可評估區域大小，常用 mut/Mb','Panel 範圍、germline 排除、事件規則與門檻'],
            ['MSI 微衛星不穩定','重複序列長度分布異常的證據','標記集合、演算法、對照需求與腫瘤含量'],
            ['HRD 同源重組修復缺陷','可由相關基因、基因體疤痕或功能測試評估不同層面','BRCA、疤痕分數、功能缺陷不是同義；各測試需分別驗證'],
        ]),
        '不能將單一基因、單一分數或其他廠牌門檻，直接搬成這套 LDT 的聲稱。',
        'TMB 的分母是實際可評估的區域，不是隨意使用 panel 標示大小；不同事件納入規則也會改變值。MSI 是重複長度不穩定的分析結果，需以適當標記與模型評估，不等同一張一般 SNV 清單。\n\nHRD 是修復功能相關概念；某些測試量測歷史性基因體疤痕，某些看基因事件，某些評估功能，不能互相視為完全等價。實際臨床意義仍需結合特定檢測、癌別與適應症。本頁僅比較訊號與分析邊界，不提供用藥閾值。', 'L02：TMB／MSI／HRD 三頁及來源', '', 'compact')

    links = ''.join(f'<li><a href="{SOURCES[k][1]}" target="_blank" rel="noopener noreferrer">{SOURCES[k][0]}</a></li>' for k in ['jct','apply','lab','roy','jennings','giab'])
    add('備查 D · 延伸閱讀', '從簡報回到原始規範、方法與完整教材',
        '<div class="reading-columns"><div><h3>官方資訊與技術建議</h3><ul>'+links+'</ul></div><div><h3>本專案的完整解釋</h3><p><a href="ldt-20261024-explanations.html">本堂逐頁詳解</a><br><a href="lesson-01-genomics.html">第一堂：Array／WES／WGS</a><br><a href="lesson-02-somatic.html">第二堂：癌症體細胞分析</a><br><a href="lesson-03-bulk-rnaseq.html">第三堂：RNA-seq 與剪接</a></p><p><a href="../../sources/ldt-20261024-sources.md">來源、查核日期與教學範圍</a></p></div></div>',
        '查核日 2026-10-15；正式授課及申請前，請再確認主管機關公告與機構適用版本。',
        '臺灣行政資訊優先以主管機關公告及醫策會工作小組為準；AMP/CAP 與 NIST 資料用於理解分析驗證與方法，不作為臺灣個案法規意見。訓練時數是否採認，須依主辦單位及適用程序確認，本檔案本身不是認證課程證明。\n\n本課只使用既有教學內容、原創人工示意與一張已有出處的官方 IGV 範例，未執行病人分析、caller、正式 LoD 或性能驗證。可在逐頁詳解中查到概念背景、計算前提與限制。', '官方來源與原三堂完整教材', '', 'resources')


CSS = BASE['CSS'] + r'''
.cover footer a{color:#b4dcd6}
.slide{padding-top:32px}.eyebrow{margin-bottom:14px}h2{font-size:37px;margin-bottom:20px}.content{height:auto}.cards{margin:12px 0;gap:22px}.cards article{padding:20px}.cards h3{font-size:27px;margin-bottom:13px}.cards p{font-size:25px;line-height:1.55}p{font-size:25px;line-height:1.55}.takeaway{font-size:24px;margin-top:22px;padding:13px 18px}.compact td{padding:12px 14px}.compact table{font-size:23px}.compact p{font-size:24px}.flow{margin:18px 0 23px}.flow div{font-size:26px;line-height:1.5;padding:20px 14px}.ldt-figure{display:grid;grid-template-columns:700px 1fr;gap:25px;align-items:start}.ldt-figure img{width:700px;height:380px;object-fit:contain;background:#fffdf8}.ldt-figure .igv-image{height:420px}.ldt-figure h3{font-size:27px;margin:6px 0 14px}.ldt-figure p{font-size:23px;line-height:1.5;margin:13px 0}.fig .takeaway{font-size:24px;margin-top:18px}.cover .subtitle{font-size:28px}.cover .hero{font-size:28px;margin-top:26px}.cover h2{font-size:52px;margin:30px 0}.cover .speaker{font-size:25px;bottom:90px}.reading-columns{display:grid;grid-template-columns:1.1fr 1fr;gap:34px}.reading-columns h3{font-size:27px}.reading-columns ul{font-size:23px;line-height:1.8;padding-left:25px}.reading-columns p{font-size:24px;line-height:1.9}footer{font-size:14px}.appendix .eyebrow{color:#a94b27}
'''


def main():
    make_figures()
    make_slides()
    assert len(SLIDES) == 34
    pages, readings = [], []
    for i, s in enumerate(SLIDES, 1):
        source = refs(s['sources']) or '整合前三堂教材；完整依據與前提見逐頁詳解'
        md = s['notes'] + f'\n\n**教材對應**：{s["origin"]}。\n\n**使用界線**：圖中人工數字與門檻僅供教學，非實測臨床效能或放行標準。'
        notes = subprocess.run(['pandoc','--from=gfm','--to=html5','--wrap=none',f'--id-prefix=ldt-{i}-'],input=md,text=True,capture_output=True,check=True).stdout
        notes += f'<p class="help">{source}</p>'
        title = escape(s['title'].replace('<br>', ' '))
        kind = s['kind'] + (' appendix' if i > 30 else '')
        take = f'<p class="takeaway">{s["takeaway"]}</p>' if s['takeaway'] else ''
        pages.append(f'<section class="slide {kind}" id="slide-{i}" data-title="{title}" aria-label="第 {i} 頁：{title}"><header class="eyebrow">LDTs / {s["topic"]}</header><h2>{s["title"]}</h2><div class="content">{s["body"]}{take}</div><template>{notes}</template><footer><span class="source">{source}</span><span class="page">{i:02d} / 34</span></footer></section>')
        readings.append(f'<article id="page-{i}"><h2>{i:02d} · {title}</h2>{notes}<p><a href="ldt-20261024-bioinformatics.html#slide-{i}">回到投影片</a></p></article>')
    head = '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="奇美醫院精準醫學核心實驗室組長邱家軍">'
    controls = '''<nav aria-label="投影片導覽"><button id="prev">← 上一張</button><span id="status" aria-live="polite"></span><button id="next">下一張 →</button><button id="overview">目錄 O</button><button id="explanation">逐頁詳解 E</button><button id="fullscreen">全螢幕 F</button><button id="print">列印全部</button></nav><dialog id="menu" aria-labelledby="menu-title"><div class="menuhead"><h3 id="menu-title">LDTs 生物資訊 · 30 頁主課程＋4 頁備查</h3><button id="close">關閉</button></div><p class="help">方向鍵／空白鍵翻頁 · E 詳解 · Esc 關閉 · F 全螢幕<br>正文及圖片可離線播放；外部來源需連網。</p><div id="toc"></div></dialog><dialog id="explain" aria-labelledby="explain-title"><div class="menuhead"><a id="reading-link" href="ldt-20261024-explanations.html" target="_blank" rel="noopener">閱讀全部詳解 ↗</a><button id="explain-close">關閉 Esc</button></div><h2 id="explain-title"></h2><div id="explain-body"></div></dialog>'''
    js = BASE['JS'].replace('lesson-03-explanations.html','ldt-20261024-explanations.html')
    html = head+'<title>LDTs 生物資訊入門｜2026-10-24</title><style>'+CSS+'</style></head><body class="nojs"><noscript>JavaScript 關閉，以下顯示全部投影片。</noscript><main id="stage">'+''.join(pages)+'</main>'+controls+'<script>'+js+'</script></body></html>'
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'ldt-20261024-bioinformatics.html').write_text(html)
    reading_css = 'body{max-width:1000px;margin:40px auto;padding:0 30px;background:#fbf9f3;color:#183b40;font-family:"PingFang TC","Microsoft JhengHei",sans-serif}p,li{font-size:22px;line-height:1.9}h1{font-size:36px}h2{font-size:30px}article{padding:24px 0;border-bottom:1px solid #abc1bc}a{color:#087c83}nav a{display:block;font-size:18px;line-height:1.9}.help{font-size:17px}@media print{nav{display:none}article{break-before:page}p{font-size:12pt}}'
    nav = ''.join(f'<a href="#page-{i}">{i:02d} · {escape(s["title"].replace("<br>"," "))}</a>' for i,s in enumerate(SLIDES,1))
    (OUT/'ldt-20261024-explanations.html').write_text(head+'<title>LDTs 生物資訊｜逐頁詳解</title><style>'+reading_css+'</style></head><body><h1>LDTs 生物資訊：逐頁詳解</h1><p>2026-10-24｜奇美醫院精準醫學核心實驗室組長邱家軍<br>學員閱讀版；查核日 2026-10-15。</p><nav>'+nav+'</nav>'+''.join(readings)+'</body></html>')
    print(f'Built {len(SLIDES)} slides, reading notes and 8 original SVGs.')
    for i,s in enumerate(SLIDES,1):
        print(f'{i:02d} {s["title"].replace("<br>"," ")}')


if __name__ == '__main__':
    main()
