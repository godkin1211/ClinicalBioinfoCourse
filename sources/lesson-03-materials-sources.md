# 第三堂教材來源與驗證紀錄

查核日期：2026-09-29。對應[完整學員教材](../lessons/lesson-03-materials.md)。本文記錄來源與執行範圍，不是另一份講師講稿。

## 查核方式

依 scientific-writing 與 research-lookup 技能先整理章節，再展開說明。研究查詢 API 未設定，因此改用可讀取的原始論文、官方工具文件及製造商技術文件；沒有宣稱執行未設定的研究查詢服務。數值教學例子為自行設計，不取用病人資料。線上 release 文件會變动，下方日期不表示本機已安裝其最新版。

## 來源與對應內容

| 來源 | 教材用途 | 查核說明 |
|---|---|---|
| [DESeq2 vignette](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html) | 模型設計、raw counts、轉換、contrast、NA | 官方文件；本機執行版本另記，不以網頁版本冒充 |
| [Love et al., 2014](https://doi.org/10.1186/s13059-014-0550-8) | 負二項、尺度與離散程度 | Genome Biology 原始方法；出版商頁面可讀 |
| [Robinson et al., 2010](https://academic.oup.com/bioinformatics/article/26/1/139/182458) | edgeR 計數與變異背景 | 出版商全文與 [PubMed](https://pubmed.ncbi.nlm.nih.gov/19910308/)核對 DOI btp616；不沿用舊論文的功能限制 |
| [Robinson & Oshlack, 2010](https://doi.org/10.1186/gb-2010-11-3-r25) | TMM、組成偏差 | Genome Biology 原始方法 |
| [Zhu et al., 2019](https://academic.oup.com/bioinformatics/article/35/12/2084/5159452) | apeglm 與效應收縮 | 出版商全文；2018 線上發表、2019 卷期 |
| [Benjamini & Hochberg, 1995](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1995.tb02031.x) | FDR 與 BH | 出版商檢索摘要核對書目；DOI 直開失敗，不宣稱本次讀完全文；算例另以 R p.adjust 驗證 |
| [tximport](https://bioconductor.org/packages/release/bioc/vignettes/tximport/inst/doc/tximport.html) | transcript 匯入、長度與 offset | 官方文件，不把 TPM 直接當 raw counts |
| [Salmon](https://salmon.readthedocs.io/en/latest/salmon.html) | selective alignment、定量與模型輸出 | 官方文件；不將當代 Salmon 一律稱為無比對方法 |
| [STAR](https://github.com/alexdobin/STAR) | splice-aware alignment、two-pass | 官方程式與文件 |
| [featureCounts](https://subread.sourceforge.net/featureCounts.html) | feature、meta-feature、計數歸屬 | 官方文件；paired-end 計數需核對版本參數 |
| [GENCODE](https://www.gencodegenes.org/pages/data_format.html) | GTF、gene／transcript／exon | 官方格式文件 |
| [SAM 規格](https://www.htslib.org/doc/sam.html) | CIGAR、BAM／CRAM 背景 | 官方文件；RNA 的 N 不直接當 DNA deletion |
| [FastQC duplication 文件](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html) | RNA 高表現與重複序列 | 官方文件；不以 duplication 一項決定去重 |
| [FastQC per-base quality 文件](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html) | 品質箱形圖 | 官方文件核對中位數、四分位、10／90 百分位及平均線 |
| [RSeQC](https://rseqc.sourceforge.net/) | strand、gene-body coverage、junction saturation | 官方文件 |
| [Illumina mRNA prep](https://www.illumina.com/products/by-type/sequencing-kits/stranded-mrna-prep.html) | poly(A) 富集 | 製造商方法背景，不作產品推薦或通用門檻 |
| [Illumina total RNA prep](https://www.illumina.com/products/by-type/sequencing-kits/stranded-total-rna-prep.html) | rRNA depletion | 製造商方法背景 |
| [Illumina stranded mRNA](https://www.illumina.com/products/by-type/sequencing-kits/library-prep-kits/truseq-stranded-mrna.html) | strandedness | 製造商方法背景；工具設定仍需實際核對 |
| [Illumina reference guide](https://support.illumina.com/content/dam/illumina-support/documents/documentation/chemistry_documentation/illumina_prep/1000000124514_03-illumina-stranded-total-rna-prep-reference-guide.pdf) | RNA 品質、DV200 與輸入條件 | 特定產品版次技術文件；不抄成所有文庫的放行標準 |
| [rMATS-turbo](https://github.com/Xinglab/rmats-turbo) | 五類事件、JC／JCEC、輸出欄位 | 官方 repository；[歷史 guide](https://rnaseq-mats.sourceforge.io/rmats4.0.2/user_guide.htm)僅協助核對 PSI 與組別方向，不採其舊安裝指令 |
| [LeafCutter](https://davidaknowles.github.io/leafcutter/articles/Usage.html) | intron clusters 與 differential excision | 官方文件；不當作 RI 或完整 isoform 重建工具 |
| [DEXSeq](https://bioconductor.org/packages/release/bioc/vignettes/DEXSeq/inst/doc/DEXSeq.html) | exon bins 與 relative exon usage | 官方 vignette |
| [IGV RNA-seq](https://igv.org/doc/desktop/UserGuide/tracks/alignments/rna_seq/) | sashimi 與 junction 圖 | 官方文件；核對可直接開啟的頁面路徑 |
| [limma 手冊](https://bioconductor.org/packages/release/bioc/manuals/limma/man/limma.pdf) | removeBatchEffect 的視覺化用途 | 官方 PDF；取代非官方文件鏡像 |
| [airway](https://bioconductor.org/packages/release/data/experiment/html/airway.html) | 可選公開資料延伸 | 僅列來源；本機未裝，不宣稱完成該分析 |

## 已執行與未執行

已以 R 4.4.2、DESeq2 1.46.0 執行新建的 `demos/lesson-03-bulk-rnaseq/run-demo.R`，從合成 counts 開始。生成 3,000 個基因、12 個樣本，設計為 `~ batch + condition`，對比 Case／Control；保留 2,984 個基因，283 個 padj<0.05。這不是方法 benchmark 或臨床發現。

輸出包含輸入、模擬參數、完整差異表、normalized counts、VST、PCA 座標、四張圖、PSI 算例、sessionInfo 與執行摘要。程式核對樣本對齊、counts 型態與設計滿秩，並以斷言驗證 BH 及兩種有效長度的 PSI 算例；零支持的 PSI 保留 NA。最終圖表經人工視覺檢查，調整 PCA 圖例與距離圖版面。

沒有下載 FASTQ、病人資料、參考基因組，沒有安裝新套件，也沒有執行 STAR、Salmon、featureCounts、rMATS、LeafCutter、DEXSeq、apeglm 或 airway。未把這些工具的方法說明包裝成已驗證的分析產物。範例圖的 log2FC 為未收縮值；VST 沒有移除 batch。正式學術或臨床專案仍需針對資料與版本驗證。

本次只新增第三堂學員教材、示範與來源，更新第三堂入口和 README；未修改前兩堂教材或投影片。

結構檢查確認 12 章正文、12 題練習、程式碼區塊成對，並檢查六份相關 Markdown 中的 46 個本地連結／圖片目標皆存在；課程簡介為 281 字元，保留原先 300 字以內要求。對已存在輸出位置的測試已確認會停止，避免覆寫；這個預期的停止不代表分析失敗。
