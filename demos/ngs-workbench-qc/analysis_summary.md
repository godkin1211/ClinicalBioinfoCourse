Takeaway: SRR6357070 公開 FASTQ 子集 QC 已完成，雙端品質通過，但有序列組成偏差與高重複訊號，需結合建庫資訊判讀。

這次以公開測試子集體驗讀序品質檢查，目標是理解報告並評估是否有修剪的依據。本機流程已完成雙端讀序的 FastQC 與 MultiQC，沒有修剪或去重。實際驗證共有五萬對讀序，每條長度為 101 bp，兩端每位置品質均通過，GC 含量皆為 40%。兩端都有序列組成與重複程度警示，且部分序列過度代表，不能只憑這些旗標判定污染或刪除讀序。這些結果適合教學判讀，尚不足以支持完整研究品質合格、比對表現或臨床結論。下一步應先閱讀品質曲線與接頭曲線，再核對建庫方式及過度代表序列來源，才決定是否另做修剪比較。

## 科學背景與問題

使用 nf-core 公開測試資料中的 SRR6357070 雙端子集，展示原始輸入 QC。這不是合成資料，但也不是完整研究資料；此次未查證物種、組織、建庫策略、既有前處理及子集抽樣方式，不能從檔名推定。沒有進行比對、定量或變異分析。

## 執行狀態與端點

- Workbench registry run ID：`0a28f0b1-9881-4d04-a33c-72e34dd9b2c2`。
- 狀態：`completed`，退出碼 0；FastQC、MultiQC 與流程內建 COWPY 均完成。COWPY 只產生示範文字，沒有科學分析功能。
- 本機執行目錄：`/Users/godkin/Projects/KCGMH_Cource_Series/demos/ngs-workbench-qc/runs/20261005-raw-qc`。
- 工作流程：nf-core/demo 1.2.0，實際 revision `32893afef8076a03a2767a020b3f0cab2e0b40b2`。
- Nextflow 26.04.4、FastQC 0.12.1、MultiQC 1.34（由實際程序日誌確認）。
- profile：`docker,emulate_amd64`；Linux ARM64 Docker daemon 上執行 AMD64 容器。每工作資源上限 2 CPU／4 GB。
- `skip_trim=true`、`igenomes_ignore=true`；未下載參考基因組。

## 主要發現

| 指標 | R1 | R2 |
|---|---:|---:|
| 讀序數 | 50,000 | 50,000 |
| 讀長 | 101 bp | 101 bp |
| GC | 40% | 40% |
| 每位置品質 | PASS | PASS |
| 每位置序列組成 | FAIL | FAIL |
| GC 分布 | WARN | PASS |
| 序列重複 | FAIL | FAIL |
| FastQC 估計重複比例 | 68.414% | 66.822% |
| 過度代表序列 | WARN | WARN |
| 接頭內容 | PASS | PASS |

完整 FASTQ 解析確認 gzip 可完整讀取、四行結構與序列／品質長度一致，50,000 對的讀序名稱逐筆對應。品質曲線末端 100–101 bp 的平均 Phred 分數為 R1 33.91、R2 33.85；這是位置區間平均，不是每條讀序皆達此品質。Illumina Universal Adapter 曲線在位置 90 達 R1 4.10%、R2 4.09%，因此接頭 PASS 不代表完全沒有接頭訊號。R2 的過度代表表包含 131 次全 N 的 50-base 片段（0.262%）；FastQC 表中的片段不能直接視為整條 101 bp 皆為 N。

數值來源為原生 FastQC ZIP 內的 `fastqc_data.txt`、`summary.txt`，以及 `results/multiqc/SRR6357070-public-FASTQ-QC-demo_multiqc_report_data/multiqc_fastqc.txt`。MultiQC general stats 的讀序數以百萬為單位顯示 0.05；不能誤讀為 0.05 條。兩個 FAIL 占十個 FastQC 模組的 20%，不是 20% 讀序失敗。

## 判讀

基礎品質檢查沒有顯示需要立即品質修剪的充分理由。序列組成偏差、高重複與過度代表序列需要建庫資訊及序列來源分類才能解釋；例如部分文庫本來就會具有非隨機序列組成或高重複。FastQC 重複估計屬序列層級指標，不能直接當成 PCR duplicates、唯一分子比例或去重後可保留讀序數。先保留原始讀序，確認接頭與建庫策略後，才有依據規劃修剪或其他前處理。

## 產物與來源

- 結果數值：上述 `multiqc_fastqc.txt` 與同目錄 `multiqc_general_stats.txt`。
- QC 報告：`results/fastqc/SRR6357070/SRR6357070_1_fastqc.html`、`SRR6357070_2_fastqc.html`，以及 `results/multiqc/SRR6357070-public-FASTQ-QC-demo_multiqc_report.html`。
- FastQC ZIP：位於 `work/77/692470ff9d5b29a2f4dd3d0270d496/SRR6357070_1_fastqc.zip` 與 `SRR6357070_2_fastqc.zip`；上游流程只將 HTML 發布到 results，ZIP 留在本機工作目錄，未搬移或重建。
- 參數與樣本表：`config/20261005-raw-qc/`；版本資訊：`results/pipeline_info/nf_core_demo_software_mqc_versions.yml`。
- 原始資料來源固定於 [nf-core/test-datasets commit 626c8fab](https://github.com/nf-core/test-datasets/tree/626c8fab639062eade4b10747e919341cbf9b41a/testdata/GSE110004)。本機資料位於 `data/`，不納入 Git。
- R1：2,239,317 bytes，SHA-256 `3f50541fa9cf2bedc87e7b682ada0fccfdfcd6d27b9bb81f17be230ff140ebe7`。
- R2：2,232,117 bytes，SHA-256 `8590e1e01e568fba256aa7dced40519604cbb111ee44ab106a3dcb869660aaf4`。
- 執行計畫：`ngs-plan-2a0761e75c2699fc`；checksum `sha256:2a0761e75c2699fc8c3b36e857de558a8871248b0f03f5c010c24eda1f6dd681`。
- 本文件為檢查實際輸出後撰寫的分析摘要，與引擎退出狀態分開。

## 限制與下一步

MultiQC 的 AMD64 模擬模式偵測到 Rosetta，停用 Kaleido 靜態 PNG／PDF／SVG 匯出；HTML 與數值表已完成，不宣稱有靜態圖檔。Host PATH Nextflow 沒有套件鎖定，流程版本固定不等於所有執行相依項都以 digest 鎖定。未查證完整 assay metadata，也未檢查 tile 訊號或進行污染比對；目前不能確認警示的生物學或技術來源。先在 MultiQC 比較 R1／R2 的品質、接頭、重複與 GC 曲線，再補建庫資訊；任何後續修剪分析需另建 Workbench 執行計畫。
