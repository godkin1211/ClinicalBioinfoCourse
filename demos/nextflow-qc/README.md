# Nextflow FASTQ QC 教學示範

完整學員操作與背景說明見[第八堂講義](../../lessons/lesson-08-materials.md)，實測狀態見[驗證紀錄](VALIDATION.md)。

這是一個刻意保持小型的 DSL2 pipeline：

```text
samplesheet.csv
      ↓
one channel item per sample
      ↓
FASTQC tasks run independently
      ↓
FASTQC zip files are collected
      ↓
MULTIQC creates one cohort report
```

它只用來教 process、channel、workflow、parallel tasks、cache、`-resume`、container 與 provenance，不是 production RNA-seq pipeline。

## 目錄

```text
.
├── main.nf
├── nextflow.config
├── data/
│   ├── samplesheet.csv
│   └── synthetic FASTQ files
└── results/              # 執行後產生
```

## 需求

- Java 17 以上相容版本（建議 Java 21 LTS）
- 本教材以 Nextflow 26.10.3 測試
- 以下任一軟體路徑：
  - Docker
  - Conda
  - 已在本機 PATH 中安裝 FastQC 與 MultiQC

## 1. 無外部工具驗證

`-stub-run` 會執行每個 process 的 `stub` block，只產生占位檔，可理解 DSL、channels、輸入與輸出契約，但不能作為分析驗收：

```bash
NXF_OFFLINE=true nextflow run . -stub-run -profile standard
```

## 2. Docker 執行

```bash
nextflow run . -profile docker
```

第一次執行需要下載 container images。上課前應完成下載。

## 3. Conda 執行

```bash
nextflow run . -profile conda
```

## 4. 本機工具

若 `fastqc` 和 `multiqc` 已在 PATH：

```bash
nextflow run . -profile standard
```

## 5. 展示 cache 與 resume

```bash
nextflow run . -profile docker -resume
```

檢查 console 中的 `cached` 狀態，再開啟：

- `results/pipeline_info/execution_trace.txt`
- `results/pipeline_info/execution_report.html`
- `results/pipeline_info/execution_timeline.html`
- `results/pipeline_info/pipeline_dag.html`

## Demo 操作

### 加一個樣本

1. 複製一列 sample sheet，指定另一組 FASTQ。
2. 使用新的 `sample_id`。
3. 執行 `-resume`。
4. 觀察哪些 tasks 被重用、哪些新增。

### 製造輸入錯誤

把一個 `fastq_1` 改成不存在的路徑。流程應在開始分析前以清楚訊息失敗。

### 檢查 task 目錄

從 console 複製 task hash，進入對應 `work/` 目錄，查看：

- `.command.sh`
- `.command.run`
- `.command.out`
- `.command.err`
- `.exitcode`

## 課堂限制

- 合成 FASTQ 太小，FastQC flags 不能代表真實 sequencing quality。
- 四個 FASTQ 各 4 reads、40 bases；每檔第一筆首個品質為 `!`（Q0），其餘為 `I`（Q40），避免全部 `I` 造成編碼歧義。
- Container tag、Nextflow 與 Java 版本應於上課前重新測試。
- `-resume` 依 cache 判斷，不代表 biological result 已驗證。
- Production 使用應考慮 schema validation、reference manifest、test profiles、CI 與 institutional execution profiles。

## 選配：Seqera AI 摘要

此 profile 會把 QC 報告資料送至 Seqera AI；只對公開／合成資料或已核准資料使用。預設 `docker` profile 不啟用 AI。token 檔須只包含單一 token，可帶結尾換行；不要 `source` 不可信任的憑證檔，也不要把 token 值貼入命令、設定、Git 或課堂畫面。

### 先登錄憑證，再決定如何取用

