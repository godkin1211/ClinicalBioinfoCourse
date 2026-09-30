# 第一堂 HTML 投影片：來源與編製紀錄

編製日期：2026-09-20。此文件記錄教學內容來源，不是系統性文獻回顧。

## 專案內容來源

- `lessons/lesson-01-germline-wes-wgs.md`：課程定位、主題與學習目標。
- `lessons/lesson-01-materials.md`：完整學員教材、名詞、分析原理、操作命令、Windows 安裝附錄。
- `demos/lesson-01-genomics/README.md`：合成資料設計、執行方法、2026-09-13 實測結果及限制。

Array 示範沿用 40 個樣本、6,000 個 SNP，QC 後 39 個樣本與 5,999 個 SNP；S40 缺失 2,000/6,000，v1 缺失 11/40，S01/S02 為已知合成複本。定序示範的 chrToy:1000 A>C、GT 0/1、DP 40、AD 20,20 來自專案實測紀錄，並非本次重新執行 calling 的結果。Windows 安裝指令尚需於實際教室環境預先驗證。

## 官方文件核對

研究查詢技能要求的 API 金鑰未設定，因此改以網頁工具直接查閱下列官方文件（2026-09-20）：

- [PLINK 1.9 basic statistics](https://www.cog-genomics.org/plink/1.9/basic_stats)：missingness、HWE、heterozygosity、sex check 定義。
- [PLINK 1.9 IBD](https://www.cog-genomics.org/plink/1.9/ibd)：IBD 報表及 PI_HAT 定義。
- [BCFtools manual](https://samtools.github.io/bcftools/bcftools.html)：mpileup、call、query 等命令文件。
- [Microsoft WSL install](https://learn.microsoft.com/en-us/windows/wsl/install)：Windows／Ubuntu 安裝途徑。

另保留教材既有 [SAMtools 官方手冊](https://www.htslib.org/doc/samtools.html) 連結供課後閱讀。

## 編排原則

### 2026-09-21 第七張補充

以 [Illumina：How to interpret DNA strand and allele information for Infinium genotyping array data](https://knowledge.illumina.com/microarray/general/microarray-general-reference_material-list/000001489) 核對 A/B 是 allele 編碼，而非固定鹼基名稱或 REF/ALT 順序；轉換時需依 manifest 與股向資訊。沿用網頁工具查閱官方文件的 fallback。

第七張新增 A／G 位點的教學假設：A 代號對應鹼基 A、B 代號對應鹼基 G，所以 AA、AB、BB 分別對應 A/A、A/G、G/G。此對照只適用這個範例，不推廣成所有位點的固定對應。

### 2026-09-21 新增第八張：SNP array 平台示意

- [Introduction to Infinium LCG Assay](https://support-docs.illumina.com/ARR/Inf_LCG_UG_15023139/Content/ARR/LCG/Intro_fINF_mLCG.htm)：Infinium II 探針 3′ 端停在 SNP 旁，以單鹼基延伸引入標記，再讀取訊號；Infinium I 的設計不同。
- [Infinium Array Product Line](https://www.illumina.com/products/by-brand/infinium.html)：Infinium I 每位點兩種探針；Infinium II 每位點一種探針，流程包含擴增、片段化、雜交、延伸、染色與成像。
- [Infinium Assay Workflow](https://www.illumina.com/content/dam/illumina-marketing/documents/products/workflows/workflow_infinium_ii.pdf)：前處理、探針捕捉與延伸染色的流程背景。

圖檔 `figures/lesson-01-snp-array-mechanism.svg` 是原創教學 SVG，以 Infinium II 為例，不代表所有 SNP array 的通用反應。DNA 的 A/T 與 G/C 是兩條同源染色體各自的互補鹼基對；本例以 T/C 股作模板，探針分別補入 A/G。兩個微珠圖示代表同一探針序列的不同拷貝，不是兩種 allele-specific 探針。標記經染色後偵測，圖中配色僅作區分，不聲稱是儀器實際的螢光通道顏色。右側群聚為概念圖，每點代表一個樣本，沒有真實測量值或預設判定門檻。

科學示意圖與研究查詢技能的外部服務金鑰仍未設定；改以官方網頁核對、原生 SVG 繪圖及瀏覽器截圖檢查，不宣稱已執行其 AI 品質評分。SVG 由建置腳本讀取並內嵌於 HTML，保留單檔離線播放功能。

### 2026-09-21 第九張：Hard call 解釋擴充

沿用研究查詢技能的官方網頁 fallback，查核 [Infinium Genotyping Data Analysis](https://www.illumina.com/Documents/products/technotes/technote_infinium_genotyping_data_analysis.pdf) 與 [DRAGEN Array Output Files](https://help.connected.illumina.com/dragen-array/product-guides/output-files)。前者說明距離群中心較遠的 calls 可有較低 GenCall score；後者將 genotype、GC score、BAF、LRR 分列為不同欄位。

第九張以「兩個同為 AB、但群聚位置與品質不同」的假設案例說明資訊摘要，沒有編造實测強度或品質分數。限制限定為只保留 genotype 欄位，未宣稱 calling 自動刪除訊號或完整報表一定不含品質。另新增 `lessons/lesson-01-slide-09-explanation.md`，包含可口述的說明、資料保存清單、BAF/LRR 與 ROH 的邊界及問答。

### 新增第十張：BAF 與 LRR 定義

將使用者的「LPR」依既有教材上下文解讀為 LRR，已先向使用者說明。沿用科學簡報與研究查詢技能的官方網頁 fallback，核對 [DRAGEN Array Output Files](https://help.connected.illumina.com/dragen-array/product-guides/output-files) 中的 Final Report 欄位：BAF 依群聚參考校正／內插；LRR 是 normalized R 相對於該 theta 之 expected R 的 log2 比值。

新頁置於 hard call 說明後；使用正常二倍體 BAF 約 0、0.5、1 與 LRR 的負／零／正作入門對照，不把 BAF 寫成未校正強度的簡單比值，不把 LRR 當成拷貝數。總訊號為預期一半時 LRR = −1 僅為算術例子，不是缺失診斷門檻。附檔 `lessons/lesson-01-slide-10-baf-lrr.md` 保留完整講解與假設算例。後段區域分析的 BAF/LRR 頁保留作回顧與應用銜接。

依科學簡報技能整理為一頁一個核心判斷，搭配文字可選取的 HTML 表格、流程與原創 SVG 圖，不使用外部圖片或病人資料。Array BAF/LRR、PCA 與 coverage 圖為明確標示的理想化／概念示意，不冒充實測圖。正文不列教授時長，答案以可展開區塊呈現。

### 2026-09-22 第十二張：QC 判讀總覽

研究查詢技能所需 API 金鑰未設定，使用官方網頁 fallback 核對以下文件：

- [PLINK Basic statistics](https://www.cog-genomics.org/plink/1.9/basic_stats)：樣本／位點缺失率、allele 頻率、HWE、雜合度與 sex check；產生報表不等於自動過濾。
- [PLINK Identity-by-descent](https://www.cog-genomics.org/plink/1.9/ibd)：親緣推估對 LD 與 allele 頻率的依賴，以及 ROH 的視窗、密度、長度等參數。
- [PLINK Population stratification](https://www.cog-genomics.org/plink/1.9/strat)：PCA 為基因型關係的摘要，可支援群體結構評估，但不直接證明分群原因。

將四組名詞卡改為「檢查問題／指標／查證方向」對照表，並加入不同病人 ID 但基因型高度相似的假設案例。99.8% 只是示範 call rate 不保證樣本身分與獨立性，並非實測結果或建議門檻。詳細定義及處置步驟放在 `lessons/lesson-01-slide-12-qc.md`，維持學員導向，不列授課時長；ROH/CNV 與群體離群均不被直接等同 QC 失敗。

### 2026-09-22 新增第 23–28 張：Panel／WES／WGS 比較與選擇

科學簡報與研究查詢技能：使用同座標 HTML 範圍圖、建庫流程、能力對照與覆蓋算例。外部研究服務金鑰未設定，改以官方網頁查核並保存以下來源；不採用廠商宣傳中的固定靈敏度或成本承諾。

- [Illumina WGS vs WES](https://www.illumina.com/techniques/sequencing/dna-sequencing/whole-genome-sequencing/whole-genome-vs-exome.html)：編碼／非編碼範圍與捕捉差異。
- [Target enrichment](https://www.illumina.com/techniques/sequencing/dna-sequencing/targeted-resequencing/target-enrichment.html)、[AmpliSeq](https://www.illumina.com/products/by-brand/ampliseq.html)：捕捉與 amplicon 為不同富集途徑。
- [Paired-end vs single-read](https://www.illumina.com/science/technology/next-generation-sequencing/plan-experiments/paired-end-vs-single-read.html)：同片段兩端的讀序；片段長度不同於 read 長度。
- [Picard metrics definitions](https://broadinstitute.github.io/picard/picard-metric-definitions.html)：目標覆蓋、達指定深度的目標比例及品質過濾概念。20× 僅用於教學算例。
- [GATK CNV postprocessing](https://gatk.broadinstitute.org/hc/en-us/articles/360056969372-PostprocessGermlineCNVCalls)：CNV 有獨立分析輸出與區域模型，不由 SNV／indel VCF 自動完成。
- [GATK resource bundle](https://gatk.broadinstitute.org/hc/en-us/articles/360035890811-Resource-bundle)、[callset evaluation](https://gatk.broadinstitute.org/hc/en-us/articles/360035531572-Evaluating-the-quality-of-a-germline-short-variant-callset)：相符的 reference／資源版本與結果品質評估。
- [NHGRI Completing the human genome sequence](https://www.genome.gov/about-genomics/educational-resources/infographics/Completing-the-human-genome-sequence)：重複序列等困難區域，不能因 WGS 名稱而假設所有位置皆已可靠分析。

範圍圖是設計示意，不是真實基因組比例或實測 coverage。第 26 張使用共同的 10 個等長目標區段；WES 深度為八格 110、一格 120、一格 0，WGS 為十格 35：共同目標平均分別為 100／35，≥20× 比例為 90%／100%。這是原創算術案例，不是效能比較研究，不推論 WGS 普遍優於 WES。

新增完整說明 `lessons/lesson-01-sequencing-choice.md`。總數 52 張，主課程第 1–44 張、附錄第 45–52 張；既有第 1–22 張不變。既有 PDF 講義未重新編譯。本段以短讀長 DNA 定序為範圍，不展開腫瘤或 RNA 分析。

### 2026-09-22 第 19 張與 run-array.sh：逐行註解

依科學簡報技能將四行命令改成編號、指令及中文解釋的一對一區塊；完整細節放在 `lessons/lesson-01-slide-19-array-commands.md` 與腳本註解。研究查詢服務無可用金鑰，沿用官方網頁查核方式，核對：

- [PLINK Basic statistics](https://www.cog-genomics.org/plink/1.9/basic_stats)：報表選項與輸出、副檔名、founder 預設、HWE 群組；`--hardy` 不等於 `--hwe` 篩選。
- [Input filtering](https://www.cog-genomics.org/plink/1.9/filter)：`--mind`／`--geno` 分別按樣本／位點篩選超過門檻的缺失率；`--maf` 篩掉低於門檻的位點。
- [LD](https://www.cog-genomics.org/plink/1.9/ld)：50 是位點數、5 是移動位點數、0.2 是成對 r² 門檻；輸出為位點清單。
- [IBD / ROH](https://www.cog-genomics.org/plink/1.9/ibd)：親緣估計與 ROH 的用途、最小 SNP 數／長度，以及仍適用的其他視窗條件。
- [Population stratification](https://www.cog-genomics.org/plink/1.9/strat)：PCA 的成分數、eigenvec／eigenval 輸出。

新增 3/40 → 1/38 的缺失率例子為獨立教學假設，不是既有合成分析實測結果。明示整份腳本不會暫停等人工確認，clean 並不代表所有 QC 完成。未改動任何可執行指令、門檻或分析順序。

### 2026-09-22 新增 Array／NGS 檔案格式總覽

採用學員導向的「格式／內容／用途與限制」對照表，沿用離線 HTML 排版，不轉成圖片投影片。新增第 11 與第 31 張，共 54 張；主課程至第 46 張，附錄自第 47 張起。依科學簡報技能核對官方文件，研究服務金鑰未設定，使用網頁查核替代：

- [Illumina iScan generated files](https://support-docs.illumina.com/ARR/iScan/Content/ARR/iScan/GeneratedFiles_fIS.htm)：IDAT 與 GTC 的資料層次不同。
- [DRAGEN Array output files](https://help.connected.illumina.com/dragen-array/product-guides/output-files)：GTC、Final Report、BAF／LRR；報表欄位受軟體與匯出設定影響。
- [DRAGEN Array input files](https://help.connected.illumina.com/dragen-array/dragen-array-v1.0/product-guides/input-files)：manifest（BPM／CSV）與 EGT 群聚資源，不是樣本原始量測。
- [Thermo Fisher microarray analysis software](https://www.thermofisher.com/sg/en/home/life-science/microarray-analysis/applications/predictive-genomics/population-genomics/software.html)：Axiom 掃描後的 CEL 分析輸入；不把不同廠牌流程混為一談。
- [Illumina FASTQ](https://help.connected.illumina.com/basespace/files-used-by-basespace/fastq-files)：read 名稱、序列與鹼基品質；paired-end 的 R1／R2。
- [HTS format specifications](https://samtools.github.io/hts-specs/)：SAM、BAM、CRAM、VCF／BCF 與相關索引；區分文字與二進位編碼，避免把索引當資料本體。
- [GATK gVCF](https://gatk.broadinstitute.org/hc/en-us/articles/360035531812-GVCF-Genomic-Variant-Call-Format)：非變異位置信心與區塊記錄，供相容 joint genotyping 流程使用；不暗示所有 caller 的 gVCF 可混用。

明示 PLINK hard-call 格式不保存完整強度，CRAM 常需相符 reference，以及 .gz 副檔名不足以保證檔案可區域索引。保留既有 BED／BIM／FAM 詳解及 FASTQ／BAM／VCF 問題導向頁，不取代原內容。未更動分析腳本或 PDF 講義。
