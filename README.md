# 高雄長庚臨床生物資訊系列課程

主要版本庫：[godkin1211/ClinicalBioinfoCourse](https://github.com/godkin1211/ClinicalBioinfoCourse)。後續專案修改完成並檢查後，均 commit 並 push 至此 repository；協作規則見 [AGENTS.md](AGENTS.md)。

這個專案提供 2026 年 9–12 月、共 9 堂、每堂 60 分鐘的臨床生物資訊系列課程教學材料。課程以臨床案例為入口，把研究設計、檔案格式、品質控制與統計觀念嵌入各種 omics 分析，不另外安排抽象的基礎課。

## 課程地圖

| 月份 | 堂次 | 主題 | 教案 |
|---|---:|---|---|
| 9 月 | 1 | 從 SNP Array 到 WES/WGS：基因體資料分析入門 | [lesson-01](lessons/lesson-01-germline-wes-wgs.md) |
| 9 月 | 2 | 癌症體細胞基因體分析 | [lesson-02](lessons/lesson-02-somatic-cancer-genomics.md) |
| 10 月 | 3 | Bulk RNA-seq：從檢體到差異表現 | [lesson-03](lessons/lesson-03-bulk-rnaseq.md) |
| 10 月 | 4 | Pathway、網路與公開資料分析 | [lesson-04](lessons/lesson-04-pathway-network-public-data.md) |
| 11 月 | 5 | Single-cell RNA-seq：技術與前處理 | [lesson-05](lessons/lesson-05-scrna-preprocessing.md) |
| 11 月 | 6 | Single-cell RNA-seq：比較與臨床推論 | [lesson-06](lessons/lesson-06-scrna-clinical-inference.md) |
| 12 月 | 7 | 空間轉錄體分析 | [lesson-07](lessons/lesson-07-spatial-transcriptomics.md) |
| 12 月 | 8 | Nextflow：可重現生物資訊流程基礎 | [lesson-08](lessons/lesson-08-nextflow.md) |
| 12 月 | 9 | 使用 AI Agent 輔助生物資訊分析 | [lesson-09](lessons/lesson-09-ai-agent.md) |

完整的課程定位、共同教學原則與課程間銜接方式見 [課程總綱](curriculum/program-overview.md)。

## 可直接使用的示範

### 第一堂：基因體資料分析

- [學員詳細教材](lessons/lesson-01-materials.md)：名詞解釋、判讀與延伸練習；附錄 A 完整涵蓋 Windows／WSL2、macOS、Linux 的安裝、下載專案、執行腳本、預期結果與排錯。
- [第一堂 PDF 講義](output/pdf/lesson-01-materials.pdf)：包含完整跨系統實作附錄，可獨立閱讀。
- [合成資料與操作腳本](demos/lesson-01-genomics/README.md)：PLINK QC、PCA、親緣與 ROH；SAM → BAM → VCF；BAF/LRR 與 VCF 判讀案例。
- [HTML 投影片](output/slides/lesson-01-genomics.html)：54 張、16:9、可離線播放，含 SNP array 偵測示意圖、Array／NGS 常見檔案格式、BAF／LRR 指標解說、Panel／WES／WGS 比較與選擇、判讀練習及 Windows 安裝附錄；[操作說明](output/slides/README.md)。

第一、二堂完整版為原 60 分鐘安排的延伸選項，其餘堂次時數不變。

### 第二堂：癌症體細胞基因體分析

- [HTML 投影片](output/slides/lesson-02-somatic.html)：64 張（主課程 46＋選讀附錄與資源 18）、16:9、可離線播放。從檢測目的與效益，依序進入實務設計、採樣／製備、下機 QC（含第 18 頁 FastQC 判讀）、生物資訊流程與結果解讀；第 40–42 頁分別介紹 TMB、MSI、HRD。[操作與內容導覽](output/slides/lesson-02-README.md)。
- [逐頁詳解閱讀版](output/slides/lesson-02-explanations.html)：64 頁對應的完整概念、例子與判讀說明；投影片亦可按 `E` 開啟目前頁詳解，並直接顯示具體算例或推理提示。

- [學員教材](lessons/lesson-02-materials.md)：涵蓋 tumor–normal／tumor-only、somatic calling、FFPE 與讀段 QC、VAF／純度／CN、SV、IGV 與 cohort 摘要；附錄 A 提供三種系統的安裝、腳本執行、驗證及 IGV 載入步驟，不列段落授課時長。
- [第二堂 PDF 講義](output/pdf/lesson-02-materials.pdf)：包含完整跨系統實作附錄，可獨立閱讀。
- [合成資料與操作腳本](demos/lesson-02-somatic/README.md)：比較兩個同為 5% VAF 的不同證據模式，搭配 normal、CN 混合模型與讀段抽樣練習；工具安裝見教材附錄。

### 第三堂：Bulk RNA-seq 與可變剪接

- [PDF 學員講義](output/pdf/lesson-03-materials.pdf)：26 頁，含圖表、程式碼、練習詳解與參考來源。以 `bash scripts/build-handouts.sh 03` 重新編譯，不重建前兩堂 PDF。
- [HTML 投影片](output/slides/lesson-03-bulk-rnaseq.html)：56 頁、16:9、離線播放；涵蓋研究設計、檢體／文庫、QC、定量、差異表現與可變剪接。最後兩頁為四套 RNA-seq 工具比較與 OpenAI NGS Analysis Workbench。[操作與頁次導覽](output/slides/lesson-03-README.md)。
- [逐頁詳解閱讀版](output/slides/lesson-03-explanations.html)：依完整講義對應每頁概念、算例與限制；投影片按 `E` 可直接展開。
- [完整學員教材](lessons/lesson-03-materials.md)：12 章正文，從 RNA 背景、研究設計、檢體與文庫，逐步說明資料格式、QC、定量、正規化、差異表現及可變剪接；附程式／圖表導讀、12 題練習詳解與來源，不列段落授課時長。
- [合成資料示範與有註解的 R 程式](demos/lesson-03-bulk-rnaseq/README.md)：3,000 個人工基因、12 個合成樣本；DESeq2、PCA、MA／volcano、樣本距離與 PSI 算例。[已執行輸出](output/lesson-03-demo)附實際版本及執行範圍；不含 FASTQ 比對或正式剪接檢定。
- [課程簡介與閱讀路線](lessons/lesson-03-bulk-rnaseq.md)、[教材來源與查核紀錄](sources/lesson-03-materials-sources.md)。

### Nextflow FASTQ QC

[demos/nextflow-qc](demos/nextflow-qc) 包含：

- DSL2 `process`、`channel` 與 `workflow`
- 合成 FASTQ 與 sample sheet
- FastQC → MultiQC 流程
- Docker、Conda 與本機執行 profile
- `-stub-run` 無工具驗證方式
- execution report、timeline、trace 與 DAG 設定

### AI Agent RNA-seq 稽核

[demos/ai-agent](demos/ai-agent) 包含：

- 含批次混雜與一筆潛在標籤異常的教學資料
- plan-only、核准後執行及結果稽核提示詞
- 人工審核清單與講師版預期發現
- 不需第三方套件的 deterministic preflight
- 可重用的 [`audit-rnaseq-analysis` Skill](demos/ai-agent/skills/audit-rnaseq-analysis/SKILL.md)

## 共用材料

- [課前／課後測驗與逐堂檢核](assessment/learning-assessment.md)
- [一頁式生物資訊分析需求書](templates/analysis-request-template.md)
- [60 分鐘教案模板](templates/lesson-template.md)
- [核心參考資料](references/core-reading.md)

## 快速驗證

在專案根目錄執行：

```bash
python3 demos/ai-agent/reference_checks.py \
  --counts demos/ai-agent/data/counts.csv \
  --metadata demos/ai-agent/data/metadata.csv
```

若已安裝 Nextflow，可用 stub mode 驗證 DSL2 與資料流，不需要安裝 FastQC 或 MultiQC：

```bash
cd demos/nextflow-qc
NXF_OFFLINE=true nextflow run . -stub-run -profile standard
```

正式示範可使用 Docker：

```bash
nextflow run . -profile docker
nextflow run . -profile docker -resume
```

## 教學安全邊界

- 所有課堂操作只使用公開或合成資料。
- 不把院內病人資料上傳至未核准的外部服務。
- 所有 AI 產生的程式、引用、數值、圖表與生物學結論都必須由人員驗證。
- 課程訓練的是研究分析與溝通能力，不取代臨床檢驗認證、遺傳諮詢或醫療決策。
