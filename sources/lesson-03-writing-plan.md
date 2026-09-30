# 第三堂完整版教材編寫架構

日期：2026-09-29。依第三堂現行課綱與使用者要求，製作可獨立閱讀的繁體中文學員教材；不列段落授課時長，不改成講師講稿。

## 階段一：章節與必要解釋

1. 臨床問題與 RNA 生物學：基因、轉錄本、外顯子／內含子、剪接、成熟 RNA、bulk 混合與相對量。
2. 研究設計：研究單位、生物／技術重複、配對、樣本數、共變數、混雜、批次與可識別性。
3. 採樣與文庫：保存、RIN／DV200、poly(A)／rRNA depletion、cDNA、strandedness、read／fragment、UMI、3′ 與全長覆蓋。
4. 檔案：FASTA、FASTQ、SAM/BAM/CRAM、GTF/GFF/BED、quant.sf、counts、metadata；版本與座標實例。
5. QC 與定量：FastQC、MultiQC、RNA 特有 QC、STAR splice-aware alignment、Salmon、多重比對、featureCounts、tximport。
6. 表現量尺度：counts、CPM、RPKM／FPKM／TPM、composition、size factor、median-of-ratios、TMM、spike-in 與假設。
7. 樣本探索：log／VST、PCA、distance、heatmap、outlier；避免用分群選擇性刪樣本。
8. 差異表現：負二項分布、dispersion、GLM、design、contrast、paired／interaction、fold change、SE／CI、shrinkage、p／FDR、filtering、NA。
9. 結果判讀：DESeq2 欄位、MA／volcano、熱圖、細胞組成、因果邊界與驗證。
10. 可變剪接：五種事件、junction、PSI／ΔPSI、DGE／DTE／DTU／DEU、rMATS／LeafCutter／DEXSeq、短讀長限制、IGV／sashimi、PCR 驗證。
11. 實務與自學：可追溯的分析交付、新增平衡設計合成 counts 的 DESeq2 示範、現有少量基因合成資料僅用於稽核、練習與完整解析。airway 未安裝，不另外下載，僅列為公開資料延伸方向。

## 階段二：寫作與驗證原則

逐節展開為完整段落，每個核心名詞說明背景、定義、機制、例子與限制。用少量表格與文字示意圖幫助比較，不以術語清單取代解說。保留本課與第四堂 pathway 分析的界線。

使用 scientific-writing 與 research-lookup 技能。後者的 API 未設定，改用原始研究與官方技術文件查核，來源另記於 lesson-03-materials-sources.md。學員教材不是期刊論文，不強套 IMRAD、圖像式摘要或投稿版面，沿用專案 Markdown 講義。

數學算例需重算；可執行程式需驗證，未能執行的部分明示限制。不安裝大型流程或下載 FASTQ，不使用院內資料，不聲稱合成資料產生臨床發現。
