"""Build learner-facing, offline RNA-seq slides and reading notes.

Python standard library + Pandoc (already used for the handouts).
Detailed explanations are rendered from the authoritative Lesson 03 handout.
"""
from base64 import b64encode
from html import escape
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/slides'
SLIDES = []
SOURCES = {
    'deseq': ('DESeq2', 'https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html'),
    'gtf': ('GENCODE', 'https://www.gencodegenes.org/pages/data_format.html'),
    'star': ('STAR', 'https://github.com/alexdobin/STAR'),
    'salmon': ('Salmon', 'https://salmon.readthedocs.io/en/latest/salmon.html'),
    'tximport': ('tximport', 'https://bioconductor.org/packages/release/bioc/vignettes/tximport/inst/doc/tximport.html'),
    'fc': ('featureCounts', 'https://subread.sourceforge.net/featureCounts.html'),
    'fastqc': ('FastQC', 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/'),
    'rseqc': ('RSeQC', 'https://rseqc.sourceforge.net/'),
    'sam': ('SAM 規格', 'https://www.htslib.org/doc/sam.html'),
    'rmats': ('rMATS', 'https://github.com/Xinglab/rmats-turbo'),
    'leaf': ('LeafCutter', 'https://davidaknowles.github.io/leafcutter/articles/Usage.html'),
    'dexseq': ('DEXSeq', 'https://bioconductor.org/packages/release/bioc/vignettes/DEXSeq/inst/doc/DEXSeq.html'),
    'igv': ('IGV RNA-seq', 'https://igv.org/doc/desktop/UserGuide/tracks/alignments/rna_seq/'),
    'beavr': ('BEAVR', 'https://github.com/developerpiru/BEAVR'),
    'rnadetector': ('RNAdetector', 'https://doi.org/10.1186/s12859-021-04211-7'),
    'rana': ('RaNA-seq', 'https://ranaseq.eu/'),
    'idep': ('iDEP', 'https://bioinformatics.sdstate.edu/idep/'),
    'workbench': ('OpenAI 官方介紹', 'https://developers.openai.com/blog/rosalind-workbench'),
}


def refs(*keys):
    return ' · '.join(f'<a href="{SOURCES[k][1]}">{SOURCES[k][0]}</a>' for k in keys)


def add(topic, title, body, sections, source='', kind='', extra=''):
    SLIDES.append(dict(topic=topic, title=title, body=body, sections=sections.split(),
                       source=source, kind=kind, extra=extra))


def cards(*items):
    return '<div class="cards">' + ''.join(f'<article><h3>{h}</h3><p>{p}</p></article>' for h, p in items) + '</div>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{x}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>'


def flow(*items):
    return '<div class="flow">' + '<span>→</span>'.join(f'<div>{x}</div>' for x in items) + '</div>'


def take(text):
    return f'<p class="takeaway">{text}</p>'


def code(text):
    return '<pre><code>' + escape(text) + '</code></pre>'


def plot(name, heading, description):
    data = b64encode((ROOT / 'output/lesson-03-demo' / name).read_bytes()).decode()
    return f'<div class="plot"><img src="data:image/png;base64,{data}" alt="合成資料：{escape(heading)}"><article><h3>{heading}</h3>{description}<p class="label">既有 R／DESeq2 合成分析輸出<br>不是病人資料或臨床發現</p></article></div>'


def transcript(rows):
    """Conceptual exon blocks, never a measured genomic track."""
    return '<div class="transcripts" role="img" aria-label="外顯子組合概念示意，非按實際座標繪製">' + ''.join('<div class="transcript"><b>' + label + '</b><div class="exons">' + ''.join(f'<span class="exon {"skip" if x == "—" else ""}">{x}</span>' for x in exons) + '</div></div>' for label, exons in rows) + '</div>'


def igv_example(name, alt):
    """Embed unmodified official screenshots; link to the local original for zooming."""
    data = b64encode((ROOT / 'figures/lesson-03-igv' / name).read_bytes()).decode()
    return f'<a href="../../figures/lesson-03-igv/{name}" target="_blank" rel="noopener noreferrer" title="另開分頁查看原尺寸"><img src="data:image/png;base64,{data}" alt="{escape(alt)}"></a>'


add('第三堂 · 轉錄體', 'Bulk RNA-seq<br>從檢體到差異表現與可變剪接',
    '<p class="subtitle">不只看哪些基因變多，也看 RNA 形式如何改變</p>'
    '<p class="hero">研究問題 → 可比較的數字 → 可查證的結論</p>'
    '<p class="speaker">講師：奇美醫院精準醫學核心實驗室組長邱家軍</p>',
    '1.1 1.4', '高雄長庚臨床生物資訊系列 · 學員版 · 2026-10-05', 'cover')

add('起點 · 研究問題', 'DNA 問「有什麼」，RNA 問「正在使用什麼」',
    cards(('基因體', 'DNA 序列與結構提供可用的資訊；<br>第一、二堂關心基因體的差異。'), ('轉錄體', 'RNA 反映取樣當下的細胞狀態；<br>疾病、治療與處理都可能改變它。'))
    + take('RNA 增加可能來自製造增加或降解減少；不等於蛋白質活性增加。'), '1.1 1.2')

add('背景 · 基因與轉錄本', '一個基因，可以產生不只一種 RNA',
    transcript([('前驅 RNA', ['E1', 'E2', 'E3']), ('成熟形式 A', ['E1', 'E2', 'E3']), ('成熟形式 B', ['E1', '—', 'E3'])])
    + take('Exon 是成熟 RNA 保留的區段，含 UTR；不是每一段都會翻譯成蛋白質。'), '1.1 11.1', refs('gtf') + ' · 原創結構示意，非按長度繪製')

add('背景 · 混合訊號', '免疫基因變高，可能只是免疫細胞變多',
    cards(('假設 A 組：免疫細胞 10%', '每顆免疫細胞產生相同量的基因 X。<br>其餘細胞不表現 X。'), ('假設 B 組：免疫細胞 30%', '即使每顆細胞都沒有改變調控，<br>混合組織仍可能有更多 X 訊號。'))
    + take('Bulk 混合不同細胞的 RNA；RNA 貢獻比例不必等於細胞數比例。'), '1.3', '教學假設；不是以細胞比例直接換算真實 counts')

add('全貌 · 分析地圖', '同一份 RNA 資料，分成兩條證據路徑',
    flow('研究問題／樣本表', 'RNA／文庫', 'FASTQ 與 QC', '比對／定量')
    + cards(('基因總量路徑', 'Gene counts → 正規化／探索<br>→ 設計模型 → 差異表現'), ('RNA 形式路徑', 'Junction／exon／transcript 證據<br>→ 事件與比例 → 剪接／使用差異'))
    + take('Gene count matrix 已彙整掉接合位置；不能靠它還原所有剪接事件。'), '12.2 11.4')

add('設計 · 臨床案例', '先把「想找 biomarker」寫成可分析的比較',
    flow('治療前腫瘤', '依後續反應分 R／NR', '比較 RNA 表現')
    + cards(('先寫清楚', '癌別、採樣時間、反應定義；<br>主要比較為 R 相對 NR，控制已知批次。'), ('先守住界線', '這是反應分組的關聯研究；<br>不是證明 RNA 差異造成療效。')),
    '2.1 2.5', '概念案例；本課合成示範另以 Case／Control 命名，並非真實反應資料')

add('設計 · 研究單位', '5 位病人、10 個 lane，仍是 5 位病人',
    cards(('生物重複', '獨立病人提供族群變異資訊；<br>同病人前後檢體需保留配對關係。'), ('技術重複', '同一文庫分兩次讀取增加深度；<br>不能當成兩位獨立病人。'))
    + take('更多 reads 改善同一樣本的抽樣；更多病人改善群體差異的估計。'), '2.2 2.3 B.1')

add('設計 · 批次效應', '完全混雜時，軟體無法分開疾病與批次',
    table(['安排', 'Batch 1', 'Batch 2', '可辨識性'], [
        ['平衡', 'R 3、NR 3', 'R 3、NR 3', '可建模，仍需 QC'],
        ['部分混雜', 'R 1、NR 5', 'R 5、NR 1', '交叉資訊少，估計較不穩'],
        ['完全混雜', '只有 NR', '只有 R', '無法唯一分開兩種效果'],
    ]) + take('Batch＝製備／操作等系統性差異；應在採樣、建庫安排時避免混雜。'), '2.4 B.5', refs('deseq'))

add('設計 · Metadata', '數字與病人配錯，模型再精密也沒有用',
    table(['欄位', '分析用途'], [
        ['sample_id／patient_id／time', '核對檔案身分、獨立樣本與配對'],
        ['condition／batch', '定義比較、檢查分組與批次交叉表'],
        ['組織／保存／RNA 品質／文庫方向', '回查離群、計數規則與方法適用性'],
    ]) + code('stopifnot(identical(colnames(counts_matrix), rownames(meta)))')
    + '<p class="small">不只名字集合相同，counts 欄與 metadata 列的順序也必須一致。</p>', '2.5 A.2 A.3')

add('檢體 · 品質', 'RIN 與 DV200：看的是不同品質面向',
    cards(('RIN：整體完整性指數', '依電泳峰形與降解分布評分，通常 1–10。<br>不是每個基因的完整率，也不是污染率。'), ('DV200：片段長度分布', '大於 200 nt 的 RNA 訊號比例。<br>60% 不代表六成基因完整或六成可比對。'))
    + take('連同保存方式、輸入量與試劑要求判讀；沒有通用的單一放行門檻。'), '3.1 3.2')

add('製備 · 選到哪些 RNA', 'Poly(A) 富集與 rRNA 去除，不是同一母體',
    table(['策略', '原理／常見用途', '影響分析的限制'], [
        ['Poly(A) selection', '捕捉帶 poly(A) 尾的 RNA；<br>集中成熟 mRNA 訊號', '非 poly(A) RNA 可能流失；<br>降解可造成 3′ 偏差'],
        ['rRNA depletion', '移除高豐度 rRNA；<br>保留較廣的非 rRNA', '可有較多 pre-mRNA／內含子訊號；<br>不能直接當 intron retention'],
    ]) + take('兩組若採不同策略，改變的是可觀察 RNA 集合，不只是總 reads。'), '3.3 3.6 B.11')

add('製備 · 讀段與方向', 'Paired-end 與 strandedness，回答不同問題',
    cards(('Paired-end：同片段兩端', 'R1／R2 來自同一 cDNA 片段；<br>計 fragments 時通常計一次，不是兩個分子。'), ('Strandedness：RNA 來源股', '保留轉錄方向，協助區分重疊基因；<br>reverse-stranded 是設計，不是資料錯誤。'))
    + take('3′ counting 可適合基因總量，卻不保證看得到遠端 exon／junction。'), '3.4 3.5 3.6', refs('rseqc'))

add('資料 · 格式地圖', '先辨認檔案層次，再決定可以分析什麼',
    table(['檔案', '主要內容', '不能當成什麼'], [
        ['FASTQ', 'Read 序列與每個鹼基的品質', '已定位的基因表現量'],
        ['SAM／BAM／CRAM', '比對座標、CIGAR、方向與品質', '最終差異表現結果'],
        ['FASTA ＋ GTF', '參考序列 ＋ gene／transcript／exon 註解', '兩者版本自動相容'],
        ['Counts／quant.sf', '基因計數／轉錄本定量', '兩種可任意互換的 CSV'],
    ]), '4.1 4.2 4.3 4.4 4.5', refs('sam', 'gtf', 'salmon'), 'compact')

add('資料 · 參考與座標', '同樣寫 GRCh38，註解也可能不同',
    code('chrToy  teaching  exon  101  150  .  +  .\ngene_id "G1"; transcript_id "T1";')
    + cards(('GTF：1-based，兩端包含', '101–150 表示 50 個位置。<br>對應 BED 的 100–150。'), ('Assembly ≠ annotation release', '序列組裝與 GENCODE／Ensembl 版次都要記。<br>gene_id、transcript_id 與 symbol 不可混用。'))
    + '<p class="small">上方為換行展示的人工 GTF 概念；正式每筆有 9 個 tab 分隔欄位。</p>', '4.4', refs('gtf'))

add('QC · 原始讀段', 'FastQC 警示，是回查線索，不是淘汰指令',
    table(['看哪個訊號？', '如何解讀？'], [
        ['每位置品質／接頭', '末端品質下降或接頭增加？先查片段長度與實際接頭。'],
        ['GC／過度出現序列', 'RNA 不是隨機基因體取樣；可能是 rRNA、污染或高表現 RNA。'],
        ['重複序列', '可能 PCR 重複，也可能是真實高表現；不能一律去重。'],
    ]) + take('保留處理前後報表；MultiQC 彙整已有證據，不會自動判斷樣本是否可用。'), '5.1 5.2 3.4', refs('fastqc'))

add('QC · RNA 特有檢查', 'Mapping 95%，仍可能沒多少可用 mRNA',
    table(['指標', '想知道什麼？', '需要的背景'], [
        ['Mapping／assigned fraction', '比對得上？能歸給目標基因？', 'rRNA、方向、註解、歸屬規則'],
        ['Exonic／intronic／intergenic', '讀段落在哪些區域？', '富集策略、pre-mRNA、污染'],
        ['Gene-body coverage', '5′ 到 3′ 覆蓋是否偏斜？', '降解或刻意的 3′ 文庫'],
        ['Junction saturation', '多讀一些還增加多少接合點？', '事件覆蓋；不等於臨床 LOD'],
    ]), '5.3 B.2', refs('rseqc'), 'compact')

add('QC · 決策', '補定序、重新製備、暫停推論：不是同一件事',
    cards(('讀段不足，但文庫仍有資訊', '可評估補定序；先看目標區域、<br>文庫複雜度及研究所需證據量。'), ('身分不明／嚴重降解／策略不符', '更多 reads 未必能補救；<br>回查紀錄、製備與可回答的問題。'))
    + take('PCA 離群不能直接刪除；記錄排除理由，必要時做敏感度分析。'), '5.4 8.4')

add('方法 · Splice-aware alignment', 'RNA 的一條 read，可能跨過基因體的內含子',
    transcript([('基因體區段', ['E1', '內含子', 'E2']), ('成熟 RNA', ['E1', '—', 'E2'])])
    + code('CIGAR  50M1000N50M\n50 個對齊位置 → 跳過 1000 個 reference 位置 → 50 個對齊位置')
    + take('STAR 等 RNA 比對器可處理跨內含子定位；N 不直接等於 DNA deletion。'), '4.3 6.1 11.4', refs('star', 'sam'), 'compact')

add('方法 · 定量', '兩條常見路線：先定位到 genome，或估計 transcript',
    cards(('STAR → BAM → featureCounts', '先做剪接感知比對，再依 GTF 歸給基因。<br>保留座標，可回查覆蓋與接合證據。'), ('Salmon → quant.sf → tximport', '對參考轉錄本建立片段相容性與分配模型。<br>再以合適匯入策略進入 gene-level 分析。'))
    + take('共享序列可能無法唯一歸屬；transcript 的估計 counts 出現小數不等於錯誤。'), '6.1 6.2 6.3 6.4', refs('star', 'fc', 'salmon', 'tximport'))

add('方法 · Count matrix', '每格是歸屬計數，不是實際分子總數',
    table(['人工基因', 'S01', 'S02', 'S03'], [['G1', '100', '200', '0'], ['G2', '50', '40', '60']])
    + cards(('列＝基因；欄＝樣本', '確認是 raw counts、TPM 還是 log 值。<br>副檔名 CSV 不能告訴你資料尺度。'), ('0 與 NA 不一樣', '0：沒有觀察到可歸屬片段。<br>NA：缺失／不可估計，不應直接補零。')),
    '1.4 4.5 6.2', '人工表格；讀段／片段計數規則需明確記錄')

add('尺度 · CPM 與 TPM', '長兩倍的 RNA，本來就可能被讀到更多次',
    table(['假設只有兩種 transcript', 'Counts', '有效長度', 'Counts／kb', 'TPM'], [
        ['A', '100', '1 kb', '100', '500,000'], ['B', '200', '2 kb', '100', '500,000'],
    ]) + cards(('CPM', '除以樣本文庫計數總量，再乘一百萬；<br>沒有校正 transcript 長度。'), ('TPM', '先校正長度，再把總和縮放到一百萬；<br>描述相對組成，不是每顆細胞的絕對量。')),
    '7.1 7.2', '簡化算例；實際工具可能使用有效長度與偏差模型')

add('尺度 · 模型輸入', 'TPM 相同，不代表有相同的證據量',
    cards(('文庫 A：TPM＝10', '可能只有 5 個支持片段；<br>抽樣估計的波動較大。'), ('文庫 B：TPM＝10', '可能有 500 個支持片段；<br>相對量一樣，資訊量仍不同。'))
    + take('DESeq2 的 counts 路徑不使用 TPM／FPKM／log 值；Salmon 走 tximport 等支援路徑。'), '7.3 B.4', refs('deseq', 'tximport'))

add('尺度 · 組成偏差', '少數 RNA 暴增，會擠掉其他 RNA 的抽樣名額',
    flow('兩個文庫各讀固定片段數', '某 RNA 占比大幅增加', '其他基因相對 counts 可下降')
    + cards(('為何不能只除以總 reads？', '少數極高表現基因可能主導總量，<br>讓其他基因一起看似下調。'), ('穩健尺度仍有假設', '多數基因需提供相對穩定的參考；<br>全域同方向改變可能需要外加尺度。')),
    '7.4 7.6', 'TMM 與 median-of-ratios 嘗試減少極端組成影響；不是保證恢復絕對量')

add('尺度 · Size factor', '100 與 200 counts，正規化後可能一樣',
    flow('跨樣本建立基因代表量', '各樣本／代表量的比值', '取多個基因比值的中位數')
    + table(['樣本', 'Raw count', '假設 size factor', 'Normalized count'], [
        ['A', '100', '1', '100 ÷ 1＝100'], ['B', '200', '2', '200 ÷ 2＝100'],
    ]) + take('Size factor 是樣本尺度，不是 batch 校正，也不是跨基因的長度校正。'), '7.5 B.3', refs('deseq'))

add('探索 · 資料轉換', 'VST 給探索圖使用；raw counts 留給計數模型',
    cards(('Raw counts → DE 模型', '保留計數的抽樣尺度，<br>由模型處理 size factor 與 dispersion。'), ('VST → PCA／距離／熱圖', '利用均值與變異關係穩定尺度，<br>避免距離過度受極高表現基因主導。'))
    + take('VST 的 blind=FALSE 不是扣掉 batch；不要把轉換後矩陣當成 raw counts。'), '8.1 8.4', refs('deseq'))

add('探索 · PCA', '先看點是誰，再問分開代表什麼',
    plot('01-pca.png', '每個點＝一個合成樣本', '<p>顏色：Control／Case。<br>形狀：B1／B2。</p><p>PC 軸找主要變異方向；<br>百分比不是分類正確率。</p><p>本圖未移除 batch。<br>分群不等於疾病因果。</p>'), '8.2 A.4 B.6', refs('deseq'), 'figure-slide')

add('探索 · 距離圖', '深色代表較遠，不是基因表現較高',
    plot('04-sample-distance.png', '每格＝兩個樣本的距離', '<p>使用 VST 空間的<br>Euclidean distance。</p><p>此圖深色＝距離大；<br>自己對自己是零。</p><p>樹枝依分群規則排列，<br>不是腫瘤演化關係。</p>'), '8.3 A.4', '已執行合成資料；complete-linkage 排序', 'figure-slide')

add('探索 · Heatmap', '熱圖顏色的意思，由你輸入的數字決定',
    cards(('若是 gene row z-score', '每個基因先減自己的平均，再除以標準差。<br>紅色表示相對自己的平均較高；<br>不能跨基因比較絕對表現。'), ('若先挑顯著基因再畫圖', '已利用這批樣本的分組挑選特徵。<br>兩組分開可展示結果；<br>不能當作新病人的預測驗證。'))
    + take('回查色階、轉換與選基因規則；同樣叫 heatmap，不代表同一種量。'), '8.3 B.8')

add('統計 · 跨病人變異', '平均同樣差兩倍，可信度也可能不同',
    cards(('組內差異小', 'Control：90、100、110<br>Case：190、200、210<br>差異相對穩定。'), ('組內差異大', 'Control：0、100、200<br>Case：0、200、400<br>平均同樣 100 對 200，但波動較大。'))
    + take('差異表現同時考慮效應與變異；讀段數不能代替生物重複。'), '9.1 9.2', '人工算例，未對這兩組小樣本執行檢定')

add('統計 · 負二項模型', 'Dispersion 讓模型容納額外的生物變異',
    '<div class="equation">Var(K)＝μ＋αμ²</div>'
    + cards(('μ＝100，Poisson', '變異數等於平均：100。<br>這是簡化的獨立計數抽樣模型。'), ('μ＝100，α＝0.1', '負二項變異數＝100＋0.1×100²＝1100。<br>容許超出簡單抽樣的變異。'))
    + take('α 不是 reads 錯誤率；跨基因借用資訊可穩定估計，卻沒有增加病人數。'), '9.2', refs('deseq'))

add('統計 · Design 與 contrast', '模型控制哪些因素？結果又是誰對誰？',
    code('design = ~ batch + condition\ncontrast = c("condition", "Case", "Control")')
    + cards(('Design：解釋變異的項目', '估計 condition 差異時納入 batch。<br>若兩者完全重疊，就無法分開。'), ('Contrast：指定要報的比較', '這裡是 Case／Control。<br>正 log2FC 表示 Case 較高，不代表好或壞。')),
    '9.3 A.3', refs('deseq'))

add('統計 · 配對與交互作用', '同病人前後比較，不等於兩群獨立病人',
    table(['研究問題', '設計概念', '常見錯誤'], [
        ['同病人治療前後', 'patient ＋ time；保留配對', '把前後當獨立病人'],
        ['不同病人的 Case／Control', '依問題納入必要共變數', '每人一份仍加入所有 patient 固定效果'],
        ['兩組的前後變化是否不同', '直接檢驗 group × time 交互作用', 'A 顯著、B 不顯著就說兩組不同'],
    ]) + take('公式只是模型簡寫；重複測量與巢狀設計必須先確認可辨識性。'), '9.4', refs('deseq'), 'compact')

add('統計 · 效應與不確定性', 'log2FC 告訴你幅度，SE 告訴你估計多穩',
    table(['Case／Control', 'log2FC', '意思'], [['2 倍', '+1', 'Case 較高'], ['一半', '−1', 'Case 較低'], ['4 倍', '+2', '不是增加 2%']])
    + take('低 counts 可出現極端倍數；shrinkage 可穩定弱證據的效應估計。<br>本課合成圖使用未收縮 log2FC，不能宣稱已執行 shrinkage。'), '9.5', refs('deseq'))

add('統計 · 多重檢定', 'p 值與 FDR，都不是單一基因為假的機率',
    cards(('p 值', '在虛無假設與模型成立時，<br>看到目前或更極端統計量的機率。'), ('FDR／BH 調整', '控制被選中集合的錯誤發現比例期望；<br>不是每一基因都有 5% 機率是假。'))
    + table(['人工 p 值', '0.001', '0.010', '0.030', '0.200'], [['BH 校正', '0.004', '0.020', '0.040', '0.200']])
    + '<p class="small">需說明檢定集合；多個 contrast、pathway 與剪接事件不能任意拼湊顯著結果。</p>', '9.6')

add('統計 · 過濾與缺值', '沒有 padj，不一定是「沒有差異」',
    table(['情況', '可能原因／處理'], [
        ['極低 counts', '檢定資訊不足；使用預先規則過濾，記錄被排除的基因。'],
        ['有 p、但 padj 是 NA', '可能是 independent filtering；回查工具設定與平均計數。'],
        ['高影響觀測', 'Cook’s distance 反映某觀測對模型的影響；不等於整位病人應刪掉。'],
    ]) + take('保留完整表與警告；不要把所有 NA 改成零、也不要只留顯著列。'), '9.7', refs('deseq'))

add('實作 · 執行範圍', '這次示範從合成 counts 開始，不是 FASTQ',
    cards(('已有的實際輸出', '3,000 個人工基因、12 個獨立合成樣本；<br>兩批各含 3 Control ＋ 3 Case。<br>DESeq2、VST、PCA、差異表與圖。'), ('未執行的部分', '沒有 FASTQ QC、STAR／Salmon、<br>featureCounts 或正式剪接檢定。<br>PSI 只做算術驗證。'))
    + take('本次保留 2,984 基因；283 個 padj&lt;0.05。這不是研究的目標命中數。'), 'A.1 A.5', '既有 run-summary.txt：R 4.4.2／DESeq2 1.46.0；本次沿用已保存輸出')

add('實作 · 讀懂核心程式', '程式不是黑箱：每行對應一個分析決定',
    code('# 用 raw counts 與樣本表建立物件；模型納入批次\ndds <- DESeqDataSetFromMatrix(counts_matrix, meta,\n                             design = ~ batch + condition)\n# 估計尺度、離散程度並擬合模型\ndds <- DESeq(dds)\n# 明確指定 Case 相對 Control；回傳完整結果\nres <- results(dds, contrast = c("condition", "Case", "Control"))')
    + take('這是主程式節錄；完整腳本另包含樣本對齊、滿秩、低 counts 與輸出檢查。'), 'A.2 A.3', refs('deseq'), 'code-slide')

add('結果 · 讀一列數字', 'GENE0001：效應、標準誤與證據要一起看',
    table(['實際合成輸出欄位', '約值', '怎麼解讀'], [
        ['baseMean', '402.02', 'Normalized counts 平均；不是 TPM'],
        ['log2FoldChange／lfcSE', '1.206／0.243', '估計約 2.31 倍；SE 描述不確定性'],
        ['Wald stat', '4.969', '此情境約為效應除以 SE'],
        ['padj', '1.32 × 10⁻⁵', 'BH 校正後證據；不是臨床效能'],
    ]) + take('不是每個 Case 都剛好是每個 Control 的 2.31 倍。'), '10.1 A.5', 'GENE0001 是人工 ID；數值取自已執行合成資料', 'compact')

add('結果 · MA plot', 'MA 圖：低表現區的倍數可能特別不穩',
    plot('02-ma.png', '每個點＝一個基因', '<p>橫軸：平均 normalized counts。<br>縱軸：未收縮 log2FC。</p><p>藍色：padj&lt;0.05。</p><p>邊界三角形表示超出<br>顯示範圍，不是新事件類型。</p>'), '10.3 A.4', refs('deseq'), 'figure-slide')

add('結果 · Volcano plot', '左右是效應，上下是統計證據',
    plot('03-volcano.png', '先確認縱軸是 p 還是 padj', '<p>本圖縱軸＝−log₁₀(padj)。<br>越高表示 padj 越小。</p><p>右邊＝Case 較高；<br>左邊＝Case 較低。</p><p>圖中沒有各病人分布；<br>仍需回查 counts 與離群值。</p>'), '10.2 A.4', '未收縮 log2FC；水平線 padj＝0.05，非臨床有效性門檻', 'figure-slide')

add('結果 · 判讀練習', '哪一個基因更值得追？不能只看 padj',
    table(['人工候選', 'log2FC', 'padj', '可以說的話'], [
        ['A', '0.2', '0.0001', '證據強，但幅度約 1.15 倍'],
        ['B', '2', '0.20', '估計 4 倍，但證據仍不足'],
        ['C', '−1', '0.01', '估計降低一半，通過所選規則'],
    ]) + take('還要考慮基礎表現、病人一致性、研究問題與驗證可行性。<br>「不顯著」不等於證明無差異；「顯著」不等於臨床可用。'), '10.1 B.7')

add('可變剪接 · 為什麼需要', '基因總量沒變，RNA 形式卻可能翻轉',
    table(['假設分子數', 'Isoform A', 'Isoform B', '基因總量'], [['組 1', '80', '20', '100'], ['組 2', '20', '80', '100']])
    + cards(('Gene-level DE 可能看不到', '總量相同，但兩種形式的使用比例互換。<br>可能改變編碼區，也可能只影響 UTR。'), ('需要更細的證據', 'Transcript、exon 或 junction 層級資訊。<br>不能從一列 gene count 還原結構。')),
    '11.3 B.9', '可直接相加的假設分子數；不是未校正長度的實際 reads')

add('可變剪接 · 分子背景', '剪接體選擇切接位置，連出不同成熟 RNA',
    flow('含 exon／intron 的 pre-mRNA', '剪接體辨識位點', '切除 intron、接合 exon')
    + cards(('5′ splice site／donor', '沿 RNA 方向，內含子靠 5′ 的邊界。<br>不是永遠等於較小的基因體座標。'), ('3′ splice site／acceptor', '沿 RNA 方向，內含子靠 3′ 的邊界。<br>分枝點與調控因子也參與辨識。'))
    + take('Spliceosome 由小核 RNA 與蛋白質組成；剪接差異不一定來自 DNA 突變。'), '11.1')

add('可變剪接 · 局部事件', 'SE 與 MXE：換的是外顯子組合',
    transcript([('SE · 保留', ['E1', 'E2', 'E3']), ('SE · 跳過', ['E1', '—', 'E3']), ('MXE · 擇一', ['E1', 'E2a 或 E2b', 'E3'])])
    + take('SE：skipped exon，保留或跳過 E2。<br>MXE：mutually exclusive exons，在事件模型中選 E2a 或 E2b。'), '11.2', refs('rmats') + ' · 結構示意，不代表完整長距離 isoform 已被重建')

add('可變剪接 · 邊界與滯留', 'A5SS、A3SS 與 RI：不是把整個基因換一條股',
    table(['事件', '局部結構概念', '解讀關鍵'], [
        ['A5SS', '改選 donor：上游 exon 結束邊界不同', '沿轉錄方向辨認 5′，需精確 junction 座標'],
        ['A3SS', '改選 acceptor：下游 exon 開始邊界不同', '沿轉錄方向辨認 3′，不是股向翻轉'],
        ['RI', '原本剪掉的 intron，在部分 RNA 中保留', '整合 intron、邊界與已剪接 junction 證據'],
    ]) + take('Intronic reads 多也可能來自 pre-mRNA、DNA 污染或製備差異，不能直接宣稱 RI。'), '11.2 B.11', refs('rmats'), 'compact')

add('可變剪接 · 問題層級', 'DGE、DTE、DTU、DEU，不是四個同義詞',
    table(['分析', '觀察單位', '問的是什麼？'], [
        ['DGE', 'Gene', '基因整體 RNA 訊號是否改變？'],
        ['DTE', 'Transcript', '某一種 RNA 形式的量是否改變？'],
        ['DTU', 'Transcript／其 gene', '同基因內各形式的比例是否改變？'],
        ['DEU', 'Exon／counting bin', '某區段相對同基因其他區段是否改變？'],
    ]) + take('若 A／B 從 80／20 變 160／40：總量變兩倍，比例卻仍是 80%／20%。'), '11.3', 'Transcript 使用改變也可能來自起始點或末端加工，不一定全是剪接', 'compact')

add('可變剪接 · 證據', 'E1 的 read 只支持基因；E1–E3 才支持跳過 E2',
    transcript([('包含 E2', ['E1', 'E2', 'E3']), ('跳過 E2', ['E1', '—', 'E3'])])
    + cards(('共同 exon 內的 reads', '兩種形式都會產生，不能區分路徑。<br>E2 覆蓋降低也可能是整個基因變低。'), ('Junction reads', '跨接合的 reads 提供局部連接證據。<br>兩側 anchor 太短或多重比對時需小心。')),
    '11.4', refs('star', 'igv') + ' · 示意非實際 IGV 軌道')

add('可變剪接 · PSI', 'PSI：可辨識形式中，包含事件的比例',
    '<p class="small">Percent spliced in；常以 0–1 表示，0.8 即 80%。</p><div class="equation">PSI＝(I／L<sub>I</sub>) ÷ [(I／L<sub>I</sub>)＋(S／L<sub>S</sub>)]</div>'
    + table(['符號', '意義'], [['I／S', 'Inclusion／skipping（或另一形式）的支持計數'], ['Lᵢ／Lₛ', '各形式可產生可辨識讀段的有效長度']])
    + take('等有效長度時，80／(80＋20)＝0.8。<br>若 Lᵢ＝200、Lₛ＝100，同樣計數得到 0.667，不是 0.8。'), '11.5', refs('rmats') + ' · 有效長度依事件與讀取方式，非任意 exon 長度')

add('可變剪接 · 幅度與證據量', 'ΔPSI＝−0.25，是下降 25 個百分點',
    table(['教學情境', '結果', '限制'], [
        ['PSI_A＝0.60、PSI_B＝0.35', '定義 B−A：−0.25', '不是下降 0.25%，也不是相對下降 25%'],
        ['等長：I／S＝8／2 或 800／200', 'PSI 都是 0.8', '比例相同，支持量不同'],
        ['I＝0、S＝0', '不可估計', '不能填 PSI＝0'],
    ]) + take('方向必須看工具：rMATS 的 IncLevelDifference 是第一組減第二組。'), '11.5 11.6 B.10', refs('rmats'), 'compact')

add('可變剪接 · 工具', '先選問題，再選事件、intron cluster 或 exon bin',
    table(['方法', '主要證據／問題', '不能直接取代'], [
        ['rMATS', 'SE／A5SS／A3SS／MXE／RI；<br>JC 或 JCEC 計數比較', '任意臨床共變數設計；須查版本能力'],
        ['LeafCutter', 'Split reads 建 intron clusters；<br>比較相對切除路徑', '完整 RI 評估與完整 isoform 重建'],
        ['DEXSeq', 'Exon bins 的相對使用', '指定唯一完整 transcript'],
    ]) + take('每位病人保留獨立證據；不要合併兩組 BAM 後只比較兩個大檔案。'), '11.6 11.7', refs('rmats', 'leaf', 'dexseq'), 'compact')

add('可變剪接 · 局部回查', 'Sashimi plot 是接合證據，不是完整 RNA 照片',
    '<div class="sashimi-grid"><figure>'
    + igv_example('SL_Sashimi1.png', 'IGV 官方 SLC25A3 Sashimi 範例：heart、kidney、liver 的 coverage、junction 弧線與下方轉錄本註解')
    + '<figcaption>官方範例：紅 heart／藍 kidney／綠 liver；點圖看原尺寸。</figcaption></figure><article><h3>先看 split read 如何跨接合點</h3>'
    + igv_example('alignments-rnaseq-zoomedin-selection.png', 'IGV 官方另一張 split-read 範例：紅色高亮的同一條 read 分成兩段，中間由細藍線連接')
    + '<p class="split-caption">另一官方範例：紅色兩段屬同一 read；<br>細藍線跨過未比對的 intron 區段。</p>'
    + '<p><b>① 山峰＝coverage</b><br>每個位置有多少 reads 覆蓋。</p>'
    + '<p><b>② 弧線＝junction</b><br>數字如 2890 是支持 reads 數，非 PSI。</p>'
    + '<p><b>③ 下方藍色模型＝註解</b><br>不是本次證明的完整 RNA；<br>左圖三軌縱軸不同，勿直接比較峰高。</p></article></div>'
    + take('弧線只支持局部接合；比較樣本前，須核對深度、尺度與生物重複。'),
    '11.8', refs('igv') + ' · 圖片：IGV team 官方文件；原圖等比例縮放，非本課執行結果', 'sashimi-slide',
    '''### 官方範例圖怎麼讀

左圖是 IGV 文件的 SLC25A3 範例，三種顏色標示 heart、kidney、liver 軌道，不是在此表示正反股。山峰顯示 coverage，弧線連接 splice junction，數字是跨該接合點的 reads 數；例如 2890 不是 PSI，也不是 2890 位病人。下方藍色模型是參考註解，不能因此認定樣本具有該完整轉錄本。

三軌的 coverage 上限分別為 11850、5842、5313，因此相似峰高不等於相似讀取深度。原始 junction 計數也受總深度影響，不能直接當成剪接比例差異或統計顯著性。須回查各病人的支持、比較尺度與正式事件分析；局部 junction 無法把遠端事件串成唯一完整 RNA。

右上圖是另一個獨立的官方 split-read 範例，不能與左圖當成相同座標。紅色只是選取高亮：同一 read 的兩個比對區塊由細藍線連接，中間是相對參考基因組跳過的區段；不能把細線解讀成 intron 也被定序覆蓋。

### 在 IGV 中開啟

先將主視窗移至涵蓋目標區域的範圍，在 RNA-seq alignment 軌道按右鍵選 Sashimi Plot，再依提示選註解與樣本軌道。比較前核對 genome／annotation／股向、coverage 尺度及 junction 顯示門檻；未顯示的弧線不必然等於沒有支持 reads。

本頁是官方圖片的教學引用，非本課重新執行 IGV、亦非院內病人分析。原圖未裁切或改動數值，可點圖另開原尺寸；圖片來源及查核紀錄見 [第三堂來源記錄](../../sources/lesson-03-slides-sources.md)。
''')

add('可變剪接 · 驗證', 'RNA 結構改變，不等於蛋白質功能已改變',
    flow('回查比對與事件', '獨立樣本／接合驗證', '編碼／NMD 假說', '蛋白與功能證據')
    + cards(('結構驗證', 'RT-PCR／接合專一 RT-qPCR 或長讀長；<br>擴增效率、覆蓋與偏差仍需評估。'), ('功能驗證', 'UTR 改變可能不換蛋白序列；<br>提前終止可涉及 NMD，但不是一律發生。'))
    + take('NMD 是無義介導的 RNA 降解；RNA 量反映製造、加工與降解後的結果。'), '11.9 B.12')

add('交付 · 可重現性', '拿到圖以前，先確認可追溯的資料包',
    table(['輸入／設定', '輸出／稽核'], [
        ['Counts 或 FASTQ、metadata、QC', '完整差異表、可分析／排除清單與原因'],
        ['Genome／GTF、軟體版本、參數', '程式、執行紀錄、圖的尺度與選基因規則'],
        ['Design、contrast、事前規則', '效應與不確定性、限制、下一步驗證'],
    ]) + take('候選清單交給第四堂做 pathway 等分析時，仍要保留背景基因集合與比較方向。'), '12.1 12.2 12.3')

add('課後 · 取用與重現', '從已保存的圖，回到程式與方法文件',
    code('Rscript --vanilla demos/lesson-03-bulk-rnaseq/run-demo.R \\\n  output/lesson-03-demo-rerun')
    + '<p>先準備 R 與相容的 DESeq2；於專案根目錄執行。<br>輸出資料夾須為新名稱；本指令不會在瀏覽器內執行。</p>'
    + '<p class="resource"><a href="../pdf/lesson-03-materials.pdf">完整 PDF 講義</a> · <a href="../../demos/lesson-03-bulk-rnaseq/README.md">示範與程式說明</a><br><a href="../../sources/lesson-03-slides-sources.md">投影片來源與範圍</a> · <a href="lesson-03-explanations.html">全部逐頁詳解</a></p>',
    'A.1 A.6', '主張界線：已執行 counts 示範，不是完整 FASTQ pipeline；外部方法文件見各頁來源')

add('工具比較 · 如何選', '四個 RNA-seq 工具：本堂優先使用 iDEP',
    table(['工具', '起點／分析重點', '課堂使用考量'], [
        ['<a href="https://github.com/developerpiru/BEAVR" target="_blank" rel="noopener noreferrer" title="開啟 BEAVR 專案頁（另開分頁）">BEAVR</a>', 'Counts → DESeq2、探索與視覺化', '聚焦下游；需先部署 R／Docker 環境'],
        ['<a href="https://github.com/knowmics-lab/RNAdetector" target="_blank" rel="noopener noreferrer" title="開啟 RNAdetector 專案頁（另開分頁）">RNAdetector</a>', 'FASTQ／BAM／SAM → 定量、DE 等', '流程廣；安裝、Docker 與參考資料準備較多'],
        ['<a href="https://ranaseq.eu/" target="_blank" rel="noopener noreferrer" title="開啟 RaNA-seq 網站（另開分頁）">RaNA-seq</a>', 'FASTQ／公開 accession → QC、定量、DE', '網頁端全流程；需預留上傳與運算等待'],
        ['<a href="https://bioinformatics.sdstate.edu/idep/" target="_blank" rel="noopener noreferrer" title="開啟 iDEP 網站（另開分頁）">iDEP ★</a>', 'Gene counts → PCA、DE、富集與圖表', '適合本堂即時判讀；不取代 FASTQ QC／比對'],
    ]) + take('推薦是依本堂教學目標，不是準確度排名。Gene counts 介面也不等於完成剪接分析。'),
    '', refs('beavr', 'rnadetector', 'rana', 'idep') + ' · 2026-10-05 文件查核；未宣稱完成四站實測', 'tools',
    '''### 如何選擇

這四個工具的分析起點不同。BEAVR 以計數矩陣與分組資訊進入 DESeq2，適合集中展示下游結果，但 browser-based 只表示用瀏覽器操作，不保證有免安裝的公共伺服器。RNAdetector 涵蓋原始讀段、比對與定量到下游分析；準備 Docker、後端與參考資源的負擔較大，較適合較長的實作課。RaNA-seq 適合展示從 FASTQ 或公開資料起步的流程，但必須預留上傳、排程與運算時間。iDEP 的計數矩陣探索、差異表現與視覺化最貼近本堂目標，因此作為首選。

### 課堂前要確認

先用相同公開資料測試上傳、樣本對齊、物種與 ID 辨識、比較方向、batch 模型及結果匯出，再保存離線圖與完整結果備援。若要銜接 pathway，需使用真實且可辨識的基因 ID；本課 GENE0001 等合成 ID 不能用來宣稱真實富集。iDEP 可接受的表現尺度不代表 DESeq2 可直接使用 TPM。複雜配對與連續共變數設計須另核對介面及方法限制。

### 已查核的邊界

本頁比較依官方文件與原始論文整理，未執行四套平台的端到端分析，也未驗證當天服務容量。沒有把一般基因表現 GUI 當成完整剪接事件分析工具。功能、存取及部署條件會更新；課前需重新測試。院內序列或 metadata 不可任意上傳外部服務。
''')

add('AI 協作 · 延伸到第九堂', 'OpenAI NGS Analysis Workbench',
    '<p class="intro">將研究問題、分析工具與執行證據串在一起的工作環境；不是新的 DE 演算法。</p>'
    + flow('理解資料', '設計分析', '審核計畫後執行', '檢查結果／限制')
    + cards(('可以協助什麼？', '核對輸入與 metadata、選擇適用流程，<br>協調工具執行，保留計畫、版本與紀錄。'), ('人員仍需負責什麼？', '確認研究單位、模型、QC 與資料權限；<br>完成執行不等於結論有效，更不是臨床驗證。'))
    + take('本課只介紹；實際可用流程、運算環境與帳號權限須查核。不要上傳未核准病人資料。'),
    '', refs('workbench') + ' · 官方插件 0.2.16 文件；2026-10-05 查核，本次未啟動 NGS 分析', 'workbench',
    '''### 定位與操作概念

OpenAI 的公開介紹以 RNA-seq 等引導式任務說明 NGS Analysis Workbench：讓研究問題與資料處理保持連結，先提出供研究人員審查的計畫，再協調工具並回傳可追溯輸出。它不是把 DESeq2、STAR 等方法換成一個語言模型，也不是保證所有人已有可用帳號或運算資源。

### 從資料到可查證的結果

本次安裝的官方插件 0.2.16 將能力分為理解資料、設計分析、執行核准流程與理解結果。執行前須查可用流程及版本、計算目標與環境、輸入和參考是否就緒，再建立具有身分與校驗資訊的計畫；實際執行須通過產品的核准機制。文件涵蓋 Nextflow 與 Snakemake 路徑，但找到流程不等於適用，環境就緒也不等於研究設計成立。

### 本堂可用的提問示例與限制

可提問：「這是一份公開 bulk RNA-seq counts 與 sample sheet。請先核對樣本對齊、獨立重複、批次混雜與比較方向，提出分析計畫並列出缺失資訊，尚不要執行。」此處是提問示例，不是已執行結果。若之後執行，應回查真實輸出、錯誤與部分完成狀態，保存程式、版本及 provenance。不能把 agent 的文字解釋當成數值已驗證，也不能讓它自行決定排除病人或形成臨床診斷。本頁為功能介紹，不是安裝或權限保證；進一步操作留待第九堂。
''')


CSS = r'''
:root{--ink:#183b40;--teal:#087c83;--paper:#fbf9f3;--scale:1}*{box-sizing:border-box}body{margin:0;background:#152d32;color:var(--ink);font-family:"PingFang TC","Microsoft JhengHei",system-ui,sans-serif}a{color:var(--teal);text-underline-offset:3px}
#stage{width:1280px;height:720px;position:absolute;left:50%;top:calc(50% - 28px);transform:translate(-50%,-50%) scale(var(--scale));transform-origin:center}.slide{width:1280px;height:720px;padding:36px 56px 65px;background:var(--paper);display:none;position:relative;overflow:hidden}.slide.active{display:block}.eyebrow{font-size:16px;font-weight:700;letter-spacing:.1em;color:var(--teal);margin-bottom:17px}h2{font-size:38px;line-height:1.28;margin:0 0 24px;font-weight:800}h3{font-size:27px;line-height:1.35;margin:0 0 16px}p{font-size:25px;line-height:1.5;margin:15px 0}.content{height:480px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:18px 0}.cards article{padding:23px;background:#edf2ef;border-top:5px solid var(--teal)}.cards p{margin:0;font-size:24px}.takeaway{border-left:6px solid #a94b27;background:#f4e9df;padding:14px 18px;font-size:25px;line-height:1.45;margin-top:25px}.flow{display:flex;align-items:center;gap:12px;margin:18px 0 24px}.flow div{flex:1;padding:22px 14px;background:#e1edeb;font-size:24px;line-height:1.45;text-align:center;border-radius:5px}.flow>span{font-size:28px;color:var(--teal)}
table{width:100%;border-collapse:collapse;font-size:24px;line-height:1.42}th{background:var(--ink);color:white;text-align:left;padding:12px 15px}td{padding:13px 15px;border-bottom:1px solid #bdcfca}tr:nth-child(even){background:#edf2ef}.compact table,.tools table{font-size:23px}.compact td,.tools td{padding:11px 14px}.compact .takeaway,.tools .takeaway{font-size:24px;margin-top:20px}.equation{padding:20px;background:#e1edeb;font-size:32px;color:var(--teal);text-align:center;margin:16px 0 24px}pre{background:#193a40;color:#f3f7f4;border-radius:6px;padding:18px 22px;white-space:pre-wrap;overflow-wrap:anywhere;font:21px/1.5 Menlo,Consolas,monospace;margin:20px 0}code{font-family:Menlo,Consolas,monospace}.code-slide pre{font-size:22px}.small{font-size:22px}.intro{font-size:25px}.resource{line-height:1.8}
.transcripts{background:#edf2ef;padding:18px 24px;margin:15px 0 24px}.transcript{display:flex;align-items:center;gap:30px;margin:15px 0}.transcript>b{width:210px;font-size:25px}.exons{display:flex;align-items:center;gap:25px;flex:1;background:linear-gradient(transparent 48%,#8da6a0 48%,#8da6a0 52%,transparent 52%)}.exon{flex:1;padding:13px 10px;text-align:center;background:#087c83;color:white;font-size:26px;border-radius:4px}.exon.skip{background:#edf2ef;color:#526b67;border:2px dashed #8da6a0}
.plot{display:grid;grid-template-columns:770px 1fr;gap:26px;align-items:center}.plot img{width:770px;height:465px;object-fit:contain;background:white}.plot article p{font-size:23px;line-height:1.48}.plot h3{font-size:25px}.plot .label{font-size:17px;border-top:1px solid #adc2bd;padding-top:12px}.figure-slide h2{margin-bottom:16px}
.sashimi-slide h2{font-size:36px;margin-bottom:16px}.sashimi-grid{display:grid;grid-template-columns:704px 1fr;gap:24px;align-items:start}.sashimi-grid figure{margin:0}.sashimi-grid a{display:block}.sashimi-grid img{display:block;width:100%;height:auto}.sashimi-grid figcaption{font-size:18px;line-height:1.5;margin-top:8px}.sashimi-grid h3{font-size:24px;margin:0 0 10px}.sashimi-grid article p{font-size:22px;line-height:1.4;margin:12px 0 0}.sashimi-grid article .split-caption{font-size:20px;margin-top:8px}.sashimi-slide .takeaway{font-size:23px;margin-top:14px;padding:10px 16px}
footer{position:absolute;left:56px;right:56px;bottom:14px;border-top:1px solid #b6cbc7;padding-top:10px;display:flex;gap:20px;font-size:15px;line-height:1.4;color:#415b62}.source{flex:1}.page{white-space:nowrap;font-weight:800;color:var(--teal)}.cover{background:#193d42;color:#f9f7ef}.cover .eyebrow{color:#a8d6c6}.cover h2{font-size:54px;line-height:1.25;margin:45px 0 30px}.cover .subtitle{font-size:30px;color:#cbe3d5}.hero{font-size:31px;color:#f0d3ae;border-top:2px solid #d6ac75;padding-top:25px;margin-top:32px}.speaker{position:absolute;bottom:85px;font-size:23px}.cover footer,.cover .page{color:#c9dcd4}.workbench h2{font-size:40px}.workbench .cards{margin:12px 0}.workbench .cards article{padding:18px 22px}.workbench .takeaway{font-size:23px;margin-top:18px}
nav{position:fixed;bottom:0;left:0;right:0;background:#0e262b;color:white;height:54px;display:flex;align-items:center;justify-content:center;gap:12px;font-size:14px}button{font:inherit;padding:8px 15px;border:1px solid #8fb1ac;background:#23454b;color:white;border-radius:6px;cursor:pointer}button:disabled{opacity:.4}button:focus-visible,a:focus-visible{outline:3px solid #dc843d;outline-offset:3px}#status{min-width:75px;text-align:center}dialog{width:min(1050px,94vw);max-height:87vh;background:var(--paper);color:var(--ink);border:0;border-radius:10px;padding:30px 38px}dialog::backdrop{background:#10282bcf}.menuhead{display:flex;justify-content:space-between;align-items:center;gap:20px}#toc{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}#toc button{background:#e2ece8;color:var(--ink);text-align:left;font-size:17px}#toc button[aria-current=true]{background:var(--ink);color:white}#explain h2{font-size:30px;margin:24px 0}#explain h3,#explain h4{font-size:25px;margin:26px 0 12px}#explain p,#explain li{font-size:22px;line-height:1.8}#explain table{font-size:19px;display:block;overflow:auto}#explain pre{font-size:17px}#explain img{max-width:100%}.help{font-size:17px}body.nojs #stage{position:static;transform:none;width:100%;height:auto}body.nojs .slide{display:block;margin-bottom:20px}body.nojs nav{display:none}noscript{display:block;padding:25px;color:white}
@media print{@page{size:1280px 720px;margin:0}body{background:white;-webkit-print-color-adjust:exact;print-color-adjust:exact}#stage{position:static;transform:none;width:1280px;height:auto}.slide{display:block!important;break-after:page}.slide:last-child{break-after:auto}nav,dialog,noscript{display:none!important}}
'''

JS = r'''
document.body.classList.remove('nojs');
const slides=[...document.querySelectorAll('.slide')], menu=document.querySelector('#menu'), explain=document.querySelector('#explain');let current=0;
function fit(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1280,(innerHeight-68)/720));}
function go(i,write=true){current=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,j)=>{s.classList.toggle('active',j===current);s.setAttribute('aria-hidden',j!==current)});document.querySelector('#status').textContent=`${current+1} / ${slides.length}`;document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;document.querySelectorAll('#toc button').forEach((b,j)=>b.setAttribute('aria-current',j===current));if(write)history.replaceState(null,'',`#slide-${current+1}`);}
function fromHash(){const n=Number(location.hash.replace('#slide-',''));go(Number.isInteger(n)&&n>0?n-1:0,false);}
function showExplanation(){document.querySelector('#explain-title').textContent=`${current+1} / ${slides.length} · ${slides[current].dataset.title}`;document.querySelector('#explain-body').replaceChildren(slides[current].querySelector('template').content.cloneNode(true));document.querySelector('#reading-link').href=`lesson-03-explanations.html#page-${current+1}`;explain.showModal();explain.scrollTop=0;}
async function full(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{document.querySelector('#status').textContent='請用瀏覽器全螢幕';}}
document.querySelector('#prev').onclick=()=>go(current-1);document.querySelector('#next').onclick=()=>go(current+1);document.querySelector('#overview').onclick=()=>menu.showModal();document.querySelector('#close').onclick=()=>menu.close();document.querySelector('#explanation').onclick=showExplanation;document.querySelector('#explain-close').onclick=()=>explain.close();document.querySelector('#fullscreen').onclick=full;document.querySelector('#print').onclick=()=>window.print();
slides.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${i+1} · ${s.dataset.title}`;b.onclick=()=>{go(i);menu.close()};document.querySelector('#toc').appendChild(b)});
document.addEventListener('keydown',e=>{if(menu.open||explain.open||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea'))return;if(e.key===' '&&e.target.closest('button,a'))return;let i=null;if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key))i=current+1;if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key))i=current-1;if(e.key==='Home')i=0;if(e.key==='End')i=slides.length-1;if(i!==null){e.preventDefault();go(i)}if(e.key.toLowerCase()==='f')full();if(e.key.toLowerCase()==='o')menu.showModal();if(e.key.toLowerCase()==='e')showExplanation()});
window.addEventListener('resize',fit);window.addEventListener('hashchange',fromHash);fit();fromHash();
'''


def handout_sections():
    text = (ROOT / 'lessons/lesson-03-materials.md').read_text()
    result = {}
    for match in re.finditer(r'^### ([A-Z]|\d+)\.(\d+) ([^\n]+)\n(.*?)(?=^## |^### |\Z)', text, re.M | re.S):
        key = f'{match[1]}.{match[2]}'
        assert key not in result
        # Handout-relative paths need one more parent from output/slides.
        result[key] = f'### {key} {match[3]}\n{match[4]}'.replace('](../', '](../../')
    return result


def main():
    parts = handout_sections()
    pages, readings = [], []
    for i, s in enumerate(SLIDES, 1):
        assert all(k in parts for k in s['sections']), (i, s['sections'])
        md = '\n\n'.join(parts[k] for k in s['sections']) + '\n\n' + s['extra']
        notes = subprocess.run(['pandoc', '--from=gfm', '--to=html5', '--wrap=none', f'--id-prefix=page-{i}-'],
                               input=md, text=True, capture_output=True, check=True).stdout
        assert len(notes) > 100, s['title']
        title = escape(s['title'].replace('<br>', ' '))
        source = s['source'] or '依第三堂完整學員講義整理；按 E 展開原理、例子與限制'
        notes += f'<p class="help">{source}</p>'
        # Tool comparison keeps references in the notes, with only a page number below.
        footer_source = '' if s['kind'] == 'tools' else source
        pages.append(f'<section class="slide {s["kind"]} {"active" if i==1 else ""}" id="slide-{i}" data-title="{title}" aria-label="第 {i} 張：{title}"><header class="eyebrow">LESSON 03 / {s["topic"]}</header><h2>{s["title"]}</h2><div class="content">{s["body"]}</div><template>{notes}</template><footer><span class="source">{footer_source}</span><span class="page">{i:02d} / {len(SLIDES):02d}</span></footer></section>')
        readings.append(f'<article id="page-{i}"><h2>{i:02d} · {title}</h2>{notes}<p><a href="lesson-03-bulk-rnaseq.html#slide-{i}">回到投影片</a></p></article>')
    head = '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html = head + '<title>第三堂｜Bulk RNA-seq 與可變剪接</title><style>' + CSS + '</style></head><body class="nojs"><noscript>JavaScript 未啟用；以下顯示全部投影片。<a href="lesson-03-explanations.html">閱讀逐頁詳解</a></noscript><main id="stage">' + ''.join(pages) + '''</main><nav aria-label="投影片導覽"><button id="prev">← 上一張</button><span id="status" aria-live="polite"></span><button id="next">下一張 →</button><button id="overview">目錄 O</button><button id="explanation">逐頁詳解 E</button><button id="fullscreen">全螢幕 F</button><button id="print">列印全部</button></nav><dialog id="menu" aria-labelledby="menu-title"><div class="menuhead"><h3 id="menu-title">第三堂 · 內容目錄</h3><button id="close">關閉</button></div><p class="help">方向鍵／空白鍵翻頁 · Home／End 首末頁 · Esc 關閉<br>正文可離線播放；工具網站與參考連結需網路。</p><div id="toc"></div></dialog><dialog id="explain" aria-labelledby="explain-title"><div class="menuhead"><a id="reading-link" href="lesson-03-explanations.html" target="_blank" rel="noopener">閱讀／列印全部詳解 ↗</a><button id="explain-close">關閉 Esc</button></div><h2 id="explain-title"></h2><div id="explain-body"></div></dialog><script>''' + JS + '</script></body></html>'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'lesson-03-bulk-rnaseq.html').write_text(html)
    reading_css = 'body{max-width:1000px;margin:40px auto;padding:0 30px;background:#fbf9f3;color:#183b40;font-family:"PingFang TC","Microsoft JhengHei",sans-serif}h1{font-size:34px}h2{font-size:30px}h3{font-size:25px}p,li{font-size:22px;line-height:1.85}article{padding:30px 0;border-bottom:1px solid #abc1bc}a{color:#087c83}img{max-width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:17px;line-height:1.6;background:#e2ece8;padding:18px}table{border-collapse:collapse;font-size:18px}th,td{padding:10px;border:1px solid #abc1bc}nav a{display:block;line-height:1.8}.help{font-size:17px}@media print{nav{display:none}article{break-before:page}p,li{font-size:12pt}h2{font-size:18pt}h3{font-size:15pt}}'
    toc = ''.join(f'<a href="#page-{i}">{i:02d} · {escape(s["title"].replace("<br>", " "))}</a>' for i, s in enumerate(SLIDES, 1))
    (OUT / 'lesson-03-explanations.html').write_text(head + '<title>第三堂｜逐頁詳解</title><style>' + reading_css + '</style></head><body><h1>Bulk RNA-seq 與可變剪接 · 逐頁詳解</h1><p>講師：奇美醫院精準醫學核心實驗室組長邱家軍</p><p>依完整學員講義擷取對應章節；可搭配投影片或列印閱讀。教學假設、合成輸出與方法介紹均非臨床發現。</p><nav>' + toc + '</nav>' + ''.join(readings) + '</body></html>')
    for i, s in enumerate(SLIDES, 1):
        print(f'{i:02d} {s["title"].replace("<br>", " ")}')
    print(f'{len(SLIDES)} slides → {OUT / "lesson-03-bulk-rnaseq.html"}')


if __name__ == '__main__':
    main()
