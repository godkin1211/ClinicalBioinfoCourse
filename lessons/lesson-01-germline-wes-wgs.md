# Lesson 01 — 從 SNP Array 到 WES/WGS：基因體資料分析入門

完整版：[75 分鐘詳細教材與 Windows 安裝附錄](lesson-01-materials.md)（含中段 15 分鐘彈性活動；另附延伸至 90 分鐘的單元）。以下保留原始 60 分鐘精簡教案供排課使用。

## 課程簡介

本課程從生物資訊資料流出發，比較 SNP array、基因套組、WES 與 WGS 的偵測範圍、解析度及限制。課程將介紹 array intensity、genotype、BAF/LRR、PLINK 與 VCF 等資料格式，並示範 sample/variant QC、族群結構、親緣關係、ROH、CNV 及序列變異偵測，使學員理解不同平台如何從原始訊號轉換為可分析的基因體資料。

## 課程目標

完成本堂後，學員能：

1. 比較 SNP array、panel、WES 與 WGS 的資料特性、可偵測變異及適用研究問題。
2. 說明 SNP array 與定序資料從原始訊號到 genotype／variant call 的兩條分析流程。
3. 判讀常用 sample-level、variant-level 與 intensity／sequencing QC，辨認不適合直接進入下游分析的資料。

## 研究情境

研究團隊收集一組心血管疾病 case–control cohort，規劃分析常見 SNP、族群結構、親緣關係、ROH、CNV 及 rare variants。

- 決策：哪些問題適合 SNP array，哪些需要 WES 或 WGS？
- 必要資訊：樣本數、研究設計、預期變異類型、解析度、成本、參考族群與運算需求。
- 不回答：個別受試者的致病性分類、遺傳諮詢或臨床檢測報告簽發。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–8 | 分析問題 | 從研究問題選資料平台；common/rare variant、SNV/CNV/ROH | 為 4 種問題選平台 |
| 8–18 | 技術比較 | SNP array probe/intensity 與 short-read sequencing；解析度、coverage、ascertainment bias | 完成 array/WES/WGS 比較表 |
| 18–32 | SNP array 資料流 | IDAT/CEL → normalization → genotype calling → PLINK；BAF/LRR、call rate、HWE、MAF | 排列 array pipeline |
| 32–44 | WES/WGS 資料流 | FASTQ → alignment → BAM/CRAM → variant calling → VCF；depth、mapping quality、allele balance | 排列 sequencing pipeline |
| 44–55 | 實際示範 | PCA、heterozygosity、relatedness、sex check、ROH/CNV plot 與 VCF record | 找出異常樣本與錯誤推論 |
| 55–60 | 決策題 | 只有 genotype hard calls，能否完整重做 array CNV QC？ | 個人作答後討論 |

## 核心資料流

```text
research question + cohort design
        ↓
        ├─ SNP array
        │    IDAT/CEL → normalization → genotype calling
        │    → genotype/intensity QC → PLINK + BAF/LRR
        │    → PCA / relatedness / ROH / CNV / association
        │
        └─ panel / WES / WGS
             FASTQ → read QC → alignment → BAM/CRAM
             → variant calling/filtering → VCF
             → annotation / cohort-level analysis
```

## 必講概念

- SNP array 測量預先設計 probes 的 allele-specific intensity，不是逐鹼基定序。
- Genotype hard calls 適合部分下游分析；BAF、LRR 等 intensity 資訊對 array QC 與 CNV 分析很重要。
- Array 常見 QC 包含 sample/variant call rate、heterozygosity、reported-sex check、duplicates/relatedness、ancestry PCA、HWE 與 MAF。
- SNP array 容易受 probe design 與族群代表性造成的 ascertainment bias 影響。
- WES 的 target capture 造成 coverage 不均，不能用平均 depth 取代逐區域檢查。
- WGS 的範圍較廣，但不同 SNV、indel、CNV、SV、repeat 與低複雜度區域仍需要不同演算法及 QC。
- Reference build、strand、allele coding 與 sample ID 不一致，是資料合併時常見且高風險的錯誤。
- PCA 上的群聚表示資料結構，不應自動被解讀成離散「種族」分類。

## 示範

### SNP array

使用簡化 PLINK 與 intensity 輸出，展示：

- `BED/BIM/FAM` 的樣本與 variant 結構
- Sample 與 variant missingness
- Heterozygosity outlier
- Kinship/IBD 與 duplicate sample
- PCA population structure
- BAF/LRR 中的 deletion、duplication 與長段 ROH

### WES/WGS

使用簡化 VCF，展示：

- `CHROM/POS/REF/ALT/FILTER`
- `GT:AD:DP:GQ`
- Low depth、allele imbalance 與 mapping-related flags
- 同一 cohort 進行 joint calling 前後的資料結構

學員回答：

1. 這個訊號是直接測量、演算法推估，還是下游註解？
2. 問題位於 sample level、variant level 或 genomic region level？
3. 在修正問題前，哪些下游分析不應進行？

## 不深入

- 個別疾病的致病性分類與 VUS 溝通
- ACMG/AMP clinical classification rules
- GWAS association model 與 imputation 的完整推導
- 各 CNV/SV caller 的內部演算法細節

## 決策題

**題目：** 研究團隊只保存 SNP genotype hard calls，沒有原始 intensity 或 BAF/LRR，是否能完整重新檢查並執行 array-based CNV 分析？

**正確決策：** 通常不能完整重做。

**理由：** Hard calls 已經是離散化後的結果；array CNV 與部分平台 QC 需要探針強度、BAF/LRR、cluster 或原始訊號資訊。應先確認原始檔與 calling 軟體版本是否仍可取得。

## 講師檢查

- [ ] SNP array 與 WES/WGS 各有一條完整資料流
- [ ] 明確區分 raw intensity、genotype、alignment 與 variant call
- [ ] 示範同時包含 sample-level 與 variant-level QC
- [ ] 不把 PCA cluster 直接命名為種族
- [ ] 臨床分類與遺傳諮詢只列為下游協作邊界，不占主要授課時間
