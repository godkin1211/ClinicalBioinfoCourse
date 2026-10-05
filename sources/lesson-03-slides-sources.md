# 第三堂投影片：來源、查核與執行界線

查核日期：2026-10-05。對應 [HTML 投影片](../output/slides/lesson-03-bulk-rnaseq.html) 與 [逐頁詳解](../output/slides/lesson-03-explanations.html)。

## 編製依據

主課程以 [第三堂完整學員講義](../lessons/lesson-03-materials.md) 為準；原始方法、官方文件與先前驗證記錄見 [講義來源](lesson-03-materials-sources.md)。本次採 scientific-slides 的結構與視覺驗證原則，依使用者要求製作可編輯文字的 HTML，而非 AI 圖像化投影片。逐頁詳解由建置程式選取講義章節，避免另寫一份逐漸失去同步的解釋；頁面末兩項補充另在建置程式中維護。

研究查詢專用服務先前查核未配置金鑰，本次未呼叫該服務；沿用講義的已查核方法來源，並使用官方網站與官方套件文件查核新增工具內容。未新增或執行 NGS 工作流程。

## 合成分析與數字

投影片第 26、27、39、40 頁直接內嵌 `output/lesson-03-demo/` 中既有的四張 PNG，未改寫數據或以生成圖替換研究圖。來源為合成 counts 的 R 4.4.2／DESeq2 1.46.0 執行：3,000 個人工基因、12 個樣本，兩批各有 3 Case、3 Control，模型 `~ batch + condition`，Case／Control 對比。

核對 `run-summary.txt` 與 `differential-expression.csv`：保留 2,984 個基因、283 個 padj<0.05；GENE0001 的 baseMean=402.022686、log2FC=1.205939、lfcSE=0.242680、Wald stat=4.969256、padj=1.319445e-05。這些數字不是病人分析、效能 benchmark 或應達到的顯著基因數。

VST／PCA 沒有移除 batch，圖上的 log2FC 未收縮。PSI 僅算術示範；沒有執行 FASTQ QC、STAR、Salmon、featureCounts、rMATS、LeafCutter 或 DEXSeq。外顯子組合圖是概念示意，非真實 IGV／sashimi 圖，也非按 genomic coordinates 繪製。

## 第 55 頁：四工具比較

| 來源 | 可支持的內容 | 教學判斷與限制 |
|---|---|---|
| [BEAVR 官方程式與 README](https://github.com/developerpiru/BEAVR)、[原始論文](https://doi.org/10.1186/s12859-020-03549-8) | Count matrix、分組資料、DESeq2、探索與視覺化；R／Docker 部署 | Browser-based 不等於免安裝的公共服務；講者需預先準備 |
| [RNAdetector 原始論文](https://doi.org/10.1186/s12859-021-04211-7)、[官方 repository](https://github.com/knowmics-lab/RNAdetector)、[下載頁](https://rnadetector.atlas.dmi.unict.it/download.html) | FASTQ／BAM／SAM、定量、DE 等；獨立軟體／後端部署 | 不把原始論文年份當作不再維護的證據，也未實測安裝 |
| [RaNA-seq 官網](https://ranaseq.eu/)、[官方手冊](https://ranaseq.eu/docs/Manual.pdf)、[原始論文](https://doi.org/10.1093/bioinformatics/btz854) | FASTQ／公開資料、QC、定量、DE 的網頁流程 | 適合示範端到端概念；上傳、排程與運算需先測，不宣稱特定容量或免等待 |
| [iDEP 網站](https://bioinformatics.sdstate.edu/idep/)、[官方程式](https://github.com/gexijin/idepGolem)、[格式文件](https://idepsite.wordpress.com/data-format/)、[原始論文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6299935/) | 表現矩陣的探索、差異表現、圖表與富集 | 依本堂 counts→PCA→DE 目標推薦；不是正確率排名或保證可支援任何設計 |

以上是文件層級查核，不是四套平台端到端實測。網頁可讀不代表分析服務正常或可供全班同時使用。課前須使用同一公開資料檢查上傳、ID、設計、對比及匯出；準備離線圖與完整結果。一般 gene counts 分析並不等於正式差異剪接分析。GENE0001 等人工 ID 不適合生物學 pathway 富集。

## 第 56 頁：OpenAI NGS Analysis Workbench

- [OpenAI 官方公開介紹：Rosalind Workbench](https://developers.openai.com/blog/rosalind-workbench)，2026-08-28：連結生物問題、工具與可追溯輸出；提供研究人員審查的計畫，介紹 FASTQ QC、bulk RNA-seq 與 single-cell 等工作情境。它是工作環境與工具協調方式，不是新的差異表現統計方法。
- 本機已安裝的 OpenAI curated `ngs-analysis-workbench` 插件 **0.2.16**：直接閱讀 `skills/ngs-analysis-workbench/SKILL.md`、`references/analysis-context.md`、`skills/run-ngs-analysis/SKILL.md`，核對理解資料／設計／執行／解讀分工、Nextflow 與 Snakemake 路徑、環境 readiness、計畫身分與 checksum、host-native approval、run 與真實輸出審查等。這些是本次版本的文件能力，不能當作所有帳號都可使用或任意工作流程皆已就緒的證明。
- 本次只介紹，沒有發出執行計畫、下載參考、配置 compute target 或啟動分析。範例 prompt 明確要求先規劃、暫不執行；若之後實作，另需使用產品的核准機制。
- 院內病人序列與 metadata 不可因去除姓名就任意上傳。AI 不替代研究設計、QC、結果審查與臨床責任。

## 更新範圍

新增第三堂 HTML／逐頁詳解、建置與檢查程式、操作說明與本來源記錄，更新 README 入口。沒有更動講義正文、既有 PDF、前兩堂投影片或合成分析數據，因此不重建這些未受影響的交付物。
