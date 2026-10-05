# NGS Analysis Workbench：公開 FASTQ QC 示範

本示範使用本機現有 Nextflow 與 Docker，學習原始 FASTQ 品質檢查及報告判讀。資料預計取自公開測試資料集；目前僅完成目錄準備與環境盤點，尚未下載 FASTQ 或執行 QC。

## 目錄

- `data/`：公開 FASTQ 與來源資訊；原始 FASTQ 不納入 Git。
- `config/`：經確認的參數與樣本表。
- `runs/<run-name>/`：由 Workbench 核准執行後建立，放置流程工作目錄、日誌與結果；不納入 Git。

候選流程為目錄中的 `nf-core/demo 1.2.0`。正式執行前需完成資料大小與 SHA-256 驗證、流程來源檢視、Docker 容器架構相容性及 Workbench readiness 檢查。第一輪關閉 trimming，使用 FastQC 與 MultiQC；是否修剪依實際報告判斷。QC 示範不支持臨床判讀或完整資料集品質結論。

## 執行流程

```mermaid
flowchart TD
    A[讀取技能與專案規範] --> B[查詢運算目標與流程目錄]
    B --> C[盤點本機 Nextflow、Java 與 Docker]
    C --> D[選定本機 Nextflow 與 Docker]
    D --> E[建立 demo 目錄：目前已完成]
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
    V --> W[保存分析摘要、版本、參數與結果限制]
```

執行失敗時應檢查日誌與部分輸出，先說明阻礙；不得把流程完成狀態當成資料品質合格的證據。
