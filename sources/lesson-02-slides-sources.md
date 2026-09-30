# 第二堂 HTML 投影片：來源與查核紀錄

## 2026-09-28：TMB、MSI、HRD 分頁擴充

原第 40 頁改為三張獨立頁（40 TMB、41 MSI、42 HRD），後續順延兩頁。以生物資訊輸入、處理、QC、輸出定義及解讀限制為主，不提供治療門檻。每頁保留算例／判讀例及三段學員詳解。研究查詢技能的 API 未設定，改以 web 直接核對原始研究與官方資料；PMC／PubMed 部分全文遭 reCAPTCHA，JITC HTML 回傳 403，以下區分可取得的來源，不宣稱全部全文已重新讀取。

| 查核來源 | 本次用途與取得狀態 |
|---|---|
| [Merino et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7174078/)，DOI 10.1136/jitc-2019-000147 | 搜尋可取得原始研究摘要與出版資訊；TMB 分子／分母、panel 與 WES 的差異及方法校準。延續既有來源，不設定通用 cutoff。 |
| [MSIsensor 官方專案](https://github.com/ding-lab/msisensor)；[Niu et al., 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC3967115/)，DOI 10.1093/bioinformatics/btt755 | 官方方法文件可讀取，原研究搜尋摘要可取得；長度分布比較、tumor–normal 與 tumor-only 模型區別。 |
| [Telli et al., 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC6773427/)，DOI 10.1158/1078-0432.CCR-15-2477 | 原始研究搜尋片段可取得，直接全文遇驗證頁；LOH／TAI／LST 計數與組合分數案例，不移植研究門檻。 |
| [FDA myChoice CDx 技術描述，P190014S002](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id=P190014S002) | 官方資料可取得；GIS 使用 LOH、TAI、LST，並與 BRCA 狀態區分。此歷史文件僅支持技術描述，不當作目前適應症摘要。 |
| [Cruz et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5961353/)，DOI 10.1093/annonc/mdy099 | 原始研究搜尋段落可取得，直接全文遇驗證頁；疤痕可能持續存在於 HR 功能恢復後，RAD51 foci 與功能評估。 |
| [Hechtman et al., 2020](https://www.nature.com/articles/s41379-019-0414-6)，DOI 10.1038/s41379-019-0414-6 | 原始研究搜尋摘要可取得；MSI-H 與 MMR 蛋白表現並非完全一致，不能互相直接替代。 |

本次教學推論：一般小 panel 未必具有疤痕分析所需的廣泛 SNP 覆蓋；不能把一般 CNV 的 SEG 欄位任意加總視為經驗證 HRD 檢測。HRD 基因變異、基因體疤痕、功能性檢測分屬不同證據層次；無法評估不能回報成陰性。

人工算例核對：8/0.8=10 mut/Mb；(8+2)/0.8=12.5 mut/Mb。MSI 比例型分數的教學例為 12/80×100=15%，不是所有方法共同定義或臨床閾值。未執行 TMB／MSI／HRD 檢測，未新增病人資料。

編製／核對日期：2026-09-27。依既有學員教材與合成練習製作，不使用病人資料，也不將人工案例當作 somatic caller 的實測效能。

## 內容來源與取捨

- 主來源：`lessons/lesson-02-materials.md`、`demos/lesson-02-somatic/README.md` 及其中的產生器、計數、驗證與模型腳本。
- 精簡教案只作範圍參考；採用完整版已釐清的表述：「正反向 reads」不稱作 duplex，「保留研究候選」不寫成確定的 somatic 真值。
- 科學簡報技能用於案例主線、圖表層次、字級、留白與逐頁視覺驗證；依使用者要求產生可離線的原生 HTML，而非圖片 PDF。
- 研究查詢技能所需 `PARALLEL_API_KEY`／`OPENROUTER_API_KEY` 均未設定，改以官方文件與原始研究網頁核對；未呼叫付費研究服務。
- 現行共 64 張：第 1–46 張主課程，第 47–64 張選讀附錄與資源。正文不列各段授課時長。

## 方法參考

| 來源 | 對應內容 |
|---|---|
| [GATK Mutect2](https://gatk.broadinstitute.org/hc/en-us/articles/360037593851-Mutect2) | Tumor–normal／tumor-only、局部組裝與 somatic 模型；作概念案例，不在課堂執行完整 GATK。 |
| [GATK somatic workflow](https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2) | Calling 之外的 filtering、orientation model、污染估計與 PoN；不將固定教材規則當作官方預設。 |
| [NCI GDC MAF format](https://docs.gdc.cancer.gov/Data/File_Formats/MAF_Format/) | MAF 為 Mutation Annotation Format；與 minor allele frequency 區分。 |
| [SAMtools](https://www.htslib.org/doc/samtools.html)、[BCFtools](https://samtools.github.io/bcftools/bcftools.html) | SAM/BAM 轉換、排序、索引與 VCF 查詢語法。 |
| [IGV alignments](https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/)、[reference](https://igv.org/doc/desktop/UserGuide/reference_genome/) | Reference、alignment 顯示與 downsampling 的限制。 |
| [fgbio duplex consensus](https://fulcrumgenomics.github.io/fgbio/tools/latest/CallDuplexConsensusReads.html) | 原始分子雙股的配對／consensus 不等同一般正反向 read 支持。 |
| [Shen & Seshan, FACETS, 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5027494/)；DOI: 10.1093/nar/gkw520 | 深度與 allelic imbalance、segmentation、purity/ploidy 與 allele-specific CN；不假設 ratio 唯一決定絕對 CN。 |
| [Manta 原始專案](https://github.com/Illumina/manta) | SV 的 paired/split-read 與組裝概念，不推薦或安裝特定版本。 |
| [Merino et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32217756/)；DOI: 10.1136/jitc-2019-000147 | TMB 跨平台量化差異、定義與校準；不提供臨床處方閾值。 |
| [Razavi et al., 2019](https://www.nature.com/articles/s41591-019-0652-7)；DOI: 10.1038/s41591-019-0652-7 | cfDNA 變異來源、白血球與克隆性造血的干擾。 |

## 圖形與數值的來源

- A／B 讀段圖為原創 HTML 示意，只選六條 ALT 支持讀段說明方向與末端關係；不是 IGV 截圖、不是完整 pileup，不能從圖上算 VAF。
- 十個細胞示意：一個二倍體腫瘤細胞帶一份 ALT，九個正常細胞無 ALT；1/20=5%，純度 10%、CCF 100%。
- 混合公式 `p*f*m / (p*C + (1-p)*2)`：正常 CN2 且無 ALT、各腫瘤細胞局部 CN 相同、allele 取樣無偏。p 是此模型中的細胞比例，不混同 DNA fraction；不作無前提的病人 CCF 反推。
- 固定 p=.2、f=1、C=6，m=1／3 時為 7.1429%／21.4286%。
- CN6 相對正常 CN2 的混合 log2 ratio：p=.2／.6／1 時為 .485427／1.137504／1.584963。條圖同一線性尺度，數值由公式計算，不是 BAM 的 CN 測量。
- 3/8=37.5% 的 cohort 分母例子是原創假設，不是研究統計結果。
- Normal 0/200 的 `3/n` 是獨立抽樣下的近似單側 95% 上界。精確值為 `1 - .05**(1/200)`，約 1.487%；不是方法 LOD。
- Binomial 模型至少 3 條 ALT 的機率：n=30、100、400 時為 .187821、.881737、.999999701（末值近似）；只在無錯誤且獨立讀段假設下成立。

## 初版的合成練習驗證（敘事重整未修改實作資料）

於新的暫存練習目錄 `/private/tmp/lesson02-slides-check.2O9nug/practice` 執行既有 `generate.py`、`prepare.sh`、`verify.py` 與 `models.py`，未修改分析腳本。

- SAMtools 1.22、HTSlib 1.22.1、BCFtools 1.22。
- `verify.py` 通過 BAM 計數、偏差形狀、VCF 欄位、索引檔及 CN/VAF 模型核對。
- A：tumor 20/400、正反 ALT 各 10、末端 ALT 0；normal 0/200。
- B：tumor 20/400、ALT 全正向且末端 20；normal 0/200。
- D：tumor 200/400、normal 100/200。
- C：獨立 SEG 模型 .485427，不從 toy BAM depth 計算。

這是教材一致性檢查，不是臨床分析流程驗證。未在本次操作 IGV Desktop 或 Windows／WSL；桌面步驟依官方文件，仍需課前確認實際環境。

## 2026-09-27 敘事重整與新增來源

依使用者要求改成「目的 → 效益 → 實務 → 採樣與製備 → 下機 QC → 分析 → 解讀」。新增 14 張概念頁，將原主課程 10 張操作或深入模型頁移入附錄。未更改合成資料與生物資訊脚本。

使用研究查證技能的官方網頁替代查詢路徑，以下為本次讀取的來源及採用範圍；不引用通用檢體處理時限、不提供通用深度閾值或臨床處方。

| 官方來源 | 查核後採用的內容 |
|---|---|
| [NCI, Biomarker Testing for Cancer Treatment](https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment) | 同癌別可能有不同分子變化；檢测在適用情境提供治療／試驗線索，但非人人受益。腫瘤檢測與遺傳性風險檢測不同；疑似生殖系結果需確認。 |
| [NCI Best Practices, fourth edition, 2026](https://dctd.cancer.gov/data-tools-biospecimens/biospecimens-biobanks/resources/best-practices/biospecimen-resources/appendices/2026-4th-edition-best-practices.pdf) | 前分析處理、來源與採樣紀錄、固定／保存、核酸品質及追蹤鏈的重要性。教學轉譯為臨床／病理／實驗室與生物資訊的資料交接。 |
| [Picard metrics definitions](https://broadinstitute.github.io/picard/picard-metric-definitions.html) | 比對品質、insert size、duplicates、fingerprinting、capture target coverage 等指標各回答不同問題；平均值不代表每個位置。 |
| [Illumina Library Quantification](https://support-docs.illumina.com/SHARE/ClusterOptimize/Content/SHARE/ClusterOptimize/LibraryQuantification.htm) | 文庫定量需適當方法；片段／完整度 QC 與定量不能直接互換。未將單一試劑規格推廣成全平台閾值。 |
| [Illumina TruSeq DNA PCR-Free Reference Guide](https://www.illumina.com/content/dam/illumina-support/documents/documentation/chemistry_documentation/samplepreps_truseq/truseq-dna-pcr-free-workflow/truseq-dna-pcr-free-workflow-reference-1000000039279-00.pdf) | 接上 adapter 建立 indexed library；不同文庫方法並非都有 PCR，因此圖示明示步驟依方法而異。 |
| [FastQC introduction](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/1%20Introduction/1.1%20What%20is%20FastQC.html)、[per-base quality](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html) | 分析前檢視 raw read 品質與偏差；不同模組須結合實驗設計判讀。 |
| [MultiQC overview](https://docs.seqera.io/multiqc) | 彙整其他工具的既有分析結果；不是另外執行全部 QC 分析，更不是自動决定是否淘汰樣本。 |

QC 回饋表為上述原則的教學綜合，不是任何工具的自動決策規則；補定序、重製文庫或重新採樣均須由責任人員評估。圖示由原生 HTML/CSS 建構，保持可編輯與離線播放。

## 逐頁說明加強版

依使用者要求補足每頁的名詞、原理、具體例子及解讀步驟。維持 61 頁；60 張非封面頁直接顯示例子，全部 61 頁提供三段詳解，另產生可獨立閱讀／列印的 HTML。文字原稿為 `lessons/lesson-02-slide-explanations.md`。

科學簡報技能用於分層呈現與視覺檢查；本次依使用者需求採完整句子，不強制縮成關鍵詞。研究查詢技能依既有官方來源延伸，並以 web 工具重新核對 NCI biomarker testing、Picard metrics、GATK Mutect2、fgbio duplex、SAMtools、BCFtools。FACETS 的 PMC 頁本次遇到 reCAPTCHA，延用前次已記錄的文獻與明示模型，不宣稱重新取得全文。

新增 MSI 原始方法來源：[Niu et al., MSIsensor, 2014](https://pubmed.ncbi.nlm.nih.gov/24371154/)，DOI: 10.1093/bioinformatics/btt755。用於說明微衛星長度分布評估，未安裝工具或採用臨床閾值。

新增教學算例已直接重算：

- 深度 1000、900、100、0 的平均為 500；以示意 100× 為條件，breadth=3/4=75%。100× 不作臨床建議。
- 真實比例 1%、200 次獨立取樣時，零 ALT 機率 `0.99**200=0.1339796749`，約 13.4%。不是方法 LOD。
- 20% CN6 腫瘤＋80% CN2 正常：平均 2.8 份，相對二倍體 1.4 倍，`log2(1.4)=0.4854268272`。
- TMB 10/1=10/Mb、10/0.5=20/Mb 僅為分母算例，不是平台效能或治療判準。

生殖系／體細胞來源、陰性解讀、分子數／reads、三層證據審核等均維持原課程範圍。沒有增加病人資料、治療建議或新的生物資訊執行結果。

## 2026-09-28：新增第 18 頁 FastQC 判讀

在原第 17 頁後插入一張學員導向的結果判讀對照表，後續頁碼順延。科學簡報技能用於延續版型、將完整解釋放入逐頁詳解並做視覺檢查。研究查詢技能所需的 Parallel／OpenRouter API 未設定，改用 web 工具直接核對以下官方文件；沒有上傳或處理任何病人 FASTQ。

| 官方來源（本次已讀取） | 對應教學內容 |
|---|---|
| [FastQC — Per Base Sequence Quality](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html) | 讀取位置、Q 值、紅色中位數、25–75% 箱體、10–90% 鬚線、藍色平均值；末端下降與短暫低谷須分開判斷。 |
| [FastQC — Adapter Content](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/10%20Adapter%20Content.html) | 接頭曲線為累積比例；短片段可能產生 read-through。 |
| [FastQC — Per Sequence GC Content](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html) | 逐 read GC 分布及模型比較；不把形狀異常直接判為污染。 |
| [FastQC — Duplicate Sequences](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html) | 序列重複無法區分 PCR 複本與生物來源相同序列；起點受限／富集文庫需按設計解讀。 |

教學推論：癌症 panel 需依捕獲／amplicon 設計、同批樣本與院內 SOP 解讀，不將隨機文庫的預期直接套用。FastQC 重複率不是依比對座標估計的 BAM duplicate 指標，也不是 UMI 分子數。依 Phred 定義 `p=10**(-Q/10)`，Q20=0.01、Q30=0.001；此數值是鹼基判讀錯誤機率估計，不是變異可信度。新頁為指南與假設案例，不宣稱是實際 FastQC 執行結果。
