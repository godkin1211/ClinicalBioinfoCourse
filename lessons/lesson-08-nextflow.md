# Lesson 08 — Nextflow：可重現生物資訊流程基礎

## 課程目標

完成本堂後，學員能：

1. 用資料流解釋 `process`、`channel` 與 `workflow`。
2. 說明 cache、`-resume`、container 與 execution report 如何支援可重現性。
3. 執行並檢查一個 FastQC → MultiQC DSL2 pipeline。

## 臨床／研究案例

研究團隊收到 24 個 RNA-seq FASTQ。分析人員曾用 notebook 加多個 shell commands 跑完，但：

- 只有部分樣本成功。
- 不確定使用的 FastQC/MultiQC 版本。
- 修改 sample sheet 後全部重跑。
- 無法說明每個輸出對應哪個輸入與參數。

本堂決策：如何把分析步驟變成可重跑、可擴充、可稽核的 workflow？

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 現場操作 |
|---:|---|---|---|
| 0–8 | 問題 | Script、notebook 與 workflow manager 的差異 | 找出既有流程缺少的 provenance |
| 8–15 | 核心概念 | Task、process、channel、workflow、executor | 用人流／檢體流比喻畫圖 |
| 15–25 | 輸入 | `samplesheet.csv`、`Channel.fromPath`、tuple、file staging | 開啟 sample sheet 與 `main.nf` |
| 25–37 | Process | FASTQC/MULTIQC input、output、script、container、publishDir | 第一次執行 pipeline |
| 37–44 | 平行與 cache | 每個 sample 形成 task；work directory；hash；`-resume` | 修改 `params.outdir` 或 sample sheet 後續跑 |
| 44–50 | 執行環境 | Local、Docker、Conda、HPC/cloud profile | 對照 `nextflow.config` |
| 50–56 | 稽核輸出 | Trace、report、timeline、DAG、`.nextflow.log` | 開啟執行產物 |
| 56–60 | 決策題 | 改 reference／container 後是否可盲目 `-resume`？ | 說明 cache 邊界 |

## 必講概念

- `process` 描述可獨立執行的分析步驟及輸入／輸出契約。
- `channel` 傳遞 values/files；它不是共享資料夾。
- `workflow` 明確呼叫與連接 processes。
- 同一 process 對多筆 channel item 可產生平行 tasks；完成順序不保證等於輸入順序。
- `work/` 保存 task staging、command、log 與 outputs；`results/` 是發佈給使用者的產物。
- `-resume` 根據 task hash/cache 決定是否重用；輸入、script、設定或環境改變可能使 cache 失效。
- Container 固定 user-space tool environment，但不自動固定 reference data、parameters、Nextflow version 或 host kernel。
- Workflow 成功結束不代表資料品質良好；仍需檢查 MultiQC 與 domain-specific QC。

## Live demo

使用 [demos/nextflow-qc](../demos/nextflow-qc)：

```bash
cd demos/nextflow-qc

# 不依賴 FastQC/MultiQC 的流程驗證
NXF_OFFLINE=true nextflow run . -stub-run -profile standard

# 正式容器化示範
nextflow run . -profile docker

# 查看 cache reuse
nextflow run . -profile docker -resume
```

依序打開：

1. `data/samplesheet.csv`
2. `main.nf`
3. `nextflow.config`
4. `results/fastqc/`
5. `results/multiqc/multiqc_report.html`
6. `results/pipeline_info/execution_trace.txt`
7. `results/pipeline_info/execution_report.html`
8. `results/pipeline_info/pipeline_dag.html`

## Demo 中故意做的變更

1. 原始執行。
2. 使用 `-resume` 原樣重跑，觀察 cached tasks。
3. 在 sample sheet 新增一個 sample，再用 `-resume`，預期只增加必要 tasks。
4. 變更 process script 或 container tag，再說明為何 tasks 應重跑。
5. 示範一筆不存在的 FASTQ path 如何在分析前失敗。

不要在正式課堂中刪除 `work/` 後再試圖展示 `-resume`；cache metadata 與工作產物都需要保留。

## nf-core 簡介

只說明三件事：

- nf-core 提供經社群維護的 Nextflow pipelines、modules 與使用規範。
- 使用成熟 pipeline 仍需理解 sample sheet、parameters、reference、software release 與 MultiQC。
- 不因 pipeline 名稱知名就省略適用性與輸出驗證。

## 決策題

**題目：** 只修改 reference genome path 後執行 `-resume`，看到很多 cached tasks，是否可直接接受結果？

**正確決策：** 不可只看 `CACHED`。

**理由：** 必須確認 reference 是否確實列入 process inputs/config hashing、哪些 tasks 理應失效，以及 outputs 是否對應新 reference。

## 備援方案

- Docker 不可用：跑 `-stub-run` 並展示預先產生的 MultiQC HTML 截圖。
- 網路不可用：提前 pull images，或使用本機 FastQC/MultiQC profile。
- Nextflow 不可用：使用 DAG、`main.nf` 與 execution report 靜態材料完成資料流講解。

## 講師檢查

- [ ] 上課前完成 docker pull 與完整 run
- [ ] 保留一次 successful run 的 `results/` 備援
- [ ] 確認 Java 與 Nextflow 版本
- [ ] 不在投影片貼完整 DSL；只顯示一個 process 與 workflow block
- [ ] 示範 `.command.sh`、`.command.err` 與 `.exitcode` 至少一次

## 官方文件

- [Nextflow installation](https://www.nextflow.io/docs/latest/getstarted.html)
- [Workflows](https://www.nextflow.io/docs/latest/workflow.html)
- [Processes](https://www.nextflow.io/docs/latest/process.html)
- [Containers](https://www.nextflow.io/docs/latest/container.html)
- [nf-core](https://nf-co.re/)