可先把既有 token 登錄到 Nextflow 本地 secrets store（詳見[講義第 9.5.1 節](../../lessons/lesson-08-materials.md#951-先準備憑證登錄到-nextflow-secrets)）：

```bash
set +x
seqera_token_path='/absolute/path/to/seqera-token'
test -s "$seqera_token_path" && nextflow secrets set SEQERA_ACCESS_TOKEN \
    "$(tr -d '\r\n' < "$seqera_token_path")"
nextflow secrets list
```

請換成自己的單行 token 檔路徑；同名 `set` 會更新既有 secret。名稱清單應包含 `SEQERA_ACCESS_TOKEN`，但不代表已驗證 API 權限。不要投影 `secrets get` 或列印值。此命令避免將 token 明文貼入 shell history，但值仍會短暫出現在註冊程式的命令列參數，須考慮共用主機風險。參考 [Nextflow secrets 官方文件](https://docs.seqera.io/nextflow/secrets)。

登錄只負責保存憑證，不呼叫 AI。**目前 `seqera_ai` profile 仍採下面的 token 檔案掛載方式，尚未接上 secrets store**；不能省略 `--seqera_token_file`。之後若改用 secrets，須另外調整 process 的取用方式、移除檔案掛載與相關檢查，並重新實測。此次僅補教材，不變更執行流程。

### 執行現有檔案掛載流程

若要在 workflow 結束後以 Gmail 寄送成功／失敗通知，參考[講義第 9.5.2 節](../../lessons/lesson-08-materials.md#952-延伸設定用-gmail-通知流程完成或失敗)。另提供 `conf/gmail.config` 與精簡的 `conf/workflow-status.txt`；需先登錄自己的 `GMAIL_SMTP_USER`、`GMAIL_APP_PASSWORD`，再以 `-c conf/gmail.config -N 收件地址` 明確啟用。此選配不會自動載入，也不需要將 Gmail 憑證掛載給分析容器。本次只檢查語法及模板，未以真實 Gmail 寄信。

```bash
nextflow run . -profile seqera_ai \
    --seqera_token_file /absolute/path/to/seqera-token \
    --input data/samplesheet.csv \
    --outdir results/seqera-ai
python3 verify.py results/seqera-ai --samples sampleA sampleB --ai
```

`seqera_ai` 已啟用本機 Docker，只將指定檔案唯讀掛載到 MULTIQC 的 `/run/secrets/seqera_token`，由容器內讀成 `SEQERA_ACCESS_TOKEN`。token 值不經過 Nextflow 參數或設定插值。檔案應存放於 repository 之外，且僅允許必要帳號讀取。這不是硬體秘密保護：Docker 管理者與容器內程式仍可讀取它。

AI 的 MULTIQC task 設定 `cache = false`；即使加 `-resume`，摘要仍會重新呼叫服務，可能消耗配額。FastQC 仍可重用。請不要為了測試快取而反覆送出 AI 請求。

### MultiQC 1.30 的 API 相容性

截至 2026-11-03，1.30 預設 `intern.seqera.io` 無法解析；文件中的 `ai.seqera.io` 路徑又會重新導向網頁。官方現行 MultiQC `main` 已使用 `/internal-ai/report-summary`，官方服務公開 schema 也列出同名摘要端點。因此提供限於 **MultiQC 1.30** 的 [相容入口](bin/multiqc-seqera.py)：沿用 MultiQC 的 prompt、token 驗證及 request/response 處理，只將 Seqera 請求導向 `https://ai-api.seqera.io/v1/web/internal-ai/report-summary`，不修改安裝套件，也不影響預設非 AI 流程。

這是本課的相容包裝，不是宣稱原版 1.30 原生端點仍正常；未來升級時必須重新檢查並移除不再需要的包裝。官方參考：[AI 說明](https://docs.seqera.io/multiqc/ai/)、[目前原始碼](https://github.com/MultiQC/MultiQC/blob/main/multiqc/core/ai.py)、[公開 API schema](https://ai-api.seqera.io/openapi.json)。

原版 MultiQC 在摘要失敗時可能仍退出 0；相容入口會額外確認 `ai_global_summary` 非空，缺少摘要時以失敗退出。`verify.py --ai` 則獨立確認最終 HTML 確實嵌入摘要，而不是只有按鈕。這只驗證功能，不證明摘要科學內容正確。
