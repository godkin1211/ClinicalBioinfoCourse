"""Build an offline, dependency-free HTML deck from curated lesson 01 content."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
slides = []


def cards(items):
    return '<div class="cards">' + ''.join(f'<article><h3>{a}</h3><p>{b}</p></article>' for a,b in items) + '</div>'


def flow(items):
    return '<div class="flow">' + '<span class="arrow">→</span>'.join(f'<div>{a}</div>' for a in items) + '</div>'


def table(headers, rows):
    return '<table><thead><tr>'+''.join(f'<th>{x}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{x}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'


def code(text):
    return '<pre><code>'+escape(text)+'</code></pre>'


def answer(text):
    return '<details><summary>先想一想，再展開解析</summary><div class="answer">'+text+'</div></details>'


def sequencing_scope():
    """Design targets, not measured coverage; all tracks share the same coordinates."""
    exons = [2, 5, 8, 12, 15, 18, 22, 25, 28]
    parts = ['<div class="scope-diagram" role="img" aria-label="同一段基因體：Panel 選部分基因的目標區、WES 選跨基因的編碼外顯子、WGS 廣泛取樣編碼與非編碼區；不是實測覆蓋圖">',
             '<div class="scope-header"><span></span><div><span>基因甲</span><span>基因乙</span><span>基因丙</span></div></div>']
    for label, positions, note in [
        ('DNA 地圖', exons, '深色小塊：編碼外顯子；灰線：內含子／基因間區'),
        ('Panel', exons[:3], '本例只選基因甲；實際範圍依 panel 設計'),
        ('WES', exons, '跨許多基因捕捉編碼外顯子，仍可能有缺口'),
        ('WGS', list(range(1, 31)), '廣泛取樣全基因體；不保證每個位置都可可靠判讀'),
    ]:
        tiles = ''.join(f'<i style="grid-column:{p}" aria-hidden="true"></i>' for p in positions)
        parts.append(f'<div class="scope-row"><b>{label}</b><div class="scope-track">{tiles}</div><p>{note}</p></div>')
    return ''.join(parts) + '</div>'


def coverage_example(label, depths):
    mean = sum(depths) / len(depths)
    breadth = sum(d >= 20 for d in depths) / len(depths) * 100
    cells = ''.join(f'<span class="{"gap" if d < 20 else "covered"}">{d}×</span>' for d in depths)
    return (f'<article class="panel"><h3>{label}</h3><div class="depth-tiles">{cells}</div>'
            f'<p>共同目標平均深度：<strong>{mean:g}×</strong><br>共同目標達 ≥20×：<strong>{breadth:g}%</strong></p></article>')


def add(section, title, body, note='', kind=''):
    slides.append(dict(section=section,title=title,body=body,note=note,kind=kind))


def baf_chart():
    # Deliberately idealized bands, not biological observations.
    parts=['<svg viewBox="0 0 1080 300" role="img" aria-label="正常、缺失、增益與 ROH 的理想化 BAF 群帶與 LRR 比較">']
    for k,(label,bands,lrr) in enumerate([('正常',[0,.5,1],'≈ 0'),('缺失',[0,1],'下降'),('增益',[0,1/3,2/3,1],'上升'),('ROH',[0,1],'≈ 0')]):
        x=35+k*270
        parts += [f'<text x="{x+95}" y="26" text-anchor="middle" class="plot-title">{label}</text>',f'<path d="M{x} 55 V225 H{x+220}" class="axis"/>']
        for v in (0,.5,1):
            y=220-v*150
            parts.append(f'<text x="{x-8}" y="{y+5}" text-anchor="end" class="tick">{v:g}</text>')
        for j in range(24):
            v=bands[j%len(bands)]
            parts.append(f'<circle cx="{x+12+j*8.5}" cy="{220-v*150}" r="4.5" fill="#087c83"/>')
        parts.append(f'<text x="{x+100}" y="265" text-anchor="middle" class="plot-title">LRR {lrr}</text>')
    return ''.join(parts)+'</svg>'


add('第一堂 · 基因體資料分析', '從 SNP Array<br>到 WES/WGS', '<p class="subtitle">基因體資料分析入門</p><div class="hero-flow">訊號 <span>→</span> 資料 <span>→</span> 證據</div><p class="speaker">講師：OO醫院精準醫學核心實驗室組長邱XX</p>', '高雄長庚臨床生物資訊系列課程 · 依第一堂教案與學員教材編製', 'cover')
add('起點', '今天練習的是「分析判斷」', cards([('選資料','研究問題需要哪一種測量？'),('看流程','結果由哪些訊號與假設產生？'),('查證據','哪些 QC 問題應先停下來？')])+'<p class="takeaway">不以遺傳諮詢、致病性分級或報告簽發為主。</p>', '方向鍵／空白鍵翻頁 · F 全螢幕 · O 目錄 · Home／End 首末頁')
add('研究問題', '一組病例與對照，四種問題', cards([('常見 SNP','比較兩組的 allele 分布'),('罕見編碼變異','找出外顯子中的序列差異'),('樣本關係','是否有重複或親緣樣本？'),('區域變化','是否有 CNV 或長段 ROH？')])+'<p class="takeaway">涵蓋最廣的平台，不會自動回答所有問題。</p>')
add('技術選擇', '先決定要看什麼，再決定用什麼', table(['平台','測量範圍','主要限制'],[['SNP array','預先設計探針的 allele 訊號','位點與族群選取偏差'],['Panel','選定基因／區域的序列','目標範圍與版本限制'],['WES','捕捉目標外顯子','捕捉不均、非編碼區有限'],['WGS','更廣的基因體序列','重複區仍困難；需多種 caller']]),'技術選擇仍需考量樣本數、目標解析度、既有資料與運算資源。')
add('變異語言', '不同變化，需要不同證據', cards([('SNV / SNP','單一鹼基差異；SNP 常指族群多型性'),('Indel','短片段插入／缺失'),('CNV','一段 DNA 的拷貝數改變'),('SV','較大型結構改變，如倒位、易位')])+'<p class="takeaway">「有定序資料」≠「所有變異類型都已可靠分析」。</p>')
add('全貌', '兩條資料流，兩種原始證據', '<h3>SNP array</h3>'+flow(['探針強度','正規化／calling','Genotype + BAF/LRR','QC／下游分析'])+'<h3>Panel / WES / WGS</h3>'+flow(['FASTQ','Alignment','BAM / CRAM','Calling → VCF']), 'Annotation 是下游附加資訊，不是原始測量；reference 是座標基準，不是「健康基因體」。')
add('Array · 平台示意', 'SNP array 如何把一個位點變成基因型？',
    '<p class="mechanism-intro">以 Infinium II 為例：本例 A 代號＝鹼基 A；B 代號＝鹼基 G。</p>'
    + (ROOT / 'figures/lesson-01-snp-array-mechanism.svg').read_text(encoding='utf-8')
    + '<p class="takeaway">兩種 allele 是同源染色體的兩個版本；T/C 是互補股表示，不是另外兩種 allele。</p>',
    'Infinium II：每位點一種探針、多個拷貝；Infinium I 與其他平台設計不同。示意省略部分前處理。<br>'
    '<a href="https://support-docs.illumina.com/ARR/Inf_LCG_UG_15023139/Content/ARR/LCG/Intro_fINF_mLCG.htm">Illumina：單鹼基延伸機制</a> · '
    '<a href="https://www.illumina.com/products/by-brand/infinium.html">探針設計與工作流程</a> · 模糊／低品質訊號可不判定，不強迫分群。',
    'mechanism-slide')
add('Array · 訊號', '基因型是從訊號「判定」出來的',
    '<div class="split allele-example"><div class="panel"><h3>A／B 是兩種等位基因的代號</h3>'
    '<p>等位基因（allele）：同一位點的不同序列版本。</p>'
    '<p><strong>代號 A 不一定是鹼基 A；<br>B 也不是一種 DNA 鹼基。</strong></p>'
    '<p>例：某 A／G 位點，假設<br>A 代號＝鹼基 A，B 代號＝鹼基 G。</p></div><div>'
    '<h3>正常二倍體：每人有兩份</h3>'
    + table(['基因型代號','本例實際鹼基','組合'],[['AA','A / A','純合'],['AB','A / G','雜合'],['BB','G / G','純合']])
    + '</div></div>'
    + flow(['兩種 allele 的探針訊號','正規化＋群聚模型','判定 AA／AB／BB']),
    '示例不是通用鹼基對應；需查 manifest（探針／allele 對照）與股向，A/B 不等於 REF/ALT。<br>群聚需相容的 cluster reference；判不清楚可留 missing call。<a href="https://knowledge.illumina.com/microarray/general/microarray-general-reference_material-list/000001489">Illumina：A/B 與股向</a>',
    'allele-slide')
add('Array · 資料保留', 'Hard call 留下答案，卻壓縮了證據',
    '<p class="hardcall-definition"><strong>Hard call＝單一基因型標籤</strong>（AA／AB／BB）；無法可靠判定可留 no-call。</p>'
    + flow(['A、B 的連續強度','正規化＋群聚判定','輸出標籤，例如 AB'])
    + table(['同一位點：兩個樣本的教學假設','只看 hard call','原本不同的證據'],[
        ['樣本 1：靠近 AB 群中心','<strong>AB</strong>','較符合群聚模型'],
        ['樣本 2：靠近 AB 群邊緣，仍過門檻','<strong>AB</strong>','判定品質較低，較需回查'],
    ])
    + '<p class="takeaway">兩個 AB 不代表同樣可靠；標籤不能還原強度、品質分數或 BAF／LRR。<br>可用 hard call 做分析，但不要只留下 genotype 表。</p>',
    'BAF＝相對 B allele 訊號；LRR＝總強度相對預期的指標。完整報表可同時保存 genotype 與這些欄位。<br>'
    '另留原始檔、manifest、群聚參考與版本。<a href="../../lessons/lesson-01-slide-09-explanation.md">本頁完整講解</a> · '
    '<a href="https://www.illumina.com/Documents/products/technotes/technote_infinium_genotyping_data_analysis.pdf">Illumina：群聚與品質</a>',
    'hardcall-slide')
add('Array · 指標入門', 'BAF 與 LRR：比例、總量分開看',
    '<p class="metrics-intro">兩者都是由晶片訊號衍生的連續指標，不是另一種基因型標籤。</p>'
    '<div class="split metrics-panels"><article class="panel"><h3>BAF<span>B Allele Frequency</span></h3>'
    '<div class="metric-detail"><p>單一樣本、單一位點的<br><strong>相對 B allele 訊號</strong>（經群聚校正）。</p></div>'
    '<div class="metric-scale" aria-label="正常二倍體典型 BAF：AA 約 0，AB 約 0.5，BB 約 1">'
    '<div><b>≈ 0</b><span>AA</span></div><div><b>≈ 0.5</b><span>AB</span></div><div><b>≈ 1</b><span>BB</span></div></div>'
    '<p class="metric-note"><strong>正常二倍體典型值，不是族群頻率。</strong></p></article>'
    '<article class="panel"><h3>LRR<span>Log R Ratio</span></h3>'
    '<div class="metric-detail"><p class="metric-formula">log₂(R<sub>觀察</sub> / R<sub>預期</sub>)</p>'
    '<p class="metric-r-definition">R：正規化後的總訊號。<br>預期值：由參考群聚模型估計。</p></div>'
    '<div class="metric-scale" aria-label="LRR 小於零表示總訊號低於預期，約零表示接近預期，大於零表示高於預期">'
    '<div><b>&lt; 0</b><span>低於預期</span></div><div><b>≈ 0</b><span>接近預期</span></div><div><b>&gt; 0</b><span>高於預期</span></div></div>'
    '<p class="metric-note"><strong>不是拷貝數，也不是固定的 CNV 門檻。</strong></p></article></div>'
    '<p class="takeaway">BAF 相同，LRR 仍可不同；CNV 須合看連續探針與 QC。</p>',
    'BAF 不直接等於未校正的 B/(A+B)，也不是把 hard call 硬填成 0、0.5、1；LRR 不直接等於拷貝數。<br>'
    '<a href="../../lessons/lesson-01-slide-10-baf-lrr.md">本頁講解與算例</a> · '
    '<a href="https://help.connected.illumina.com/dragen-array/product-guides/output-files">Illumina：BAF / LRR 定義</a>',
    'metrics-slide')
add('Array · 格式總覽', 'SNP array：拿到的是訊號，還是判定結果？',
    '<p class="format-intro">不同平台的檔案不相同；先辨認資料層次，再決定能做哪些分析。</p>'
    + table(['常見檔案／層次', '主要裝什麼？', '用途與注意事項'], [
        ['<strong>IDAT／CEL</strong><br>原始強度', '探針螢光強度，不是 DNA 讀序', 'IDAT：Illumina；CEL：Affymetrix／Axiom'],
        ['<strong>GTC（.gtc）</strong><br>Illumina calling 結果', '每個樣本的 genotype 與品質等資訊', '需搭配相符 manifest 解讀位點'],
        ['<strong>Final Report（TXT／CSV）</strong><br>可讀報表', '樣本、SNP、alleles；可含 BAF／LRR', '欄位依匯出設定；不是每份都有強度'],
        ['<strong>PED＋MAP／BED＋BIM＋FAM</strong><br>PLINK 分析輸入', '基因型、位點與樣本資料', '用於 QC／PCA／ROH；不保存完整強度'],
    ])
    + '<div class="format-support"><b>還要一起保存</b><span>Manifest＝探針／位點對照（如 BPM／CSV）；EGT＝Illumina 群聚參考。<br>兩者是分析資源，不是病人的測量結果；版本須與晶片相符。</span></div>',
    '這些是不同資料層次，不是可任意互換的副檔名；Axiom 不使用 Illumina 的 GTC／EGT 流程。<br>'
    '<a href="https://support-docs.illumina.com/ARR/iScan/Content/ARR/iScan/GeneratedFiles_fIS.htm">IDAT／GTC</a> · '
    '<a href="https://help.connected.illumina.com/dragen-array/product-guides/output-files">Final Report</a> · '
    '<a href="https://help.connected.illumina.com/dragen-array/dragen-array-v1.0/product-guides/input-files">Manifest／EGT</a> · '
    '<a href="https://www.thermofisher.com/sg/en/home/life-science/microarray-analysis/applications/predictive-genomics/population-genomics/software.html">Axiom CEL</a>', 'format-slide array-format-slide')
add('Array · 檔案', 'BED / BIM / FAM 是一組資料', table(['檔案','內容','先核對'],[['.bed','二進位 genotype','是否與另外兩檔同一前綴？'],['.bim','位點、位置、alleles','Reference build／strand 一致？'],['.fam','樣本、家系與表型欄位','FID / IID 對得上檢體嗎？']])+'<p class="takeaway">PLINK .bed 不是基因體區間的文字 BED。</p>', 'PED／MAP 是可讀的 genotype／位點文字格式；本例由 PED/MAP 轉成 PLINK binary。')
add('Array · QC', 'QC 不只是一個合格率',
    '<p class="qc-intro"><strong>Call rate 高＝多數位點有答案；不代表答案都正確，也不保證樣本沒拿錯。</strong></p>'
    + table(['檢查層次／問題', '看什麼指標？', '異常時，接著查什麼？'], [
        ['<strong>樣本</strong>｜這管資料可靠嗎？', '缺失率、雜合度、樣本標籤', '查 DNA 品質、混樣與檢體紀錄'],
        ['<strong>位點</strong>｜這個 SNP 穩定嗎？', '缺失率、allele 頻率、HWE', '查訊號群聚、族群與批次差異'],
        ['<strong>樣本間</strong>｜能直接比較嗎？', '基因型相似度、親緣、PCA', '查重複收案、祖源與實驗批次'],
        ['<strong>區域</strong>｜是雜訊還是真訊號？', '連續探針的 BAF／LRR', '查訊號品質；再評估 ROH／CNV'],
    ])
    + '<div class="qc-case"><div><span class="qc-case-label">假設案例</span><b>99.8%</b><span>Call rate</span></div>'
    '<p>兩個不同病人 ID，基因型卻幾乎相同。<br><strong>先核對重複採樣、標籤與家系，不能直接當兩名獨立病人。</strong></p></div>'
    '<p class="qc-conclusion">QC 是「發現問題 → 查明原因 → 記錄處置」，不是看到離群就刪除。</p>',
    'MAF＝較少見 allele 的頻率；HWE＝基因型比例的平衡檢查；PCA＝樣本差異的摘要圖，後頁逐一說明。<br>'
    '<a href="../../lessons/lesson-01-slide-12-qc.md">本頁完整說明與判讀案例</a> · '
    '<a href="https://www.cog-genomics.org/plink/1.9/basic_stats">PLINK 基本統計</a> · '
    '<a href="https://www.cog-genomics.org/plink/1.9/ibd">親緣與 ROH</a>', 'qc-overview-slide')
add('Array · Missingness', '一個壞樣本，與一個壞位點不同', '<div class="split"><div class="panel"><h3>沿著樣本看</h3><p class="big">2,000 / 6,000</p><p>Missingness ≈ 33.3%<br>Call rate ≈ 66.7%</p></div><div class="panel"><h3>沿著位點看</h3><p class="big">10 / 40</p><p>Missingness = 25%<br>Call rate = 75%</p></div></div><p class="takeaway">Call rate = 1 − missingness；門檻要有研究依據。</p>', '此頁是計算示例；實作中的 v1 缺失為 11/40，不是 10/40。')
add('Array · MAF 與 HWE', '頻率與分布，不是「好壞」標籤', '<div class="split"><div class="panel"><h3>MAF：較少見 allele 的比例</h3><p class="big">8 / 80 = 0.1</p><p>40 名二倍體、無缺失<br>頻率依資料集與族群而變</p></div><div class="panel"><h3>HWE：理想基因型比例</h3><p class="formula">p² : 2pq : q²</p><p>p=0.7，q=0.3<br>49% : 42% : 9%</p></div></div>', 'HWE 偏離可能來自技術錯誤、族群混合、親緣或生物因素；本課只產生報表，不自動 HWE 過濾。')
add('Array · 樣本核對', '異常是調查起點，不是診斷', cards([('雜合度偏高','查污染、混合、祖源與 calling'),('雜合度偏低','查族群、親緣、技術與區域背景'),('Reported-sex check','核對登錄資料與性染色體訊號')])+'<p class="takeaway">PLINK .het 的 F 不是雜合百分比。</p>', 'Sex check 需考慮 X 非 PAR、倍體與平台；不推論性別認同。本例只有常染色體，不執行此檢查。')
add('Array · 結構', 'PCA 是資料地圖，不是原因證明', '<div class="split"><div><div class="concept-plot" role="img" aria-label="兩群資料點的概念示意，非實測 PCA"><span class="axis-y">PC2</span><span class="axis-x">PC1</span><div class="cloud a">● ● ●<br>● ● ●</div><div class="cloud b">◆ ◆ ◆<br>◆ ◆ ◆</div></div><p class="caption">概念示意，非實測 PCA</p></div><div><h3>兩群可能表示什麼？</h3><ul><li>祖源結構</li><li>批次或品質差異</li><li>重複與親緣樣本</li></ul><p>先做 LD pruning，減少高度相關位點的重複影響。</p></div></div>', 'PCA cluster 不應自動命名為種族；若病例／對照與批次完全混雜，不能靠群聚歸因疾病。')
add('Array · 親緣', '基因型相似，還需要來源紀錄', '<div class="split"><div class="panel"><h3>IBS vs IBD</h3><p>IBS：觀察到 allele 相同</p><p>IBD：推估來自共同祖先</p></div><div class="panel"><h3>PLINK PI_HAT</h3><p class="formula">Z2 + ½ × Z1</p><p>接近 1：查重複或同卵雙生<br>不是自動刪除指令</p></div></div>', '<a href="https://www.cog-genomics.org/plink/1.9/ibd">PLINK IBD 文件</a> · 估計受族群與位點選擇影響；分析前使用適當 QC 與 pruning。')
add('實作 01 · 起跑', '在合成資料中找出異常', '<div class="statline"><b>40<small>個樣本</small></b><b>6,000<small>個 SNP</small></b><b>0<small>病人資料</small></b></div>'+code('cd ~/KCGMH_Cource_Series/demos/lesson-01-genomics\npython3 generate.py practice01\ncd practice01\nPLINK=plink1.9 bash ../run-array.sh'), 'Ubuntu / WSL Bash；practice01 必須為新資料夾。套件安裝與檔案位置見附錄。')
add('實作 01 · 分步', '先保留 QC 報表，再篩選',
    '<div class="array-command-steps">'
    '<article><h3>① 轉格式｜PED／MAP → BED／BIM／FAM</h3>'
    + code('plink1.9 --file array --make-bed --out raw')
    + '<p><code>--file</code> 讀 array；<code>--make-bed</code> 產生二進位三件組；<code>--out</code> 命名前綴。</p></article>'
    '<article><h3>② 留報表｜讀 raw，只做統計，不排除資料</h3>'
    + code('plink1.9 --bfile raw --missing --freq --hardy --het --out qc')
    + '<p><code>--bfile</code> 讀三件組；後四項依序：缺失率、allele 頻率、HWE、純合／雜合統計。</p></article>'
    '<article><h3>③ 篩樣本｜從 raw 排除缺失率 &gt; 5% 的人</h3>'
    + code('plink1.9 --bfile raw --mind 0.05 --make-bed --out sample_qc')
    + '<p><code>--mind</code> 按「每人」缺失比例篩選；另存 sample_qc 三件組，保留 raw。</p></article>'
    '<article><h3>④ 篩位點｜在剩餘樣本中，排除缺失率 &gt; 5% 的 SNP</h3>'
    + code('plink1.9 --bfile sample_qc --geno 0.05 --make-bed --out clean')
    + '<p><code>--geno</code> 按「每個位點」缺失比例篩選；另存 clean 三件組，不代表所有 QC 已合格。</p></article></div>',
    '5% 僅為操作示例；先人工查看 qc 報表再決定門檻。run-array.sh 整份執行時不會停下等確認。<br>'
    '<a href="../../lessons/lesson-01-slide-19-array-commands.md">每行參數、輸出檔與算例</a> · '
    '<a href="../../demos/lesson-01-genomics/run-array.sh">完整逐行註解腳本</a> · '
    '<a href="https://www.cog-genomics.org/plink/1.9/basic_stats">PLINK 統計</a> · '
    '<a href="https://www.cog-genomics.org/plink/1.9/filter">篩選文件</a>', 'array-commands-slide')
add('實作 01 · 先判讀', '從哪個檔案找證據？', table(['問題','報表','要看的欄位'],[['哪個樣本缺失最多？','qc.imiss','IID / F_MISS'],['哪個位點缺失明顯？','qc.lmiss','SNP / F_MISS'],['哪對樣本需查重複？','related.genome','IID1 / IID2 / PI_HAT'],['哪個樣本有長段純合？','roh.hom','IID / CHR / POS1 / POS2']]), 'FID 是家族 ID，IID 是個體 ID。本例為人工編號。')
add('實作 01 · 解析', '程式跑完，還要核對預期值', '<div class="statline"><b>39<small>QC 後樣本</small></b><b>5,999<small>QC 後 SNP</small></b></div>'+table(['證據','合成資料的結果'],[['S40 missingness','2,000 / 6,000 ≈ 33.3%'],['v1 missingness','11 / 40 = 27.5%'],['S01 / S02','PI_HAT = 1；已知合成複本'],['S03','chr1 有一段人工長純合區']]), '依本專案 2026-09-13 已實測紀錄；不是臨床資料或真實族群模擬。')
add('交流／練習', 'PCA 剛好把病例與對照分開', '<p class="question">但病例全在 A 批次，<br>對照全在 B 批次。</p><p>你會先報告疾病差異，還是先查研究設計？</p>'+answer('疾病與批次完全混雜，無法直接區分兩者；加入批次共變數也未必能解決不可辨識性。'), '可在此停下來提問，或回到練習報表；投影片不預設各段授課時長。')
add('定序 · 範圍', 'Panel、WES、WGS：先看「讀哪裡」',
    '<p class="seq-intro">Panel＝選定區域定序；WES＝全外顯子定序；WGS＝全基因體定序。</p>'
    + sequencing_scope()
    + '<p class="takeaway">Array 問預設位點；定序能在有效覆蓋的區域尋找未預先指定的變異。</p>',
    '設計範圍示意，非實測覆蓋、非真實長度比例；本段以常見短讀長 DNA 定序為例。<br>'
    '<a href="https://www.illumina.com/techniques/sequencing/dna-sequencing/whole-genome-sequencing/whole-genome-vs-exome.html">WES / WGS 範圍</a> · '
    '<a href="../../lessons/lesson-01-sequencing-choice.md">六頁完整說明</a>', 'seq-slide scope-slide')
add('定序 · 建庫', 'WES 多一道「挑片段」，WGS 廣泛取樣',
    '<p class="seq-intro">Library（文庫）＝接上接頭、可送入定序儀的 DNA 片段集合。</p>'
    + flow(['基因體 DNA', '製備文庫', '依策略富集／不富集', '定序 → reads'])
    + '<div class="split"><article class="panel"><h3>Panel／WES</h3><p>WES 常用探針捕捉目標片段。<br>Panel 可用捕捉或 PCR 擴增。<br><strong>富集偏差會影響各區域深度。</strong></p></article>'
    '<article class="panel"><h3>一般 WGS</h3><p>不先挑選特定基因或外顯子。<br>可依建庫方式有／無 PCR。<br><strong>仍會受 GC、文庫與比對影響。</strong></p></article></div>'
    '<p class="seq-bottom">Read＝一段讀出的序列；paired-end＝同一片段兩端各讀一次，不是把整段都讀完。</p>',
    'WES 是 DNA 定序，不是 RNA-seq；捕捉探針選區域，不要求變異已知。WGS 不等於必然 PCR-free。<br>'
    '<a href="https://www.illumina.com/techniques/sequencing/dna-sequencing/targeted-resequencing/target-enrichment.html">Target enrichment</a> · '
    '<a href="https://www.illumina.com/products/by-brand/ampliseq.html">Amplicon panel</a>', 'seq-slide')
add('定序 · 能力邊界', '範圍更廣，不等於所有變異都找得到',
    table(['想找的變化', 'Panel／WES', '短讀長 WGS'], [
        ['編碼區 SNV／短 indel', '有效覆蓋的目標內可分析', '可分析，仍須逐區確認品質'],
        ['深部內含子／調控區變異', '通常不涵蓋；特選目標除外', '有更多序列證據；解釋仍困難'],
        ['CNV／結構變異（SV）', '可分析部分事件；受目標限制', '證據較廣；需專門 caller'],
        ['重複擴增／高度相似區域', '一般流程可能漏掉', '仍可能漏；需專用方法／其他技術'],
    ])
    + '<p class="takeaway">「已做 WGS」不等於「已做完 SNV、indel、CNV 與 SV 分析」。</p>',
    '能力依建庫、深度、read 長度、區域與驗證而異；Panel 有專用設計，不能一概而論。<br>'
    '<a href="https://gatk.broadinstitute.org/hc/en-us/articles/360056969372-PostprocessGermlineCNVCalls">CNV 專門流程</a> · '
    '<a href="https://www.genome.gov/about-genomics/educational-resources/infographics/Completing-the-human-genome-sequence">重複序列挑戰</a>', 'seq-slide seq-table-slide')
add('定序 · 覆蓋比較', 'WES 100× 與 WGS 35×，不能只比數字',
    '<p class="seq-intro">假設比較同一組目標的 10 個等長區段；每格內深度一致，數字為教學假設。</p>'
    + '<div class="split">' + coverage_example('樣本甲 · WES', [110] * 8 + [120, 0])
    + coverage_example('樣本乙 · WGS', [35] * 10) + '</div>'
    '<p class="takeaway">甲的平均較高，卻有一區沒讀到；選擇時要看「重要區域是否可靠覆蓋」。</p>'
    '<p class="seq-bottom">先統一目標範圍與品質過濾，再比較達標比例、低覆蓋清單及比對品質。</p>',
    '20× 僅是算例門檻；不是臨床標準或足夠判定的保證，也不表示 WGS 一定勝過 WES。<br>'
    '<a href="https://broadinstitute.github.io/picard/picard-metric-definitions.html">Picard：target coverage 指標</a>', 'seq-slide')
add('定序 · 分析設計', '資料流程相似，分析範圍與 QC 不同',
    flow(['FASTQ', '比對 → BAM／CRAM', '依變異類型 calling', 'VCF＋QC 報表'])
    + table(['分析前要準備', 'Panel／WES', 'WGS'], [
        ['分析座標與目標', 'Reference＋試劑版本＋target BED', 'Reference＋分析／排除區域'],
        ['覆蓋與品質', 'On-target、目標深度、漏掉的 exon', '全域與重點區域深度、難比對區'],
        ['變異分析流程', 'SNV／indel；CNV 另建模型', 'SNV／indel、CNV、SV 分開規劃'],
        ['資料與運算規劃', '通常較小；仍受樣本數與深度影響', '通常較大；預留儲存與重分析資源'],
    ])
    + '<p class="seq-bottom">WES 跨試劑／批次整合：先確認共同可分析區域，不把未測到的位置補成 0/0。</p>',
    '此處 BED 是基因體區間文字檔，不是 PLINK 的 genotype .bed。實際工具與參數須依資料驗證。<br>'
    '<a href="https://gatk.broadinstitute.org/hc/en-us/articles/360035890811-Resource-bundle">GATK reference 資源</a> · '
    '<a href="https://broadinstitute.github.io/picard/picard-metric-definitions.html">Picard 品質指標</a>', 'seq-slide seq-table-slide seq-analysis-slide')
add('定序 · 如何選擇', '先列研究問題，再選平台與分析流程',
    table(['研究情境', '可優先評估', '選之前要核對'], [
        ['候選基因明確，想集中資源', '<strong>Panel</strong>', '目標清單、覆蓋缺口、可偵測變異'],
        ['候選基因未定，主要找編碼變異', '<strong>WES</strong>', '捕捉版本、關鍵 exon、樣本／家系設計'],
        ['需研究非編碼區或結構變異', '<strong>WGS</strong>', 'SV／CNV 流程、難區域、解釋與運算能力'],
    ])
    + '<div class="seq-choice-note"><h3>如果 WES 沒找到呢？</h3><p>先查：目標有沒有涵蓋？覆蓋夠不夠？caller 與註解是否適合？<br>再決定重分析、補測、WGS 或其他技術，不是直接認定「沒有變異」。</p></div>'
    '<p class="takeaway">總預算要一起算：定序範圍、每人深度、樣本數，以及分析與驗證。</p>',
    '教學選擇框架，不是個別病人的檢測建議；也須考量檢體、既有資料、授權與研究目的。<br>'
    '<a href="../../lessons/lesson-01-sequencing-choice.md">選擇情境與完整說明</a> · '
    '<a href="https://gatk.broadinstitute.org/hc/en-us/articles/360035531572-Evaluating-the-quality-of-a-germline-short-variant-callset">Callset 品質評估</a>', 'seq-slide seq-table-slide seq-choice-slide')
add('定序 · 檔案', 'FASTQ、BAM、VCF 回答不同問題', cards([('FASTQ','讀到什麼序列？<br>每個鹼基的品質如何？'),('BAM / CRAM','放在 reference 哪裡？<br>比對證據是否可靠？'),('VCF / BCF','推估出什麼變異？<br>哪些篩選已套用？')])+'<p class="takeaway">沒有列在 variant-only VCF ≠ 已確認 0/0。</p>', 'CRAM 可能需要相符 reference；不要只交付單一壓縮比對檔而遺漏必要資訊。')
add('定序 · 格式總覽', 'NGS：讀序、比對、變異，各有自己的檔案',
    table(['常見檔案／階段', '主要裝什麼？', '用途與注意事項'], [
        ['<strong>FASTQ（.fastq／.fq／.gz）</strong><br>讀序', 'Read 名稱、序列與每個鹼基品質', 'QC／比對；paired-end 常分 R1、R2'],
        ['<strong>SAM／BAM／CRAM</strong><br>比對記錄', 'Reads、比對座標、CIGAR、MAPQ 等', 'SAM 為文字；BAM／CRAM 為二進位'],
        ['<strong>VCF／BCF</strong><br>變異記錄', '座標、REF／ALT、FILTER、樣本 GT 等', 'VCF 為文字；BCF 為二進位'],
        ['<strong>gVCF（常見 .g.vcf.gz）</strong><br>Reference confidence', '變異＋非變異位置的信心資訊', '可用區塊記錄；供相容流程聯合判定'],
        ['<strong>FASTA（.fa）／區間 BED</strong><br>分析資源', 'FASTA：參考序列；BED：目標區間', '不是樣本變異結果；先核對基因組版本'],
    ])
    + '<div class="format-support"><b>別漏掉索引</b><span>.bai／.crai／.tbi／.csi 幫助快速定位，不是資料本體。<br>CRAM 常需相符 reference；.gz 只表示壓縮，不能保證可做區域查詢。</span></div>',
    '以 DNA 定序為例。gVCF 不是一般 VCF 改檔名；variant-only VCF 沒列出某位點，不代表已確認 0/0。<br>'
    '<a href="https://help.connected.illumina.com/basespace/files-used-by-basespace/fastq-files">FASTQ</a> · '
    '<a href="https://samtools.github.io/hts-specs/">SAM／BAM／CRAM／VCF／索引規格</a> · '
    '<a href="https://gatk.broadinstitute.org/hc/en-us/articles/360035531812-GVCF-Genomic-Variant-Call-Format">GATK gVCF</a>', 'format-slide ngs-format-slide')
add('定序 · 品質', '三種品質，不要混成一種', cards([('BQ','Base quality<br>單一鹼基的錯誤不確定性'),('MAPQ','Mapping quality<br>比對位置的不確定性'),('GQ','Genotype quality<br>基因型判定的不確定性')])+'<p class="formula">Q = −10 log₁₀(P<sub>error</sub>)</p><p>Q20 ≈ 1%　／　Q30 ≈ 0.1%（品質模型的尺度）</p>', 'MAPQ 定義與校準依工具而異；CIGAR 150M 不表示 150 個位置全部無 mismatch。')
add('定序 · Coverage', '平均深度會藏起沒有覆蓋的區域', '<div class="coverage" role="img" aria-label="四個等長區域深度為 120、140、0、140，平均100"><div style="--h:120px">120×</div><div style="--h:140px">140×</div><div style="--h:4px" class="zero">0×</div><div style="--h:140px">140×</div></div><div class="split"><p><strong>Depth</strong><br>單一位置有多少 reads？</p><p><strong>Breadth</strong><br>目標區有多少比例達到條件？</p></div><p class="takeaway">四個等長區域的平均是 100×，但有一區是 0×。</p>', '概念示例，非實測。WES 應使用正確 capture target 當分母；WGS 也不是所有區域都容易分析。')
add('定序 · Calling', '「有 ALT」與「有可靠變異」不同', flow(['Read / base quality','Allele 證據','錯誤模型與先驗','Genotype / variant'])+'<div class="split"><p>Indel 附近、重複序列與低複雜度區域，都可能使逐位點計數不夠。</p><p>Caller 可採不同模型或局部組裝；流程輸出不等於驗證完成。</p></div>', '<a href="https://samtools.github.io/bcftools/bcftools.html">BCFtools 文件</a> · 本課示例不是完整人類 germline production pipeline。')
add('實作 02 · 範圍', '最小示例：從已比對 SAM 開始', '<div class="statline"><b>2 kb<small>chrToy reference</small></b><b>40<small>理想化 reads</small></b></div>'+code('head -n 8 reads.fastq\nhead -n 5 aligned.sam\nbash ../run-sequence.sh\ncat calls.tsv\ncat review.tsv'), '在同一 practice01 目錄執行。SAM 位置由產生器指定，不是 aligner 實測；review.vcf 為獨立人工案例。')
add('實作 02 · 資料流', 'SAM → sorted BAM → VCF', code('samtools faidx reference.fa\nsamtools view -b aligned.sam | samtools sort -o sample.bam\nsamtools index sample.bam\nbcftools mpileup -Ou -f reference.fa \\\n  -a FORMAT/DP,FORMAT/AD sample.bam |\n  bcftools call -mv -Oz -o calls.vcf.gz\nbcftools index calls.vcf.gz'), '<code>|</code> 串接步驟；索引支援區域查詢。首次執行用新目錄；重跑索引前注意既有檔案。')
add('實作 02 · 結果', '分開看位點與樣本層級', table(['層級','欄位','不要混淆'],[['位點','CHROM / POS / REF / ALT','REF 不等於健康 allele'],['位點','QUAL / FILTER','PASS 不保證正確；. 不等於 PASS'],['樣本','GT / AD / DP / GQ','AD 順序為 REF、ALT；DP 未必等於 AD 總和']])+'<p class="takeaway">合成 caller 結果：chrToy:1000 A&gt;C · 0/1 · DP=40 · AD=20,20</p>', '本專案已測示例結果；GT 0/0、0/1、1/1 分別表示 reference 純合、雜合、ALT 純合；./. 是缺失。')
add('判讀練習', 'DP=40，是否就足夠？', table(['位置','AD','DP','GQ','FILTER'],[['1000','20,20','40','99','PASS'],['1100','2,1','3','8','LowDP'],['1200','38,2','40','15','PASS'],['1300','19,21','40','10','LowMQ']])+answer('1200 的 allele balance 與 GQ 可疑；1300 需回查 mapping。高深度不能取代其他證據。'), '人工 review.vcf；LowDP／LowMQ 為教材自訂標記。ALT/(REF+ALT)：20/40=0.5；2/40=0.05。')
add('Cohort · Joint calling', '合併檔案，不等於整合基因型證據', '<div class="split"><div class="panel"><h3>直接拼 VCF</h3><p>沒有列出的位點<br>可能是未覆蓋或未輸出</p><p class="warning">不能直接補成 0/0</p></div><div class="panel"><h3>Joint genotyping</h3><p>整合樣本證據與模型</p><p>特定流程可利用 GVCF<br>保存非變異區信心資訊</p></div></div>', '仍需每個樣本的 QC；不相容 caller 的結果不能只因放在同一張表就當成可比較。')
add('區域分析 · BAF / LRR', 'BAF 看比例；LRR 看總強度', '<div class="split"><div class="panel"><h3>BAF</h3><p class="big">0 · 0.5 · 1</p><p>正常二倍體的常見群帶<br>不是族群 allele frequency</p></div><div class="panel"><h3>LRR</h3><p class="formula">log₂(觀察 / 預期)</p><p>總訊號的相對尺度<br>需經平台校正與正規化</p></div></div>', 'BAF／LRR 是強度衍生資訊，不能只由 AA/AB/BB 完整還原。')
add('區域分析 · 對照', '相同的「沒有 AB」，可能是不同情境', baf_chart()+'<p class="takeaway">缺失與 ROH 都可能缺少中間 BAF 帶；要一起看 LRR。</p>', '理想化群帶示意，非實測。真實值受平台、噪音與混合比例影響，不作固定 CNV 門檻。')
add('區域分析 · 限制', 'ROH ≠ deletion；depth ≠ CNV caller', cards([('ROH','連續純合區<br>需連續位點與族群背景'),('Array CNV','BAF/LRR + 分段<br>需要多探針支持與 QC'),('Sequencing CNV / SV','深度、split reads、配對或組裝<br>需要適合的演算法')])+'<p class="takeaway">一段 ROH 不能單獨診斷單親二倍體或後天 LOH。</p>', 'WES 捕捉偏差需參考與校正。samtools depth 只是覆蓋統計，不是完整 CNV 分析。')
add('資料整合', '合併之前，先核對五件事', '<ol class="checks"><li><b>Sample ID</b>　檢體、臨床表格與檔案對得上？</li><li><b>Reference</b>　版本、FASTA 與 contig 相容？</li><li><b>Allele / strand</b>　正反股與 allele coding 一致？</li><li><b>表型／批次</b>　缺失與技術差異是否跟組別相關？</li><li><b>Provenance</b>　版本、參數與排除理由可重建？</li></ol>', 'VCF POS 是 1-based；區間 BED 常用 0-based half-open。A/T、C/G 回文 SNP 只看字母不易判定方向。')
add('資料整合 · 族群', '未被測量，不代表沒有變異', cards([('Ascertainment bias','探針選取與設計族群<br>會影響 array 資訊量'),('Imputation','利用 LD 與參考 haplotype<br>推估未測位點'),('可遷移性','族群、頻率、參考品質不同<br>推估可靠性也會不同')])+'<p class="takeaway">Imputation 是推估，不是直接測量。</p>')
add('自我檢核', '請用證據回答，而不只用直覺', '<ol class="checks"><li>平均 100×，每個 exon 都可靠？</li><li>PCA 分兩群，就是疾病效應？</li><li>只剩 hard calls，能完整重做 array CNV？</li><li>PASS + DP=40，就足以接受雜合結果？</li></ol>'+answer('都不能直接成立：分別需要區域覆蓋、設計／批次核對、強度資訊，以及 AD/GQ/比對等證據。'))
add('帶走的框架', '測量、推估、註解：分開看', flow(['原始訊號','演算法推估','資料註解','研究推論'])+'<div class="split"><p>每個結果都問：<br><strong>證據在哪個檔案？</strong></p><p>每個異常都問：<br><strong>還缺什麼確認？</strong></p></div><p class="takeaway">觀察 ≠ 原因；流程成功 ≠ 結果已驗證。</p>', '以下為操作附錄與延伸練習，可從目錄直接跳轉。', 'closing')
add('附錄 A · Windows', '先裝 WSL，再進入 Ubuntu', '<h3>管理員 PowerShell</h3>'+code('wsl --install -d Ubuntu\n# 依提示重新開機、建立 Ubuntu 使用者\nwsl --list --verbose')+'<p>Ubuntu 的 VERSION 應為 2。受管制電腦先洽資訊部門，不繞過權限。</p>', '<a href="https://learn.microsoft.com/en-us/windows/wsl/install">Microsoft WSL 文件</a> · 已安裝者不必重裝；相容性與院內政策需確認。')
add('附錄 A · 工具', '所有操作指令都在 Ubuntu Bash', code('sudo apt update\nsudo apt install -y python3 plink1.9 samtools bcftools\npython3 --version\nplink1.9 --version\nsamtools --version\nbcftools --version')+'<p>Python 僅用標準函式庫；不需要 R、Conda、Docker 或 GPU。</p>', '手動版可能叫 plink：改用 PLINK=plink。不要將 PLINK 2 指令直接混入此教材。')
add('附錄 A · 檔案', '保留完整專案與相對路徑', code('cp -r "/mnt/c/Users/你的帳號/Downloads/KCGMH_Cource_Series" \\\n  ~/KCGMH_Cource_Series\ncd ~/KCGMH_Cource_Series/demos/lesson-01-genomics\nls')+'<p>替換 Windows 帳號；目的資料夾應尚未存在。<br>看到 generate.py、run-array.sh、run-sequence.sh 後，再產生新練習目錄。</p>', 'HTML 可獨立離線播放；執行練習仍需要專案中的腳本與已安裝工具。')
add('附錄 B · Array 延伸', 'Pruning、PCA、IBD 與 ROH', code('plink1.9 --bfile clean --maf 0.05 \\\n  --indep-pairwise 50 5 0.2 --out prune\nplink1.9 --bfile clean --extract prune.prune.in --genome --out related\nplink1.9 --bfile clean --extract prune.prune.in --pca 4 --out structure\nplink1.9 --bfile clean --homozyg \\\n  --homozyg-snp 100 --homozyg-kb 1000 --out roh'), '50 / 5 / 0.2：視窗位點數／移動位點數／r² 門檻。ROH 使用未 pruning 的 QC genotype。')
add('附錄 B · 移除複本', '只對已知合成複本進行比較', code('awk \'$1=="F02" && $2=="S02" {print $1, $2}\' \\\n  clean.fam > duplicate.remove\nplink1.9 --bfile clean --remove duplicate.remove \\\n  --make-bed --out unrelated_demo')+'<p class="takeaway">預期 39 → 38 人；重新 pruning / PCA 後，<br>PC 的方向、正負號與尺度可能改變。</p>', '不直接套用到病人資料。完整重算指令在學員教材；保留排除清單與人工理由。')
add('附錄 B · 查詢與驗證', '不只留截圖，也留下可重跑的紀錄', code('bcftools query \\\n  -f \'%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT\\t%DP\\t%AD]\\n\' calls.vcf.gz\npython3 ../verify.py .\npython3 --version > versions.txt\nplink1.9 --version >> versions.txt\nsamtools --version >> versions.txt\nbcftools --version >> versions.txt'), '本例 verify.py 核對合成資料結果，不驗證臨床分析效能；Linux/Windows 尚須課前確認環境。')
add('附錄 C · 常見問題', '先查環境，再查資料', table(['現象','先做什麼'],[['command not found','確認 Ubuntu 與工具名稱；不要在 PowerShell 跑 Bash'],['No such file','pwd / ls，確認在 practice01 目錄'],['FileExistsError','產生器保護舊資料；改用新的 practice02'],['結果與預期不同','核對資料、版本與參數，不直接改結果檔'],['無法安裝','使用核准環境或先做表格判讀練習']]), '完整 Windows 安裝與疑難排解，見學員教材附錄。')
add('參考與課後資源', '回到方法定義，也回到原始資料', '<div class="refs"><p><a href="../../lessons/lesson-01-materials.md">第一堂完整學員教材（Markdown）</a> · <a href="../pdf/lesson-01-materials.pdf">PDF 講義</a></p><p><a href="../../demos/lesson-01-genomics/README.md">合成資料與腳本說明</a></p><p><a href="https://www.cog-genomics.org/plink/1.9/basic_stats">PLINK：QC / HWE / heterozygosity</a></p><p><a href="https://www.cog-genomics.org/plink/1.9/ibd">PLINK：IBD / PI_HAT</a></p><p><a href="https://www.htslib.org/doc/samtools.html">SAMtools</a> · <a href="https://samtools.github.io/bcftools/bcftools.html">BCFtools</a> · <a href="https://learn.microsoft.com/en-us/windows/wsl/install">Microsoft WSL</a></p></div>', '來源核對：2026-09-20 · 內部連結需保留專案目錄結構；外部文件需連網。')

CSS = '''
:root{--ink:#183b40;--teal:#087c83;--warm:#b44b27;--paper:#fbf9f3;--muted:#52676d;--scale:1}*{box-sizing:border-box}body{margin:0;background:#152d32;color:var(--ink);font-family:"PingFang TC","Microsoft JhengHei",system-ui,sans-serif}#stage{width:1280px;height:720px;position:absolute;left:50%;top:calc(50% - 25px);transform:translate(-50%,-50%) scale(var(--scale));transform-origin:center}section.slide{width:1280px;height:720px;padding:38px 60px 56px;background:var(--paper);position:relative;display:none;overflow:hidden}section.active{display:block}.eyebrow{font-size:16px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--teal);margin-bottom:18px}h1,h2{font-size:43px;line-height:1.24;letter-spacing:-.02em;margin:0 0 27px;font-weight:800}h3{font-size:27px;line-height:1.35;margin:0 0 16px}p,li{font-size:26px;line-height:1.55;margin:12px 0}ul,ol{padding-left:32px;margin:18px 0}strong{color:var(--teal)}.content{height:485px}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.cards:has(article:nth-child(3):last-child){grid-template-columns:repeat(3,minmax(0,1fr))}.cards article,.panel{padding:26px;background:#edf2ef;border-top:5px solid var(--teal);border-radius:3px}.cards p{margin:0}.split{display:grid;grid-template-columns:1fr 1fr;gap:38px;align-items:start}.flow{display:flex;align-items:stretch;gap:12px;margin:20px 0 32px}.flow div{flex:1;display:flex;align-items:center;justify-content:center;min-height:94px;padding:18px 10px;background:#e1edeb;font-size:26px;text-align:center;border-radius:5px}.flow .arrow{align-self:center;color:var(--teal);font-size:30px}.takeaway{border-left:6px solid var(--warm);padding:10px 18px;background:#f4e9df;margin-top:30px;font-size:27px;line-height:1.45}.big{font-size:52px!important;color:var(--teal);font-weight:800;letter-spacing:-.03em}.formula{font-size:35px;line-height:1.5;color:var(--teal)}.warning{color:var(--warm);font-weight:800}.statline{display:flex;gap:80px;margin:10px 0 26px}.statline b{font-size:67px;color:var(--teal);line-height:1.15}.statline small{display:block;font-size:21px;color:var(--muted);font-weight:500;margin-top:8px}table{width:100%;border-collapse:collapse;font-size:24px;line-height:1.45}th{background:var(--ink);color:white;text-align:left;padding:14px 18px;font-weight:600}td{padding:16px 18px;border-bottom:1px solid #cbd7d4}tr:nth-child(even) td{background:#eef2ec}pre{background:#193a40;color:#f3f7f4;padding:24px 26px;border-radius:6px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:21px;line-height:1.6;margin:14px 0 26px;font-family:Menlo,Consolas,monospace}code{font-family:Menlo,Consolas,monospace}footer{position:absolute;bottom:14px;left:60px;right:60px;display:flex;align-items:end;gap:24px;border-top:1px solid #b6cbc7;padding-top:10px;font-size:15px;line-height:1.4;color:#415b62}.source{flex:1}.page{white-space:nowrap;letter-spacing:.08em;color:var(--teal);font-weight:800}a{color:var(--teal);text-underline-offset:4px}details{margin-top:20px;background:#e7eeeb;border:1px solid #b3c9c4;border-radius:6px;padding:14px 20px;font-size:24px;line-height:1.45}summary{cursor:pointer;font-weight:700;color:var(--teal)}.answer{margin-top:12px}.question{font-size:48px;line-height:1.4;margin:20px 0}.checks li{margin-bottom:15px;font-size:27px}.refs p{margin:16px 0;font-size:26px}.caption{font-size:19px;color:var(--muted)}.cover{background:#193d42!important;color:#f9f7ef}.cover .eyebrow{color:#a8d6c6}.cover h2{font-size:74px;line-height:1.14;margin-top:35px}.cover .subtitle{font-size:38px;margin-top:15px;color:#cbe3d5}.cover .hero-flow{position:absolute;right:70px;top:335px;display:flex;align-items:center;gap:12px;font-size:30px;padding:25px;border-top:2px solid #d6ac75;border-bottom:2px solid #d6ac75;color:#f0d3ae}.hero-flow span{color:#c8e2da}.speaker{position:absolute;bottom:100px;left:60px;font-size:24px}.cover footer,.cover .page{color:#c9dcd4}.closing{background:#e2ece5!important}.coverage{display:flex;align-items:end;justify-content:space-around;height:190px;border-bottom:3px solid var(--ink);padding:0 40px;margin:35px 0 18px}.coverage div{height:var(--h);width:145px;background:var(--teal);text-align:center;color:#fff;font-size:28px;font-weight:bold;padding-top:15px}.coverage .zero{color:var(--warm);background:var(--warm);position:relative;padding:0;line-height:1;transform:translateY(0)}.zero::first-line{line-height:0}.concept-plot{height:290px;border-left:3px solid var(--ink);border-bottom:3px solid var(--ink);position:relative;margin:15px 40px}.cloud{position:absolute;font-size:34px;line-height:1.25}.cloud.a{left:35px;bottom:38px;color:var(--teal)}.cloud.b{right:15px;top:22px;color:var(--warm)}.axis-x{position:absolute;right:-35px;bottom:-32px;font-size:20px}.axis-y{position:absolute;left:-38px;top:-20px;font-size:20px}svg{display:block;width:100%;height:320px}.axis{fill:none;stroke:#617c7c;stroke-width:2}.tick{font-size:16px;fill:var(--muted)}.plot-title{font-size:24px;fill:var(--ink)}nav{position:fixed;bottom:0;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:12px;height:54px;background:#0e262b;color:white;font-size:14px}button{font:inherit;border:1px solid #8fb1ac;background:#23454b;color:white;border-radius:6px;padding:8px 16px;cursor:pointer}button:hover{background:#345e63}button:disabled{opacity:.4;cursor:default}button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #dc843d;outline-offset:3px}#status{min-width:85px;text-align:center}dialog{width:min(940px,92vw);max-height:86vh;border:0;border-radius:12px;background:var(--paper);color:var(--ink);padding:28px}dialog::backdrop{background:#10282bcf}.menuhead{display:flex;justify-content:space-between;align-items:center}#toc{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}#toc button{text-align:left;background:#e2ece8;color:var(--ink);font-size:17px;padding:12px}#toc button[aria-current=true]{background:var(--ink);color:white}.help{font-size:16px}noscript{display:block;padding:30px;color:white}body.nojs #stage{position:static;transform:none;width:100%;height:auto}body.nojs section.slide{display:block;margin-bottom:20px}body.nojs nav{display:none}
.coverage .zero{font-size:0}.coverage .zero::before{content:"0×";position:absolute;bottom:14px;left:0;right:0;font-size:28px;line-height:1}
.allele-example .panel{padding:20px 24px}.allele-example p{font-size:24px;line-height:1.45;margin:12px 0}.allele-example h3{font-size:26px;margin-bottom:14px}.allele-slide .flow{margin:18px 0}.allele-slide .flow div{min-height:80px;font-size:24px;padding:14px 10px}
.mechanism-slide h2{font-size:41px;margin-bottom:14px}.mechanism-slide .mechanism-intro{font-size:22px;line-height:1.3;margin:0 0 12px}.mechanism-slide svg{height:400px}.mechanism-slide .takeaway{font-size:23px;line-height:1.3;margin:12px 0 0;padding:8px 12px}
.hardcall-slide h2{font-size:41px;margin-bottom:20px}.hardcall-slide .hardcall-definition{font-size:24px;line-height:1.45;margin:0 0 14px}.hardcall-slide .flow{margin:14px 0 20px}.hardcall-slide .flow div{min-height:76px;font-size:24px;padding:15px 10px}.hardcall-slide table{font-size:23px}.hardcall-slide th,.hardcall-slide td{padding:13px 16px}.hardcall-slide .takeaway{font-size:24px;line-height:1.45;margin-top:22px;padding:12px 16px}
.metrics-slide h2{margin-bottom:18px}
.metrics-intro{font-size:24px;line-height:1.4;margin:0 0 14px}
.metrics-panels{gap:30px;align-items:stretch}
.metrics-panels .panel{display:grid;grid-template-rows:58px 104px 76px 32px;gap:8px;padding:16px 22px}
.metrics-panels h3{font-size:29px;line-height:1.15;margin:0}
.metrics-panels h3 span{display:block;font-size:20px;line-height:1.2;font-weight:500;margin-top:3px}
.metrics-panels p{font-size:23px;line-height:1.4;margin:0}
.metric-detail{display:flex;flex-direction:column;justify-content:center;gap:8px}
.metrics-panels .metric-formula{font-size:30px;line-height:1.15;color:var(--teal);margin:0}
.metric-formula sub{font-size:65%;vertical-align:baseline;position:relative;top:.2em}
.metrics-panels .metric-r-definition{font-size:21px;line-height:1.35}
.metric-scale{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:0}
.metric-scale div{display:flex;flex-direction:column;justify-content:center;text-align:center;background:#dce9e4;border-top:3px solid var(--teal);padding:5px 3px}
.metric-scale b{display:block;font-size:29px;line-height:1.2;color:var(--teal)}
.metric-scale span{font-size:21px;line-height:1.3}
.metrics-panels .metric-note{font-size:21px;line-height:1.4;margin:0;align-self:center}
.metrics-slide .takeaway{font-size:24px;line-height:1.35;margin:20px 0 0;padding:12px 14px}
.metrics-slide footer{line-height:1.55}
.qc-overview-slide h2{margin-bottom:18px}
.qc-intro{font-size:24px;line-height:1.4;margin:0 0 17px}
.qc-overview-slide table{font-size:23px;line-height:1.45;table-layout:fixed}
.qc-overview-slide th,.qc-overview-slide td{padding:9px 14px}
.qc-overview-slide th:nth-child(1){width:33%}
.qc-overview-slide th:nth-child(2){width:31%}
.qc-case{display:grid;grid-template-columns:180px 1fr;gap:22px;align-items:center;margin-top:20px;padding:13px 18px;background:#f4e9df;border-left:6px solid var(--warm)}
.qc-case>div{display:grid;grid-template-columns:1fr 1fr;align-items:baseline;column-gap:8px}
.qc-case-label{grid-column:1/-1;font-size:18px;color:var(--warm)}
.qc-case b{font-size:34px;line-height:1.3;color:var(--warm)}
.qc-case span:last-child{font-size:16px;white-space:nowrap}
.qc-case p{font-size:23px;line-height:1.5;margin:0}
.qc-conclusion{font-size:24px;line-height:1.4;margin:16px 0 0}
.array-commands-slide h2{margin-bottom:18px}
.array-command-steps{display:grid;gap:12px}
.array-command-steps article{border-left:4px solid var(--teal);padding-left:14px}
.array-command-steps h3{font-size:24px;line-height:1.3;margin:0 0 5px}
.array-command-steps pre{font-size:20px;line-height:1.35;padding:8px 14px;margin:0 0 4px;border-radius:6px}
.array-command-steps p{font-size:21px;line-height:1.4;margin:0}
.array-command-steps p code{font-size:20px;color:var(--teal)}
.array-commands-slide footer{line-height:1.55}
.format-slide h2{font-size:40px;margin-bottom:16px}
.format-intro{font-size:23px;line-height:1.4;margin:0 0 16px}
.format-slide table{table-layout:fixed;font-size:22px;line-height:1.3}
.format-slide th,.format-slide td{padding:8px 14px}
.format-slide th:nth-child(1){width:34%}
.format-slide th:nth-child(2){width:32%}
.format-slide td:first-child{font-size:20px}
.format-slide td strong{font-size:22px}
.format-support{display:grid;grid-template-columns:160px 1fr;gap:16px;background:#f4e9df;border-left:5px solid var(--warm);padding:10px 16px;margin-top:12px;font-size:21px;line-height:1.4}
.format-support b{color:var(--warm)}
.format-slide footer{line-height:1.5}
.ngs-format-slide th,.ngs-format-slide td{padding:7px 14px}
.seq-slide h2{font-size:41px;margin-bottom:18px}
.seq-intro{font-size:24px;line-height:1.4;margin:0 0 18px}
.seq-slide .takeaway{font-size:24px;line-height:1.4;margin:20px 0 0;padding:12px 16px}
.seq-slide .seq-bottom{font-size:23px;line-height:1.45;margin:20px 0 0}
.seq-slide .flow{margin:12px 0 24px}
.seq-slide .flow div{min-height:80px;font-size:24px;padding:14px 10px}
.seq-slide .panel{padding:20px 22px}
.seq-slide .panel h3{font-size:28px;margin-bottom:12px}
.seq-slide .panel p{font-size:24px;line-height:1.55;margin:8px 0}
.seq-table-slide table{font-size:23px;line-height:1.4;table-layout:fixed}
.seq-table-slide th,.seq-table-slide td{padding:15px 14px}
.seq-table-slide th:first-child{width:29%}
.seq-table-slide th:nth-child(2){width:34%}
.seq-analysis-slide th:first-child{width:22%}
.seq-analysis-slide th:nth-child(2){width:40%}
.seq-analysis-slide th,.seq-analysis-slide td{padding:11px 12px;font-size:22px}
.seq-analysis-slide .flow{margin-top:0;margin-bottom:18px}
.seq-analysis-slide .flow div{min-height:64px}
.seq-choice-note{background:#edf2ef;border-left:5px solid var(--teal);padding:14px 18px;margin-top:20px}
.seq-choice-note h3{font-size:25px;margin:0 0 7px}
.seq-choice-note p{font-size:23px;line-height:1.45;margin:0}
.seq-choice-slide th:first-child{width:37%}
.seq-choice-slide th:nth-child(2){width:17%}
.scope-header,.scope-row{display:grid;grid-template-columns:130px 1fr;column-gap:16px}
.scope-header>div{display:grid;grid-template-columns:repeat(3,1fr);text-align:center;font-size:22px;color:var(--muted);margin-bottom:12px}
.scope-row{align-items:center;margin-bottom:12px}
.scope-row>b{font-size:27px;grid-row:span 2}
.scope-track{display:grid;grid-template-columns:repeat(30,1fr);height:22px;align-items:center;background:linear-gradient(transparent 9px,#bac9c5 9px,#bac9c5 13px,transparent 13px)}
.scope-track i{height:22px;background:var(--teal);border-right:2px solid var(--paper)}
.scope-row:nth-child(2) .scope-track i{background:var(--ink)}
.scope-row p{font-size:22px;line-height:1.3;margin:7px 0 0;grid-column:2}
.scope-slide .takeaway{font-size:23px;margin-top:18px}
.depth-tiles{display:grid;grid-template-columns:repeat(5,1fr);gap:9px;margin:10px 0}
.depth-tiles span{padding:6px 4px;background:#dce9e4;color:var(--teal);font-size:25px;font-weight:700;text-align:center;border-top:3px solid var(--teal)}
.depth-tiles .gap{background:#f4e9df;color:var(--warm);border-color:var(--warm)}
@media print{@page{size:1280px 720px;margin:0}body{background:white;-webkit-print-color-adjust:exact;print-color-adjust:exact}#stage{position:static;transform:none;width:1280px;height:auto}section.slide{display:block!important;break-after:page;page-break-after:always}section.slide:last-child{break-after:auto}nav,dialog{display:none!important}details:not([open])>div{display:block!important}summary{display:none}.answer{margin-top:0}}
'''
JS = '''
document.body.classList.remove('nojs');
const slides=[...document.querySelectorAll('.slide')], menu=document.querySelector('#menu');
let current=0;
function fit(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1280,(innerHeight-68)/720));}
function go(index,write=true){current=Math.max(0,Math.min(slides.length-1,index));slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current);});document.querySelector('#status').textContent=`${current+1} / ${slides.length}`;document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;document.querySelectorAll('#toc button').forEach((b,i)=>b.setAttribute('aria-current',i===current));if(write)history.replaceState(null,'',`#slide-${current+1}`);}
function fromHash(){const n=Number(location.hash.replace('#slide-',''));go(Number.isInteger(n)&&n>0?n-1:0,false);}
async function full(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){document.querySelector('#status').textContent='請用瀏覽器全螢幕';}}
document.querySelector('#prev').onclick=()=>go(current-1);document.querySelector('#next').onclick=()=>go(current+1);document.querySelector('#overview').onclick=()=>menu.showModal();document.querySelector('#close').onclick=()=>menu.close();document.querySelector('#fullscreen').onclick=full;document.querySelector('#print').onclick=()=>window.print();
slides.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${String(i+1).padStart(2,'0')} · ${s.dataset.title}`;b.onclick=()=>{go(i);menu.close();};document.querySelector('#toc').appendChild(b);});
document.addEventListener('keydown',e=>{if(menu.open||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea'))return;if(e.key===' '&&e.target.closest('button,summary,a'))return;let next=null;if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key))next=current+1;if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key))next=current-1;if(e.key==='Home')next=0;if(e.key==='End')next=slides.length-1;if(next!==null){e.preventDefault();go(next);}if(e.key.toLowerCase()==='f')full();if(e.key.toLowerCase()==='o')menu.showModal();});
window.addEventListener('resize',fit);window.addEventListener('hashchange',fromHash);fit();fromHash();
'''

def main():
    sections=[]
    for i,s in enumerate(slides,1):
        title_plain=s['title'].replace('<br>',' ')
        sections.append(f'<section class="slide {s["kind"]} {"active" if i==1 else ""}" id="slide-{i}" data-title="{escape(title_plain,quote=True)}" aria-label="第 {i} 張：{escape(title_plain,quote=True)}"><header class="eyebrow">LESSON 01 / {s["section"]}</header><h2>{s["title"]}</h2><div class="content">{s["body"]}</div><footer><div class="source">{s["note"]}</div><div class="page">{i:02d} / {len(slides):02d}</div></footer></section>')
    html='<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第一堂｜從 SNP Array 到 WES/WGS</title><meta name="description" content="高雄長庚臨床生物資訊第一堂課，離線 HTML 投影片"><style>'+CSS+'</style></head><body class="nojs"><noscript>JavaScript 未啟用；以下顯示全部投影片。</noscript><main id="stage">'+''.join(sections)+'</main><nav aria-label="投影片導覽"><button id="prev" aria-label="上一張">← 上一張</button><span id="status" aria-live="polite"></span><button id="next" aria-label="下一張">下一張 →</button><button id="overview">目錄 O</button><button id="fullscreen">全螢幕 F</button><button id="print">列印全部</button></nav><dialog id="menu" aria-labelledby="menu-title"><div class="menuhead"><h3 id="menu-title">第一堂 · 投影片目錄</h3><button id="close">關閉</button></div><p class="help">方向鍵／空白鍵翻頁 · Home／End 首末頁 · Esc 關閉目錄<br>離線播放不需連網；操作練習需另有完整專案與工具。</p><div id="toc"></div></dialog><script>'+JS+'</script></body></html>'
    out=ROOT/'output/slides/lesson-01-genomics.html'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding='utf-8')
    print(f'{len(slides)} slides → {out}')


if __name__=='__main__':
    main()
