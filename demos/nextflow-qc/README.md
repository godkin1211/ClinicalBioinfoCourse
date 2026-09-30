# Nextflow FASTQ QC 教學示範

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

- Java 17 或相容版本
- Nextflow
- 以下任一軟體路徑：
  - Docker
  - Conda
  - 已在本機 PATH 中安裝 FastQC 與 MultiQC

## 1. 無外部工具驗證

`-stub-run` 會執行每個 process 的 `stub` block，適合先檢查 DSL、channels、輸入與輸出契約：

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
- Container tag、Nextflow 與 Java 版本應於上課前重新測試。
- `-resume` 依 cache 判斷，不代表 biological result 已驗證。
- Production 使用應考慮 schema validation、reference manifest、test profiles、CI 與 institutional execution profiles。
