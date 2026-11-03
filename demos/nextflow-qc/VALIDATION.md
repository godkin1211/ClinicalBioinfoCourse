# Nextflow QC 教學案例驗證紀錄

_2026-11-03｜人工合成資料；非臨床分析或分析性能驗證_

---

## 📋 實測環境與範圍

- macOS 27.2，arm64 主機，既有 Docker Desktop 執行環境
- Nextflow 26.10.3 build 14229；Temurin Java 23.0.2
- Docker Engine 28.0.1
- FastQC 0.12.1；MultiQC 1.30，均真正執行容器內工具，未使用 stub
- Windows／WSL、Linux 安裝、Conda、本機工具與 HPC／雲端 profile 未在本次實測
- 靜態型別、Global Cache、pipeline composition、agent 為講義概念章節，未宣稱已執行這些延伸功能

容器實際 RepoDigest：

```text
fastqc: quay.io/biocontainers/fastqc@sha256:e194048df39c3145d9b4e0a14f4da20b59d59250465b6f2a9cb698445fd45900
multiqc: quay.io/biocontainers/multiqc@sha256:705b850db50035fd8a6973cf8c8280f0c2a1869930a14f0184a087b13f6596da
```

## ✅ 已完成的測試

所有 run 均從 `demos/nextflow-qc` 啟動，使用 `-profile docker`。

| 測試 | 輸入／參數 | 實際結果 |
|---|---|---|
| 語法檢查 | `nextflow lint .` | main.nf 與 nextflow.config 無錯誤、無警告 |
| 單樣本 | `--input data/samplesheet-one.csv --outdir results/one` | 1 FastQC＋1 MultiQC 成功 |
| 雙樣本 | `--input data/samplesheet.csv --outdir results/two` | 2 FastQC＋1 MultiQC 成功；4 HTML＋4 ZIP |
| 產物內容 | `python3 verify.py results/two --samples sampleA sampleB` | PASS；FastQC ZIP 可解讀，reads／長度／編碼／第一個 cycle 品質符合預期；MultiQC 包含四個 read 檔 |
| 原樣續跑 | 雙樣本相同參數加 `-resume` | 三個 task 都為 CACHED；`verify.py ... --cached` 通過 |
| 擴充樣本 | 先 one → grow-one，再 two → grow-two 加 `-resume` | sampleA FastQC CACHED；sampleB FastQC 與 MultiQC COMPLETED；內容驗證 PASS |
| 缺檔 | `--input data/samplesheet-missing.csv --outdir results/missing` | 退出碼 1，No such file or directory；流程 FAILED，未產生有效報告 |

成功驗證訊息：

```text
PASS: 2 samples, 4 FASTQ reports, 3 successful tasks; FastQC content and MultiQC verified
```

擴充樣本的 trace 摘要（省略環境相關的 hash、PID 與耗時）：

```text
name                    status       exit
FASTQC (sampleA)        CACHED       0
FASTQC (sampleB)        COMPLETED    0
MULTIQC (all_samples)   COMPLETED    0
```

## 📊 預期數值與重現方式

[expected/fastqc_basic_stats.tsv](expected/fastqc_basic_stats.tsv) 保存課程合成輸入的精簡預期值。完整結果由講義命令產生於 `results/`，此目錄與 `work/` 按專案規則忽略，不提交臨時執行產物。工具報告中的日期、路徑、hash 與運算時間不要求逐字一致。

MultiQC 1.30 的 `multiqc_general_stats.txt` 將 `fastqc-total_sequences` 以百萬為單位匯出，本例每列 `4e-06` 代表 4 reads，不是讀到了小於一條 read。驗證程式已按此版本單位檢查。

本次另發現舊測試資料品質全為 `I`，FastQC 會將其推定為 Illumina 1.5／Phred+64，而得到 Q9。現於每檔第一筆首位加入 `!`，使編碼辨識為 `Sanger / Illumina 1.9`，符合課程的 Phred+33 設定。第一個 cycle 四筆品質為 0、40、40、40，平均 30；其餘 cycle 平均 40。

所有 FastQC 與 MultiQC HTML／ZIP 均為工具實際輸出；`verify.py` 同時檢查檔案內容、MultiQC 樣本集合及 task 狀態。講義另外做 Markdown 區塊、相對連結、Bash 語法及合成 FASTQ 結構檢查。沒有把執行 SUCCESS、FastQC flag 或這些工程測試等同臨床適用性驗證。
