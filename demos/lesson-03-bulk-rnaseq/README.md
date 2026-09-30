# 第三堂：可重跑的 Bulk RNA-seq 統計教學

搭配[第三堂學員完整版](../../lessons/lesson-03-materials.md)。這裡使用 3,000 個人工基因、12 個合成樣本，沒有病人資料或真實基因的生物學結論。兩個批次各包含 3 個 Control 和 3 個 Case；已知模擬條件只供理解模型，不代表真實研究建議樣本數，也不是方法效能 benchmark。

## 執行

需要事先準備好 R 與 DESeq2。程式不安裝套件、不連網、不下載定序檔。請在專案根目錄執行；最後一個參數是**尚不存在**的輸出資料夾，避免覆寫先前結果。

```sh
Rscript --vanilla demos/lesson-03-bulk-rnaseq/run-demo.R output/lesson-03-demo
```

如果該資料夾已經存在，請改用新名稱，例如 `output/lesson-03-demo-rerun`，不必刪掉原結果。沒有 R 的學員可以直接閱讀已產生的圖表與 CSV；不需要為上課先安裝完整 RNA-seq 工具鏈。

## 如何閱讀輸出

先看 `metadata.csv` 與 `counts.csv`，確認樣本順序與 condition × batch 的分布。`synthetic-truth.csv` 是生成資料的假設值，不是分析程式從資料證明的真相；真實專案不會事先知道這一張表。

`size-factors.csv` 與 `normalized-counts.csv` 用來理解量尺調整。接著看 `01-pca.png` 和 `04-sample-distance.png`：顏色、形狀或距離反映的是轉換後資料的結構，沒有將 batch 自動消除。距離圖的顏色表示樣本距離，不是基因表現；對角線為零。

`differential-expression.csv` 保留完整 DESeq2 結果，正 log2FC 代表模型中 Case 相對 Control 較高。`02-ma.png` 把平均表現與效應並列，`03-volcano.png` 把效應與 BH 調整 p 值並列。這些圖使用未經 shrinkage 的 log2FC，不應當成已穩定化的候選效應排名。圖中 cutoff 只供教學，不是臨床效能門檻。

`psi-examples.csv` 重算教材中的 PSI 算式；它沒有讀取 BAM，也沒有跑 rMATS 或作差異剪接檢定。`sessionInfo.txt` 與 `run-summary.txt` 記錄實際環境、設計與限制。固定種子有助重現合成抽樣；不同軟體版本仍可能造成細微差異。

程式內含分組可識別性、樣本欄位一致性、非負整數輸入、PSI 與 BH 算例檢查。正文附錄逐步解釋主要程式，不要求學員逐行默寫。

## 這個示範沒有驗證什麼？

沒有執行 FASTQ QC、STAR、Salmon、featureCounts、rMATS、DEXSeq 或 LeafCutter，沒有模擬真實 transcript 結構，也沒有證明某個建庫或 QC 門檻適合院內檢體。真實資料必須另做本教材第五章的樣本與 RNA 特有 QC。

原有 [AI-agent 合成資料](../ai-agent/README.md) 基因數很少，用途是稽核 metadata 與追問風險；不把它用作本堂正式差異表現示範。若要延伸到公開資料，可使用 Bioconductor 的 [airway 資料](https://bioconductor.org/packages/release/data/experiment/html/airway.html)，但應先閱讀其細胞株、配對處理與來源說明，不能把細胞株寫成臨床病人。本次沒有下載或執行 airway 分析。
