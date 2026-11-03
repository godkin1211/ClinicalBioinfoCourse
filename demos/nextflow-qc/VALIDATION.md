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

## 🔐 2026-11-03：選配 Seqera AI 設定實測

在使用者明確指定本機 token 後，新增 `seqera_ai` profile；預設不啟用。token 檔在 repository 外，僅唯讀掛載給 MULTIQC，由容器內讀取，未將值插入參數或設定。測試送出的僅為本課兩個合成樣本的 QC 資料。

實測發現原版 1.30 的 `intern.seqera.io` 無法解析；官方文件當時列出的 `ai.seqera.io/v1/web` 會重新導向 HTML。確認官方最新原始碼已改用 `report-summary` 路由，且官方 `ai-api.seqera.io/openapi.json` 提供相符的 request schema 後，加入限於 1.30 的相容入口，將 Seqera 請求送到該官方新路由。原套件與 container image 未更動。此相容包裝需隨版本與 API 更新重新驗證，不代表原版端點正常。

成功輸出保留在本機忽略目錄 `results/seqera-ai-20261103/`。已確認：

- 真正取得 Seqera AI 回覆，`global_ai_summary_response` 含非空摘要文字
- `python3 verify.py results/seqera-ai-20261103 --samples sampleA sampleB --ai` 通過
- 相容入口遇到空摘要會非零退出；驗證程式也不接受只有 AI 按鈕的空報告
- Nextflow lint 無錯誤；新增 Python 程式通過語法檢查
- 來源、task 腳本與結果共 349 個檔案的內容檢查，未發現 token 值；沒有列印或提交 token
- 原始非 AI Docker 路線另執行回歸測試，仍由原版 `multiqc` 生成報告

`seqera_ai` 將 MULTIQC 設為不快取，因此 `-resume` 可重用 FastQC，但再次生成摘要會呼叫服務。AI 結果是輔助文字，不作為臨床品質認證；本次只確認功能及資料對應，不宣稱模型解讀正確。

## 📧 2026-11-03：Gmail 通知教材的檢查範圍

另提供 `conf/gmail.config` 與 `conf/workflow-status.txt`，須先自行設定 Gmail secrets，並以 `-c conf/gmail.config -N 收件地址` 明確啟用；預設流程不載入此設定，也未修改既有分析步驟。

- Nextflow 26.10.3：`nextflow lint demos/nextflow-qc/conf/gmail.config` 無錯誤
- 使用同版 Nextflow 內附的 Groovy `GStringTemplateEngine`，以人工 workflow metadata 渲染 SUCCESS／FAILED 兩種情境，文字均符合預期
- 講義 Bash 區塊通過 `bash -n`，Markdown code fences 配對與本機連結目標檢查通過
- 未建立或讀取 Gmail 帳號密碼、未連線 Gmail SMTP、未寄信，也未驗證收件匣送達

因此本節不宣稱 Gmail 端到端實測成功；學員須在核准環境完成教材列出的成功與缺檔失敗通知測試。通知只表示執行狀態，且郵件傳送失敗不一定改變分析退出碼。
