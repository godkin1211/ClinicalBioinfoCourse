# 2026-10-24 LDTs 生物資訊：來源與查核紀錄

查核日：2026-10-15。對應 [投影片](../output/slides/ldt-20261024-bioinformatics.html) 與 [逐頁詳解](../output/slides/ldt-20261024-explanations.html)。

## 範圍與證據界線

本課整合原系列前三堂，新增 LDT 預期用途、分析驗證、偵測極限、變更管理及資料追溯。臺灣制度以主管機關及醫策會資訊為準；國際學會文件用於解釋技術原則，不視為臺灣法定條文。授課或申請前應再確認公告與機構適用版本。此簡報不證明課程學分、訓練時數或檢測項目已獲認可。

本次僅製作教材與圖表，未執行病人資料分析、variant caller、正式性能驗證或 LoD 試驗。各圖的人工數字、深度、比例和門檻均為教學例子，不是實驗室實測性能或通用放行標準。

## 臺灣官方資訊

| 來源 | 本課用途與查核結果 |
|---|---|
| [醫策會 LDTs 入口](https://www.jct.org.tw/np-1303-1.html)、[簡介](https://www.jct.org.tw/np-1304-1.html) | LDT 定義及制度背景；入口與簡介已讀取。簡介頁標示 2024-12-17，不用它代替最新公告。 |
| [衛福部 LDTs 公告列表](https://dep.mohw.gov.tw/DOMA/lp-5177-106.html) | 確認現行公告入口及更新項目。 |
| [醫療機構申請施行 LDTs 檢測項目](https://dep.mohw.gov.tw/DOMA/cp-5177-65615-106.html) | 2026-03-13 更新；醫療機構須擬定施行計畫並經核准。已讀公告正文及附件可檢索部分；本課不逐條解讀全部附件。 |
| [實驗室認證資格公告](https://dep.mohw.gov.tw/DOMA/cp-5177-65471-106.html) | 2026-03-19；取代舊公告。用於區分實驗室資格、施行計畫與特定方法驗證，不為特定單位判定資格。 |
| [人員訓練須知](https://dep.mohw.gov.tw/DOMA/cp-5177-77135-106.html) | 2024-01-05 公告資訊；本課不承諾訓練時數採認。 |
| [儀器及資通系統使用切結書](https://dep.mohw.gov.tw/DOMA/cp-5177-82803-106.html) | 頁面 2025-07-10 更新；提醒檢測設備與資通系統需受控，不將其擴張為本課自訂的法規條文。 |

公告的內容更新日與網站頁首的全站更新日不同；以上採公告本身的日期。

## 技術原則與原始文件

| 來源 | 對應概念 |
|---|---|
| Roy S, et al. *Standards and Guidelines for Validating Next-Generation Sequencing Bioinformatics Pipelines.* J Mol Diagn. 2018;20:4–27. [PubMed](https://pubmed.ncbi.nlm.nih.gov/29154853/)，[DOI](https://doi.org/10.1016/j.jmoldx.2017.11.003) | 生物資訊流程的設計、驗證、執行及版本管理。查核摘要與 [AMP 官方驗證資源](https://www.amp.org/resources/validation-resources/)；未聲稱完整閱讀付費全文。 |
| Jennings LJ, et al. *Guidelines for Validation of Next-Generation Sequencing–Based Oncology Panels.* J Mol Diagn. 2017;19:341–365. [全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941185/)，[DOI](https://doi.org/10.1016/j.jmoldx.2017.01.011) | 預期用途、代表性檢體、事件範圍、分析性能與驗證設計；不從本文擷取一個數字作為通用門檻。 |
| [NIST Genome in a Bottle FAQ](https://www.nist.gov/programs-projects/faqs-genome-bottle) | 參考樣本、benchmark VCF 與區域；不能把區域外視為確定陰性，或把一類 benchmark 外推到全部事件。 |
| [FastQC：Per base sequence quality](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html) | 橫軸為 read 位置；中位數、四分位、10–90 百分位與平均數的圖例。課中圖為原創示意，不是實際 FastQC 結果。 |
| [GATK：Mutect2 somatic workflow](https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2) | 候選生成、過濾、方向性與污染等不同環節；實際參數需依軟體版本及檢測設計。 |
| [SAM／BAM 文件](https://www.htslib.org/doc/sam.html) | 比對欄位及讀段證據；VCF 各欄位仍應依實際 header 與 caller 文件。 |
| [fgbio：CallDuplexConsensusReads](https://fulcrumgenomics.github.io/fgbio/tools/latest/CallDuplexConsensusReads.html) | 分子共識概念；UMI 不會自動消除所有錯誤或增加原始分子數。 |
| [IGV RNA-seq 文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/rna_seq/) | Splice junction、sashimi plot 及局部讀段判讀。 |
| [DESeq2 vignette](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html) | 計數模型、設計與混雜；研究差異表現不等於已驗證的單一病人分類器。 |

## 原課程對應與延伸

- [Lesson 01 教材](../lessons/lesson-01-materials.md)：平台選擇、檔案、基因型、BAF／LRR／ROH、QC 與參考版本。
- [Lesson 02 教材](../lessons/lesson-02-materials.md)、[投影片來源](lesson-02-slides-sources.md)：FFPE、tumor–normal、分子數、VAF、讀段偏差、CNV／SV，以及備查頁的 TMB／MSI／HRD。複合 biomarker 沿用該課的原始參考與限制，本課不新增治療建議。
- [Lesson 03 教材](../lessons/lesson-03-materials.md)、[投影片來源](lesson-03-slides-sources.md)：RNA 文庫、QC、定量、設計與可變剪接。

## 圖像出處與計算前提

`figures/ldt-20261024/` 的八張 SVG 由 `scripts/build-ldt-slides.py` 產生，均為原創教學示意。SVG 本體保留標題，HTML 另有替代文字；圖像嵌入 HTML，不需連網載入。

| 圖 | 重要前提 |
|---|---|
| quality.svg | 人工品質分布，非真實 FastQC；Q30 是單一鹼基錯誤模型中的約 0.1%，不是變異正確率。 |
| coverage.svg | 四區等長；A 與 B 平均皆 1000×；200× 虛線僅作教學標記。 |
| molecules.svg | 假設各分子等量擴增；20 分子各 20 reads 與 400 分子各 1 read 都為 400。右側只畫其中 20 個分子。 |
| vaf-mixture.svg | 1 個異合腫瘤細胞加 9 個正常細胞，全為二倍體、等量 DNA；ALT 1/20＝5%。 |
| read-evidence.svg | 兩組均 20 ALT／400 reads；只繪 ALT 支持，380 REF reads 省略；非 IGV 實測截圖。 |
| splicing.svg | 人工 E1／E2／E3 結構，非實際基因座標；局部 exon skipping 不直接證明 DNA 缺失。 |
| lod.svg | 五濃度各 20 次，檢出數 4、14、19、20、20；全部為合成資料。19/20 不單獨證明可靠的 LoD。 |
| versions.svg | 版本比較與審核的概念圖，未執行臨床回歸測試。 |

第 20 頁重用既有 `figures/lesson-03-igv/SL_Sashimi1.png`，出自 [IGV 官方原圖](https://igv.org/doc/desktop/UserGuide/img/SL_Sashimi1.png)。依原比例縮放，未修改數據。為官方文件之教學引用，並非本課實測結果；不宣稱該圖片採用軟體原始碼的授權。原有出處與權利說明見第三堂投影片來源紀錄。
