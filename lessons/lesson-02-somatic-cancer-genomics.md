# Lesson 02 — 癌症體細胞基因體分析

完整學員教材：[癌症體細胞基因體分析：從定序證據到可信的候選事件](lesson-02-materials.md)。含基本與延伸練習、結果解析，以及 Windows／WSL2、macOS、Linux 的安裝、腳本執行、結果驗證與 IGV 操作附錄；學員教材不標示各段時長。以下保留原始精簡教案供排課參考。

## 課程簡介

本課程以腫瘤定序資料流為主軸，比較 tumor–normal 與 tumor-only 分析設計，說明 FASTQ、BAM/CRAM、VCF/MAF 到 SNV、indel、CNV、SV 結果的產生過程。課程將透過 depth、VAF、腫瘤純度、拷貝數、FFPE artifact 與 IGV 等實例，帶領學員判斷分析品質、辨認偽陽性並理解不同演算法輸出的限制。

## 課程目標

完成本堂後，學員能：

1. 說明 tumor–normal 與 tumor-only 的輸入資料、分析設計及可辨識資訊差異。
2. 說明 SNV/indel、CNV 與 SV 從 alignment 到 calling、filtering 及 annotation 的資料流。
3. 使用 depth、alternate reads、VAF、tumor purity、copy number 與 IGV 判讀 somatic call 的技術可信度。

## 臨床案例

研究團隊取得一批肺腺癌 FFPE 樣本，其中部分具有 matched normal，部分只能進行 tumor-only 分析；一個樣本出現 5% VAF 的候選變異。

- 決策：應採用何種 calling/filtering 流程，這個低 VAF variant 是否為可重現的技術訊號？
- 比較：matched normal 可得與不可得時，germline filtering、artifact control 與結果可信度有何不同？
- 不回答：特定藥物處方或正式臨床 actionability 分級。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–10 | 分析問題 | 定義 somatic event 與資料需求；matched normal 是否可得 | 選擇 tumor–normal 或 tumor-only 流程 |
| 10–20 | 檢體與資料 | Tumor cellularity、FFPE damage、depth、UMI、tumor–normal | 判斷哪些 metadata 不能缺 |
| 20–35 | 分析原理 | Somatic calling、panel of normals、germline filtering、CNV/SV、purity/ploidy、clonality | 解釋 VAF 不等於 cancer cell fraction |
| 35–55 | 結果與 QC 示範 | IGV pileup、VCF/MAF、copy-number plot、filter flags 與 cohort summary | 評估 3 個候選事件 |
| 55–60 | 決策題 | 5% VAF 是否一定是假陽性？ | 寫下判斷條件 |

## 核心資料流

```text
clinical question
   ↓
tumor specimen ± matched normal
   ↓
FASTQ → QC → BAM/CRAM → SNV/indel + CNV + SV calling
   ↓
artifact/germline filtering → annotation → orthogonal validation
   ↓
QC-reviewed calls + annotation + analysis-ready tables
```

## 必講概念

- Tumor-only 難以可靠區分部分 germline 與 somatic events。
- FFPE deamination、低輸入量與 mapping artifacts 會造成假陽性。
- VAF 同時受到 purity、local copy number、clonality 與 sequencing sampling 影響。
- 高 depth 不會自動消除系統性 error。
- 不同 caller 的結果集合不會完全相同；caller 數量多不等於 consensus 一定正確。
- VCF/MAF、segmentation file 與 visualization 都是演算法輸出，不是原始觀察真值。

## 示範

展示三個簡化事件：

1. 高 depth、雙股支持、matched normal absent 的低 VAF hotspot。
2. 只在 read ends、方向偏差明顯的 FFPE-like artifact。
3. Copy-number amplification，但 tumor purity 很低。

要求學員對每個事件標記：

- `接受`
- `需要正交驗證`
- `技術上可疑`
- `需要更多資料才能判定`

## 不深入

- 各 caller 的 likelihood function
- AMP/ASCO/CAP clinical evidence tiering
- 特定藥物處方建議

## 決策題

**題目：** VAF 5% 的候選 somatic variant 是否應直接保留為高可信度分析結果？

**正確決策：** 不能只依 VAF 決定。

**理由：** 需同時檢查 depth、alternate read count、strand/orientation bias、mapping context、tumor purity、copy number、matched normal、caller/filter 規則及正交驗證需求。

## 講師檢查

- [ ] VAF 圖示包含 purity 與 copy number
- [ ] tumor-only 的 germline incidental finding 風險有被說明
- [ ] 清楚區分 read-level evidence、caller output 與下游 annotation
- [ ] 臨床 actionability 僅列為後續跨專業協作，不占主要授課時間
