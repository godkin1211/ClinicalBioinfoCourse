# NGS Analysis Workbench：公開 FASTQ QC 示範

本示範使用本機現有 Nextflow 與 Docker，學習原始 FASTQ 品質檢查及報告判讀。2026-10-05 已透過 Workbench 完成公開 SRR6357070 測試子集的 QC，沒有修剪讀序。詳見 [實際結果與限制](analysis_summary.md)。

## 目錄

- `data/`：公開 FASTQ 與來源資訊；原始 FASTQ 不納入 Git。
- `config/`：經確認的參數與樣本表。
- `runs/<run-name>/`：由 Workbench 核准執行後建立，放置流程工作目錄、日誌與結果；不納入 Git。

本次選定的最終教學報告與數值表已明確納入 Git；其餘執行暫存仍忽略。報告保留流程原生位置：[MultiQC HTML](runs/20261005-raw-qc/results/multiqc/SRR6357070-public-FASTQ-QC-demo_multiqc_report.html)、[R1 FastQC](runs/20261005-raw-qc/results/fastqc/SRR6357070/SRR6357070_1_fastqc.html)、[R2 FastQC](runs/20261005-raw-qc/results/fastqc/SRR6357070/SRR6357070_2_fastqc.html)。

已執行流程為 `nf-core/demo 1.2.0`，profile 為 `docker,emulate_amd64`。輸入的大小、SHA-256、gzip、FASTQ 結構與雙端名稱對應皆已驗證，共 50,000 對、每條 101 bp。Docker Desktop 啟動後確認有約 8 GB 記憶體，因此本次使用每工作最多 2 CPU／4 GB 的資源設定。第一輪關閉 trimming，使用 FastQC 與 MultiQC；是否修剪依實際報告判斷。QC 示範不支持臨床判讀或完整資料集品質結論。

## 執行流程

```mermaid
flowchart TD
    A[讀取技能與專案規範] --> B[查詢運算目標與流程目錄]
    B --> C[盤點本機 Nextflow、Java 與 Docker]
    C --> D[選定本機 Nextflow 與 Docker]
    D --> E[建立 demo 目錄]
    E --> F[確認流程版本、模組、設定與授權]
    F --> G[確認公開 FASTQ 來源、大小、SHA-256 與雙端關係]
    G --> H[準備參數與樣本表：關閉 trimming]
    H --> I[Workbench readiness 檢查]
    I --> J{可執行？}
    J -- 否或未知 --> K[釐清阻礙並處理]
    K --> I
    J -- 是 --> L[建立不可變執行計畫]
    L --> M[Workbench 原生執行核准]
    M --> N{核准？}
    N -- 否 --> O[停止]
    N -- 是 --> P[下載並驗證 FASTQ、建立設定檔]
    P --> Q[啟動流程並保存 run ID]
    Q --> R[FastQC：原始 R1 與 R2]
    R --> S[MultiQC：彙整報告]
    S --> T[監控至終態並檢查實際輸出]
    T --> U[判讀品質、讀長、GC、接頭與過度代表序列]
    U --> V[有明確需求才另建修剪與重新 QC 計畫]
    V --> W[保存分析摘要、版本、參數與結果限制：本次已完成]
```

執行失敗時應檢查日誌與部分輸出，先說明阻礙；不得把流程完成狀態當成資料品質合格的證據。

本次執行至原始 QC 與摘要保存，未執行另一次修剪分析。MultiQC 在 AMD64 模擬模式下停用靜態圖匯出，HTML 與數值表已成功產生。
