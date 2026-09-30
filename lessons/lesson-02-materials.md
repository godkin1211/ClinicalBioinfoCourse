# 癌症體細胞基因體分析：從定序證據到可信的候選事件

`講師`: 奇美醫院精準醫學核心實驗室組長邱家軍

本教材適合臨床醫師、臨床工作者及初次接觸癌症定序分析的研究人員。你不必先會寫程式；可以先閱讀概念與案例，再使用附錄安裝的工具完成練習。

第一堂介紹了基因體資料格式與基本 QC；這一堂進一步處理腫瘤樣本特有的困難：正常細胞混入、不同腫瘤次族群、拷貝數改變，以及檢體處理造成的錯誤。重點是判斷技術證據與分析限制，不是開立處方、致病性分類或正式臨床 actionability 分級。

所有實作使用合成資料。你將實際建立 BAM、查詢 VCF、檢查讀段證據並計算簡化模型；不會將人工案例誤當成真實 somatic caller 的偵測結果，也不會以本練習驗證臨床檢測效能。

## 閱讀方式與學習目標

建議依序閱讀研究設計、分析原理、實作與案例解析。操作前先完成附錄 A；已完成第一堂安裝者，可直接檢查 Python、SAMtools、BCFtools 是否可用，再安裝 IGV。暫時不能安裝時，可利用文中的輸出表完成判讀。

完成後，你應能：

- 說明 tumor–normal 與 tumor-only 能提供哪些不同的資訊。
- 串接 SNV/indel、CNV、SV 的資料流，區分原始讀段、caller 輸出與 annotation。
- 解釋 VAF 為何不等於腫瘤純度或帶有變異的癌細胞比例。
- 找出低 VAF 候選事件的支持證據與可疑訊號。
- 在分析紀錄中清楚寫出「已觀察到什麼」與「尚不能確定什麼」。

## 一、研究案例：兩個 5% VAF，能得到相同結論嗎？

你收到一批肺腺癌 FFPE 定序資料，部分樣本有配對正常檢體，部分只有腫瘤。兩個候選位點都得到 400 條有效讀段，其中 20 條支持替代等位基因：

```text
VAF = 支持 ALT 的讀段數 / 納入計算的讀段總數
    = 20 / 400 = 5%
```

第一個位點的 ALT 讀段分布在正、反向比對，變異多位於讀段內部；第二個位點的 ALT 全部來自同一方向，而且集中在讀段末端。你會把兩者都列為相同可信度嗎？

這個問題不能只用「高深度」或「低 VAF」回答。你需要知道樣本來源、讀段品質、比對位置、正常樣本證據、分析模型及篩選規則。

### 1.1 Somatic 與 germline 是來源概念，不是 VAF 分類

Germline variant（生殖系變異）通常源自生殖細胞或受精卵，存在於多數體細胞；somatic variant（體細胞變異）是在發育或生命歷程中後來產生，可能僅存在於部分組織或細胞。

腫瘤內同時包含 inherited germline 與後天 somatic 變異。不能把 VAF 約 50% 一律當 germline，也不能把低於 50% 一律當 somatic。拷貝數、純度、嵌合與抽樣都會改變比例。

本課的「候選事件」表示值得檢查的分析結果，不等於已確認的腫瘤驅動事件。

### 1.2 先整理檢體與樣本對照表

| 欄位 | 為什麼需要 |
|---|---|
| 個案 ID、檢體 ID、定序 sample ID | 防止配錯 tumor 與 normal、重複或交換樣本 |
| 組織來源、採樣時間、治療前後 | 同一個案不同時間或病灶可能有不同克隆組成 |
| FFPE／冷凍、DNA 輸入量與品質 | 影響片段長度、分子數及損傷背景 |
| 病理估計 tumor cellularity | 提供純度的初步背景，但不是精確的 DNA purity |
| Panel／WES／WGS、目標區與版本 | 決定可分析範圍及結果能否比較 |
| 文庫批次、UMI、定序策略 | 決定 duplicate、consensus 與錯誤處理方式 |
| 配對正常來源與可用性 | 影響 germline 排除、污染判讀與 somatic 推論 |
| Reference、流程版本、資料存放位置 | 確保結果可重建與回查 |

Tumor cellularity 是病理觀察中腫瘤細胞所占比例；分析模型中的 purity 則與 DNA 混合及倍體假設相關。兩者可互相參考，但受切片區域、細胞大小及拷貝數等因素影響，不一定完全相等。

## 二、選擇 tumor–normal 或 tumor-only 分析

### 2.1 配對正常的作用

Matched normal 是同一個人的非腫瘤參考檢體。它讓你比較「在這個人本來就存在的 allele」與「腫瘤中特別出現的證據」，也有助於排除部分個體特有的比對或序列問題。

| 設計 | 需要的輸入 | 可以增加的資訊 | 仍然無法保證的事 |
|---|---|---|---|
| Tumor–normal | 腫瘤與同一人的正常 BAM/CRAM、配對紀錄 | 個體 germline 證據、腫瘤／正常相對支持度 | 正常覆蓋不足、腫瘤污染正常、正常組織嵌合仍可能干擾 |
| Tumor-only | 腫瘤 BAM/CRAM、適合的族群資源與技術背景 | 依頻率、模型與技術資訊縮小候選集合 | 無法可靠區分所有 germline 與 somatic 事件 |

血液不在所有情境下都是理想 normal。血液腫瘤或 clonal hematopoiesis（克隆性造血）可能使血液帶有 somatic 變異；鄰近正常組織也可能有腫瘤污染或場域效應。選擇來源時，要先知道研究疾病與檢體限制。

### 2.2 正常樣本沒有 ALT，不等於證明不存在

假設正常樣本 200 條有效讀段中沒有 ALT，你只能說「在這些讀段中未觀察到 ALT」。若真正比例很低，仍可能因抽樣沒看到。在簡單獨立抽樣模型下，0 次成功的單側約 95% 上界可用 3/n 近似；n=200 時約 1.5%。這不是檢測方法的臨床偵測極限。

反過來，normal 有少量 ALT 也不必然表示 germline：污染、比對錯誤、嵌合或組織背景都需要納入考慮。判讀應同時比較兩個樣本的品質，而非只比較兩個 VAF。

### 2.3 PoN 與族群資源不能代替 matched normal

Panel of normals（PoN，正常樣本面板）彙整多份正常資料中的技術背景，可協助辨認重複出現的 artifacts。它最好與研究資料的平台、捕捉設計及流程相容，並不等於這位個案的 germline 清單。

Germline population resource 提供族群 allele frequency，協助評估常見 germline 的可能性。但「資料庫沒收錄」不代表 somatic，「資料庫有收錄」也不代表此個案的訊號一定是 germline。稀有性與來源是不同問題。

Tumor-only 結果可能包含尚未辨明的 germline 事件。研究表格應保留不確定性；涉及個案回報時需依既定倫理、同意與專業協作流程處理，而不是由分析人員單憑 VAF 下結論。

## 三、從 FASTQ 到候選事件：三條相連但不同的分析路徑

```text
檢體與配對資訊 + reference + target regions
    ↓
FASTQ → read QC → alignment → BAM/CRAM + index
    ↓
樣本核對、污染、coverage、duplicate／UMI 檢查
    ├─ SNV/indel：局部序列證據 → somatic caller → filtering
    ├─ CNV：read depth + allele balance → normalization → segmentation
    └─ SV：split reads + paired-end + depth／assembly → breakpoint candidates
    ↓
QC-reviewed candidate set → annotation → 結果表與必要的驗證
```

### 3.1 SNV/indel calling 的核心問題

Caller 要比較「這些讀段可能由真實變異產生」與「可能只是定序、比對或其他背景錯誤」的支持程度。腫瘤不適合只用固定二倍體的 0%、50%、100% 期待來分析，因為混合與亞克隆讓 VAF 可以落在更廣的範圍。

以 Mutect2 為例，它透過局部 haplotype assembly 與 somatic 模型偵測短變異；原始輸出還需交由 FilterMutectCalls 等步驟處理。這是一個工具案例，不代表所有流程都必須使用它。[Mutect2 官方文件](https://gatk.broadinstitute.org/hc/en-us/articles/360037593851-Mutect2)

Haplotype 是同一條染色體上相連的 allele 組合；局部組裝嘗試重建候選序列，避免僅逐位點數鹼基而忽略 indel 附近的複雜比對。Likelihood 是在特定模型下觀察到這些資料的相對支持度，不是直接的臨床可信度。

### 3.2 Calling、filtering、annotation 各自回答不同問題

| 步驟 | 問題 | 常見輸出 |
|---|---|---|
| Calling | 哪些位置有足夠證據成為候選變異？ | 未篩選 VCF、模型統計 |
| Filtering | 哪些候選受污染、方向偏差、germline 等因素影響？ | FILTER 標記、篩選統計 |
| Annotation | 這個變異落在哪個基因、轉錄本或已知條目？ | 註解 VCF、表格或 MAF |
| Review／validation | 是否有充分而可重現的技術證據？ | 人工紀錄、追加實驗結果 |

例如，Mutect2 的方向性資訊可經 LearnReadOrientationModel 建模，與其他資訊一起供 filtering 使用；污染估計也是獨立的證據來源。不要把跑完 caller 當成完成分析，也不要把所有 FILTER 直接刪掉而失去追蹤原因。[GATK somatic 流程說明](https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2)

本課實作聚焦於候選事件的證據稽核，不跑完整 Mutect2、人類基因體 alignment 或 CNV/SV caller。因此，不需要下載大型人類 reference、PoN 或安裝整套 GATK；如果後續要執行完整流程，需要另行準備相容資料、環境及驗證方案。

### 3.3 VCF、MAF 與 segmentation 檔案

VCF 的 CHROM/POS/REF/ALT 定義事件；FORMAT 後的多個樣本欄位提供各自的證據。讀入前先查樣本名稱，不要假設第一欄一定是 tumor。AD 常按 REF、ALT1、ALT2 排列；DP 與 AD 的納入規則依工具而異；AF 可能是模型估計而非單純 AD 比例。

MAF 在此指 **Mutation Annotation Format**，不是第一堂的 minor allele frequency。它常用於癌症 cohort 的變異註解與摘要；欄位可能包含基因、座標、variant classification 與 tumor sample barcode。它通常不保留 BAM 的完整讀段證據，不能代替 VCF/BAM 做 QC。相同縮寫必須依上下文解讀。

Segmentation 檔將連續區域摘要成區段，包含樣本、染色體、起訖位置及區段值。區段值可能是 log2 copy ratio，也可能是絕對 copy number；先查欄位定義。不要把 0.5 的 log2 ratio 讀成「0.5 個拷貝」。

## 四、腫瘤資料的品質控制：深度之外還要看什麼？

### 4.1 FFPE、低輸入量與系統性錯誤

FFPE 是 formalin-fixed paraffin-embedded（福馬林固定石蠟包埋）。DNA 可能片段化、交聯或發生損傷；胞嘧啶脫胺可造成 C>T／互補方向 G>A 類型的假訊號。但 **C>T 本身不等於 artifact**，真實腫瘤變異也可能是這個替換。

低輸入量代表起始分子有限。反覆定序同一批 PCR 產物可以增加 read depth，卻未必增加獨立證據。系統性錯誤若存在於模板或特定序列環境中，增加深度甚至會使錯誤看起來更穩定。

| 證據 | 要問的問題 | 不能單獨得出的結論 |
|---|---|---|
| Depth、ALT count | 支持讀段多不多？是否來自足夠獨立分子？ | 高深度一定真實 |
| Base quality | ALT 鹼基本身品質如何？ | 品質分數能涵蓋全部前處理損傷 |
| Mapping quality | 是否可能對到錯誤區域？ | MAPQ 高就沒有 reference 或重複區問題 |
| Strand／orientation | ALT 是否集中在特定方向或 read-pair 類型？ | 正反方向皆有就等於 duplex 驗證 |
| Read position | ALT 是否只出現在末端或 soft clips 附近？ | 所有末端變異都是錯誤 |
| Local context | 周圍是否為 homopolymer、重複序列或 indel？ | 熱點資料庫可以消除比對疑慮 |
| Normal evidence | normal 深度、ALT、污染是否足夠評估？ | normal 0 reads 證明完全不存在 |

Soft clipping 是比對中未納入對齊的讀段端部；它可來自接頭、比對困難或真實結構變異。需要看群體一致性與區域背景，不是見到 clipping 就刪除。

### 4.2 Strand、orientation 與 duplex 不要混用

Read strand 指比對到 reference 的正／反向。Paired-end orientation 同時涉及配對、read1/read2 與方向；F1R2/F2R1 不是單純的正股／反股計數。

Duplex consensus 需要將原始 DNA 雙股的相應分子證據配對整合。一般 BAM 中正反向都有 ALT，不代表已證明原始同一 DNA 分子的雙股都支持。本課合成 BAM 是 single-end，僅示範 strand 與 read-end bias，不示範 F1R2 或 duplex。

UMI（unique molecular identifier）是在適當文庫流程中加入的分子標記，協助辨識讀段家族與建立 consensus。Raw depth、unique molecule depth、consensus depth 不可混為一談。UMI 也不能自動解決所有前期損傷、標記碰撞或比對錯誤。

### 4.3 技術可信度與功能重要性分開評估

Hotspot 表示某位置有已知重複出現或功能相關背景；它能增加研究興趣，不能替代原始證據。反之，沒有人報導的新位置也不必然是假陽性。

多個 caller 都報出同一事件也不是獨立實驗驗證：它們可能共用相同比對與錯誤來源。Orthogonal validation（正交驗證）是以具有不同限制或原理的方式查核；所選方法的靈敏度必須適合目標 VAF，不能假設任何傳統方法都能確認低頻訊號。

## 五、VAF、純度、拷貝數與克隆性

### 5.1 從簡單的混合模型開始

假設正常細胞為二倍體，normal 不帶該 ALT；腫瘤細胞在此區域的總拷貝數一致，且各 allele 的定序機會相同。令：

- p：腫瘤純度，腫瘤細胞在混合模型中的比例。
- f：cancer cell fraction（CCF），帶有這個變異的腫瘤細胞比例。
- m：帶變異腫瘤細胞內的 mutant copy 數。
- C：此區域每個腫瘤細胞的總 copy number。

```text
預期 VAF = p × f × m / [p × C + (1 − p) × 2]
```

分子是混合物中的 ALT 拷貝貢獻；分母是全部 allele 拷貝貢獻。這是用來理解影響因素的簡化模型，不是可以不帶前提地反推每個病人的 CCF。若亞克隆有不同 CN、normal 也帶 ALT、倍體不同或存在比對偏差，就需要更完整的模型。

| 情境 | p | f | m | C | 預期 VAF |
|---|---:|---:|---:|---:|---:|
| 二倍體、clonal heterozygous | 0.6 | 1 | 1 | 2 | 30% |
| 純度低，但仍是 clonal | 0.1 | 1 | 1 | 2 | 5% |
| 純度 60%，一半癌細胞帶變異 | 0.6 | 0.5 | 1 | 2 | 15% |
| 總 CN=6，只有一份 mutant copy | 0.2 | 1 | 1 | 6 | 約 7.14% |
| 總 CN=6，有三份 mutant copy | 0.2 | 1 | 3 | 6 | 約 21.43% |

Clonal 指在分析解析度下，多數或全部癌細胞帶有事件；subclonal 指只存在於部分癌細胞。上述例子說明：5% VAF 也可能來自 clonal event，不能自動解讀成「只有 5% 癌細胞有變異」。

練習：若觀察到 VAF=15%，除了「純度 60%、CCF 50%」，還有什麼解釋？在同樣二倍體、單份 ALT 假設下，純度 30%、CCF 100% 也能得到相同數字。單一 VAF 無法同時辨認所有未知量。

### 5.2 拷貝數改變會被低純度稀釋

在以正常二倍體為基準、假設測量無偏差的例子中：

```text
copy ratio = [p × C + (1 − p) × 2] / 2
log2 ratio = log2(copy ratio)
```

若腫瘤區域 C=6、p=0.2，混合物的平均拷貝貢獻為 2.8，ratio=1.4，log2 ratio 約 0.485。純腫瘤的 C=6 則為 log2(3)≈1.585。同一個增益在低純度下看起來較小。

```text
同為腫瘤 C=6；以下每個 # 約代表 0.1 log2 ratio（示意）
p=0.2   #####             0.485
p=0.6   ###########       1.138
p=1.0   ################  1.585
```

真實 CNV 流程可能以樣本整體或不同倍體基準正規化，不能把上式直接套在所有 segmentation 輸出。Purity/ploidy fitting（純度／倍體估計）會利用全基因體或目標區的 depth、BAF 等資訊共同推估，可能存在多組合理解。

## 六、實作：建立可回查的腫瘤與正常證據

### 6.1 準備練習資料

本練習不需要第一堂的輸出。在 Windows 的 WSL Ubuntu、macOS Terminal 或 Linux Terminal 執行以下指令；先完成附錄 A 的安裝與工具檢查。若專案路徑不同，只修改第一行：

```bash
cd ~/ClinicalBioinfoCourse/demos/lesson-02-somatic
python3 generate.py practice-local01
cd practice-local01
bash ../prepare.sh
```

`practice-local01` 必須是新資料夾；產生器拒絕覆蓋既有資料。若重做，改成 `practice-local02`。`prepare.sh` 重跑會取代同名分析輸出，重要版本應分開保存。

產生器建立 5,000 bp 的人工 contig `chrToy`、腫瘤／正常 SAM、候選 VCF，以及獨立設計的 CN 區段檔。所有 read 位置與候選標記都是人工指定，**不是 aligner 或 somatic caller 的輸出**。真實分子的獨立性、PCR、UMI、paired-end 與 FFPE 化學損傷沒有被模擬。

| 檔案 | 用途 |
|---|---|
| `reference.fa`、`.fai` | 人工 reference 及索引；不可改用 hg19/hg38 開啟本例 |
| `tumor.bam`、`normal.bam` 與 `.bai` | 已排序索引、可供 IGV 查看之讀段 |
| `candidates.vcf.gz`、`.tbi` | 三個人工候選 SNV，含 TUMOR/NORMAL 欄位 |
| `candidates.tsv` | VCF 查詢結果 |
| `tumor.evidence.tsv`、`normal.evidence.tsv` | 從 BAM 讀段重新計算的支持證據 |
| `copy_number.seg` | 獨立的 CN 混合模型示意，不是由上述 BAM depth 算出 |

### 6.2 理解資料轉換，而不只執行腳本

`prepare.sh` 先完成下列步驟。你可以在練習資料夾逐行操作，理解輸入與輸出：

```bash
samtools faidx reference.fa
samtools view -b tumor.sam | samtools sort -o tumor.bam
samtools index tumor.bam
samtools quickcheck -v tumor.bam
samtools flagstat tumor.bam
bcftools query -l candidates.vcf.gz
bcftools view -h candidates.vcf.gz
bcftools query -f '%CHROM\t%POS\t%ID\t%FILTER[\t%SAMPLE:%AD:%DP:%AF]\n' candidates.vcf.gz
```

`samtools view -b` 轉成 BAM；`sort` 排序；`index` 支援區域查詢。`quickcheck` 主要檢查基本檔案結構，不會證明每條 read 都正確；`flagstat` 統計比對旗標，不會證明 candidate 可信。

`bcftools query -l` 顯示樣本名稱；`-h` 顯示 header。先確認 TUMOR/NORMAL 欄位，再讀各樣本數字。這裡 `AF` 是產生器指定的比例；真實檔案需依 header 與 caller 文件確認定義。[BCFtools 文件](https://samtools.github.io/bcftools/bcftools.html)

本例 GT=0/1 是人工表示 REF 與 ALT 同時存在，不能把腫瘤的 0/1 當成「每個腫瘤細胞都是二倍體雜合」。ReviewBias、NormalEvidence 也是教材自訂 FILTER，不是 Mutect2 的正式 filter 名稱。

### 6.3 直接從讀段核對，不只相信 VCF

```bash
samtools view tumor.bam | python3 ../audit_reads.py
samtools view normal.bam | python3 ../audit_reads.py
cat tumor.evidence.tsv
cat normal.evidence.tsv
```

`audit_reads.py` 只支援本例的 `150M` CIGAR。它排除 unmapped、secondary、QC-fail、duplicate、supplementary flags，並要求 MAPQ≥20、BQ≥20，逐位點計數 T allele。`ALT_END5` 是 ALT 距任一讀段端部不足 5 個鹼基的數量。這些門檻只為教學；腳本不處理 indel、重疊 read pairs、UMI 或 somatic likelihood，不能取代正式 pileup/caller。

預期的腫瘤輸出：

| POS | DEPTH | ALT | VAF | ALT_FORWARD | ALT_REVERSE | ALT_END5 |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 400 | 20 | 0.05 | 10 | 10 | 0 |
| 1500 | 400 | 20 | 0.05 | 20 | 0 | 20 |
| 2500 | 400 | 200 | 0.50 | 100 | 100 | 0 |

正常樣本在 500/1500 各有 200 條讀段、0 ALT；2500 則為 100/200=50%。

請先記錄：哪一個差異被 VAF 隱藏了？答案是 500 與 1500 的方向和讀段位置分布。兩者 DP/AD 完全相同，但 BAM 證據的形狀不同。

### 6.4 使用 IGV 查看相同證據

IGV（Integrative Genomics Viewer）能同時顯示 reference、coverage、reads 與候選事件。先依附錄 A 安裝符合 Windows／macOS／Linux 的桌面版，再開啟練習資料：

1. 選擇 `Genomes → Load Genome from File`，載入 `reference.fa`；`.fai` 保留在同一資料夾。不要選人類 hg38。
2. 使用 `File → Load from File` 載入 `tumor.bam`、`normal.bam` 與 `candidates.vcf.gz`，索引留在各自檔案旁。
3. 搜尋 `chrToy:450-550`，觀察 tumor 與 normal 的 coverage 和 ALT 支持。
4. 在 alignment 軌道按右鍵，選擇依 read strand 著色；點選 read 查看方向、MAPQ 與位置。不要只依顏色猜 allele。
5. 移至 `chrToy:1450-1550`，比較 ALT 是否集中在同方向、接近 read ends；再查看 `chrToy:2450-2550` 的 normal 支持。
6. 載入 `copy_number.seg`，查看 `chrToy:1-5000` 的區段訊號。它來自獨立 CN 模型，不應與本例 BAM coverage 當成同一套 CN 證據。

以上操作依 [IGV reference 載入說明](https://igv.org/doc/desktop/UserGuide/reference_genome/)與[alignment 操作文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/)整理。不同版本選單文字可能略有差異。

IGV 可能為顯示效能 downsample（抽樣顯示）讀段；畫面上可見的 read 數不一定等於完整計數。低頻 ALT 不明顯時，查看 coverage 詳細資訊與 downsampling 設定，並用上面的 BAM 計數確認。IGV 是證據瀏覽工具，不是統計驗證或 caller。

若暫時無法使用 IGV，先利用第 6.3 節的讀段統計完成案例；圖形界面則可在安裝完成後補做。

## 七、三個候選事件的整合判讀

請為每個事件記錄四欄：「目前決策」、「支持證據」、「缺少的資訊」、「下一步」。可使用的決策是：保留為研究候選、需要正交驗證、技術上可疑、需要更多資料。這些標籤不是臨床報告分級。

### 7.1 事件 A：5% VAF，有正反向讀段支持

在 chrToy:500，tumor=20/400，normal=0/200；ALT 正反方向各 10，未集中在讀段端部。假設真實研究還提供該位置為已知 hotspot 的 annotation，你會如何決定？

參考解析：相對於事件 B，A 有較一致的技術支持，可保留為後續研究候選，但還不能稱為已驗證的 somatic hotspot。需要確認分子獨立性、區域比對背景、PoN、normal 偵測能力與實際流程的驗證範圍。若結果重要或接近已驗證流程的界線，需規劃適當追加驗證。chrToy 本身沒有真實基因或 hotspot 身分，不應拿去查臨床資料庫。

### 7.2 事件 B：同樣 5%，但集中在同方向及末端

在 chrToy:1500，tumor=20/400，normal=0/200；20 條 ALT 全為同方向，且全在末端。參考解析：標記為技術上可疑，回查讀段與前處理；可考慮重新製備或其他適切方式確認，但不能只說「C>T 所以一定是 FFPE」。本例只是 FFPE-like 的偏差形狀，沒有真的模擬化學損傷。

比較 A/B 的關鍵不是「20 ALT 是否足夠」，而是這些支持是否可能共用同一種錯誤來源。若單純把 VAF≥5% 寫成保留規則，兩者都會留下。

### 7.3 事件 C：低純度中的 copy-number gain

`copy_number.seg` 在 chrToy:3000–4000 顯示 log2 ratio 約 0.485。已知合成模型假設 p=0.2、腫瘤 C=6。若不知道模型真值，你能直接把它判為低幅度 gain，或反推一定是六份拷貝嗎？

參考解析：不能僅憑相對 ratio 指定絕對 CN。需核對 purity/ploidy、正規化基準、區段長度、支持區域數、噪音與 BAF。真實資料中「amplification」的操作定義也依研究與方法而異。這裡可以確認模型展示了低純度的稀釋效果，但不是用十個人工 marker 驗證真實 amplification。

### 7.4 補充對照 D：normal 同樣有 50% VAF

chrToy:2500 在兩個樣本均約 50%。它提供 germline-like 證據，不應只因出現在腫瘤 VCF 就算 somatic。仍需核對正常來源、配對與區域品質；本例的用途是提醒你「候選檔案中的每一列，不都代表癌症特有變異」。

## 八、CNV、SV 與癌症 cohort 摘要

### 8.1 CNV：由相對讀深到區段，再到模型

CNV 分析通常先將 coverage 依區域計數，處理 GC、mappability、capture efficiency 等差異，再與正常或參考樣本比較。Segmentation 尋找相鄰區域的共同變化；最後可結合 BAF 與 purity/ploidy 模型，評估 allele-specific CN。

BAF 在此常以 informative heterozygous loci 提供 allele balance 資訊。只有總 copy ratio，不一定能看出 copy-neutral LOH（總拷貝數不變但雜合性喪失）。WES 目標區不連續、捕捉波動較大；不能直接用未校正 depth 比較兩個基因就判定 CNV。

### 8.2 SV：斷點證據與替代解釋

SV 包括缺失、重複、倒位、易位等。Split read 是一條 read 的不同部分比對到不同位置；discordant read pair 的距離、方向或染色體關係不同於預期。Caller 可整合這些證據、read depth 與局部組裝提出 breakpoint（斷點）候選。

| 觀察 | 可能支持 | 仍需排除 |
|---|---|---|
| 多條 split reads 指向相近位置 | 一致斷點 | 重複序列、多重比對、文庫嵌合 |
| 多個 pairs 的 mate 在另一染色體 | 易位候選 | 系統性 mapping 或文庫問題 |
| 區域 depth 下降並伴斷點 | 缺失候選 | 捕捉不均、GC 或 reference 差異 |

本課 single-end 資料沒有這些 paired-end/SV 證據；請勿在 toy BAM 上尋找並不存在的真實結構變異。DNA 的基因重排也不自動證明產生有表現且具功能的 RNA fusion，可能需要 RNA 或其他證據。

### 8.3 從事件表到 cohort：分母不能消失

做 cohort summary 時，保留 sample ID、事件唯一識別、過濾狀態、有效分析區域與缺失狀態。同一事件若被多個 transcript 註解，不應當成多個獨立變異。

| 摘要 | 容易忽略的分母／限制 |
|---|---|
| 某基因的變異樣本比例 | 分母應反映該基因可評估的樣本，不是把未覆蓋當陰性 |
| Tumor mutation burden（TMB） | 需定義變異集合、有效 Mb、germline/artifact 排除與平台校準 |
| Microsatellite instability（MSI） | 需方法與位點模型，不能由幾筆 indel 或高 TMB 直接替代 |
| CNV 頻率 | 需一致的可評估範圍、純度與事件定義 |
| 治療前後 VAF 變化 | 也受純度、採樣位置、CN 與覆蓋影響，不一定是克隆擴張 |

液態切片中的 cfDNA（游離 DNA）只有一部分可能來自腫瘤，稱 ctDNA。低比例、分子輸入量及克隆性造血都會影響結果；未偵測到不等於沒有腫瘤變異。這些是分析設計限制，不是單一 VAF 門檻能解決。

## 九、延伸練習：抽樣能解釋多少，不能解釋多少？

在練習資料夾執行：

```bash
python3 ../models.py
```

程式只使用 Python 標準函式庫。第一部分重算第五節的 VAF 混合模型；第二部分假設每條 read 相互獨立、真實 ALT 機率為 0.05 且無錯誤，計算至少看到 3 條 ALT 的機率：

```text
X ~ Binomial(n, 0.05)
P(X ≥ 3) = 1 − [P(X=0) + P(X=1) + P(X=2)]
```

| Depth n | 至少 3 條 ALT 的理論機率 |
|---:|---:|
| 30 | 約 18.78% |
| 100 | 約 88.17% |
| 400 | 接近 100%，程式四捨五入顯示 1.000000 |

這不是臨床 sensitivity 或 limit of detection（LOD）。真實資料有錯誤、分子重複、位置偏差，caller 也不會只用「3 條 ALT」判定。偵測極限需要適當材料、重複實驗與驗證設計；不能用上表直接聲稱「400× 保證測到 5%」。

思考題：事件 B 多定序十倍，能解決原本的末端／方向偏差嗎？解析：未必；若反覆放大同一系統性錯誤，更多 reads 不會創造獨立而正確的證據。

## 十、自我檢核與研究筆記

### 10.1 先用自己的話回答

1. Tumor-only 加上 PoN，是否等於有 matched normal？
2. 為什麼 VAF=5% 可能是 clonal，而不一定是 subclonal？
3. A/B 同樣 20/400，哪兩項 BAM 證據使判斷不同？
4. 正反向 ALT 都有，能否稱為 duplex consensus？
5. Normal=0/200 能否證明 allele 完全不存在？
6. Copy ratio 與絕對 copy number 的差異是什麼？
7. 為什麼不能把 VCF/MAF 每一列直接當成一個高可信度 somatic event？
8. 為什麼不能把 toy script 成功執行當成臨床流程驗證？

### 10.2 參考解析

1. 不等於。PoN 是多人的技術背景；matched normal 才是個案本人的參考，但本身仍有侷限。
2. 在二倍體單份 ALT、純度 10% 且全部癌細胞帶變異的模型中，VAF 即為 5%。
3. ALT 的方向與 read-end 分布；B 集中在單方向及端部。
4. 不能。Duplex 需要原始分子雙股的對應證據。
5. 不能。只代表目前讀段中未觀察到，還受抽樣與有效深度影響。
6. Ratio 是相對測量，受基準與混合影響；絕對 CN 需額外模型和證據。
7. 可能含 artifact、germline、低品質、重複 transcript 註解或尚未篩選事件。
8. 本例只有人工讀段與預設候選，未包含真實樣本差異、caller 效能或驗證材料。

### 10.3 將本課套用到自己的研究

| 檢查項目 | 你的筆記／待確認事項 |
|---|---|
| Tumor 與 normal 的來源、配對與採樣時間 | |
| 檢體處理、DNA 輸入量、純度與批次 | |
| 平台、目標區域、reference 與版本 | |
| 獨立分子／UMI／consensus 的定義 | |
| Somatic calling、filtering 與背景資源 | |
| 候選事件的 read-level 證據 | |
| CN、purity/ploidy 的假設與不確定性 | |
| 未評估區域、排除理由與驗證需求 | |

建議保留原始候選與篩選後集合、FILTER 原因、人工觀察、工具版本、資料來源及後續決策。將「技術上可信」、「生物學上有興趣」與「足以支持臨床行動」分開紀錄。

## 十一、名詞速查

| 名詞 | 本課用法 |
|---|---|
| Somatic／germline | 後天體細胞來源／生殖系來源，不是 VAF 高低分類 |
| Matched normal／tumor-only | 同人正常參考／只有腫瘤資料的分析設計 |
| VAF／CCF | allele 支持比例／帶變異的癌細胞比例，兩者不同 |
| Purity／ploidy | 腫瘤混合比例／染色體組或拷貝數背景 |
| FFPE／artifact | 固定包埋檢體／技術形成的非真實候選訊號 |
| UMI／consensus | 分子識別標記／整合同分子讀段所形成的序列 |
| PoN | 多份正常資料建立的背景資源 |
| Strand／orientation | 比對正反方向／包含 read-pair 結構的方向資訊 |
| CNV／SV | 拷貝數變化／結構變異，部分事件同時屬兩者 |
| Segmentation／BAF | 將訊號整合為連續區段／相對 allele 訊號或比例資訊 |
| MAF | 此處為 Mutation Annotation Format，不是 minor allele frequency |
| TMB／MSI | 腫瘤突變負荷／微衛星不穩定，各需合適分析方法 |
| cfDNA／ctDNA | 游離 DNA／其中腫瘤來源的 DNA |
| Orthogonal validation | 用具有不同限制或原理的方法補充驗證 |

## 附錄 A：依作業系統安裝，到第一次成功執行

### A1. 選擇操作路線與必要工具

依序完成「選作業系統 → 安裝工具 → 下載完整專案 → 產生自己的練習資料 → 執行腳本 → 核對結果」。只閱讀自己系統的安裝分支，再接共同步驟。所有資料均為合成教學資料，不要把病人資料放進這個公開專案。

| 電腦 | 安裝路線 | 之後在哪裡輸入指令 |
|---|---|---|
| Windows 11、Intel／AMD 64-bit | A2：WSL2 ＋ Ubuntu 24.04 | Ubuntu；只有安裝 WSL 使用 PowerShell |
| macOS、Apple Silicon 或 Intel | A3：Homebrew ＋官方 PLINK 1.9 | Terminal（終端機） |
| Linux、Ubuntu 24.04／相容 Debian 系統 | A4：系統套件管理員 | Linux Terminal |
| Windows ARM／Linux ARM64、其他 Linux | 先看 A4 相容性限制 | 不可直接假設 x86_64 執行檔可用 |

Windows 可由「設定 → 系統 → 關於 → 系統類型」確認處理器；Mac 可由「蘋果選單 → 關於這台 Mac」確認晶片。Linux／WSL 的 `uname -m` 若顯示 `x86_64`，是 Intel／AMD 64-bit；`aarch64` 是 ARM64。Mac 原生 Apple Silicon 終端機通常顯示 `arm64`。

| 工具 | 本次用途 | 哪堂需要 |
|---|---|---|
| Git | 下載完整教材，記錄教材版本 | 兩堂 |
| Python 3.8 以上 | 產生合成資料、自動核對；只用標準函式庫 | 兩堂 |
| Bash | 依序執行 `.sh` 腳本、連接工具 | 兩堂 |
| SAMtools | SAM/BAM 轉換、排序、索引與讀段統計 | 兩堂 |
| BCFtools | VCF 處理；第一堂另做小型 variant calling | 兩堂 |
| PLINK **1.9** | Genotype QC、PCA、親緣與 ROH | 第一堂 |
| IGV Desktop | 圖形化查看 reference、BAM、VCF、SEG | 第二堂的視覺核對 |

不需 R、Docker、Conda、GPU、付費軟體或額外 Python 套件。FastQC、aligner、Mutect2 在概念部分介紹，但本次腳本沒有呼叫它們，不必額外安裝。第二堂不使用第一堂的輸出，可以單獨操作。

請為 WSL／開發工具預留數 GB 磁碟空間並確認能連線至官方下載站與 GitHub；合成資料本身很小。安裝可能需要管理員權限，分析則不需要 `sudo`。院內電腦請先取得核准；不能安裝時請資訊人員提供合規環境，勿停用防護或繞過權限。

### A2. Windows：WSL2 ＋ Ubuntu

**步驟 1：安裝 Linux 環境。** WSL（Windows Subsystem for Linux）讓 Windows 使用 Linux 工具。本路線選 Windows 11 與 Ubuntu 24.04 LTS。Microsoft 簡易指令也支援 Windows 10 2004、build 19041 以上；作業系統維護狀態與院內政策另行確認。[Microsoft 安裝說明](https://learn.microsoft.com/en-us/windows/wsl/install)

在開始選單搜尋 PowerShell，按右鍵「以系統管理員身分執行」，先查已安裝及可下載的發行版：

~~~powershell
wsl --list --verbose
wsl --list --online
~~~

尚未安裝者，確認線上清單有 `Ubuntu-24.04` 後執行：

~~~powershell
wsl --install -d Ubuntu-24.04
~~~

依提示重新開機，從開始選單開啟 Ubuntu 24.04，建立 Linux 帳號與密碼；它們可以不同於 Windows 帳號。輸入密碼不顯示字元是正常現象。已有可用 Ubuntu 不必重裝，尤其不要使用 `wsl --unregister`，這會刪除該環境與資料。

**步驟 2：確認 WSL2。** 在 PowerShell 再執行 `wsl --list --verbose`，Ubuntu 的 `VERSION` 應為 `2`。若為 `1`，請先確認硬體虛擬化與政策允許，再執行：

~~~powershell
wsl --set-version Ubuntu-24.04 2
~~~

發行版名稱必須與清單一致；若清單顯示 `Ubuntu`，就改用 `Ubuntu`。

**步驟 3：改在 Ubuntu 視窗安裝工具。** PowerShell 常見提示為 `PS C:\...>`；Ubuntu 通常為 `使用者@電腦:~$`。下面指令不是貼在 PowerShell、CMD、Git Bash 或 Python 的 `>>>`。

~~~bash
uname -m
sudo apt update
sudo apt install -y git python3 samtools bcftools
~~~

`apt update` 更新套件清單，`apt install` 安裝工具；`sudo` 要求剛設定的 Linux 密碼。第一堂另外安裝：

~~~bash
sudo apt install -y plink1.9
plink1.9 --version
~~~

PLINK 指令以 Ubuntu 24.04 的 x86_64 為主要路線；ARM 電腦或找不到套件請看 A4。不要改裝 PLINK 2 當成同一工具。完成後跳到 A5，不需再裝 Windows 版 Python／SAMtools。

### A3. macOS：Homebrew ＋ PLINK 1.9

**步驟 1：打開 Terminal。** 按 Command＋空白鍵，搜尋 Terminal，再查看系統：

~~~bash
sw_vers
uname -m
~~~

先核對 [Homebrew 支援範圍](https://docs.brew.sh/Installation)。舊 macOS／Intel Mac 的支援程度不同，安裝若提示不支援，應請資訊人員安排相容工具或核准的 Linux 環境，勿強行覆寫系統。

**步驟 2：安裝 Homebrew。** 它是管理命令列軟體的工具。先執行 `brew --version`；已有版本就跳過重裝。否則前往 [Homebrew 官網](https://brew.sh/)，確認來源與權限後，在 Terminal 執行官方安裝指令：

~~~bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
~~~

這行會下載並執行安裝程式，請閱讀提示再同意。若要求 Command Line Tools，依提示完成，或執行 `xcode-select --install` 並於系統視窗安裝；不用下載完整 Xcode。

安裝結束，**照畫面 Next steps 設定 shellenv**，讓終端機找到 `brew`。若目前視窗仍找不到，Apple Silicon 的標準安裝位置可執行：

~~~bash
eval "$(/opt/homebrew/bin/brew shellenv)"
~~~

Intel Mac 的標準位置則用：

~~~bash
eval "$(/usr/local/bin/brew shellenv)"
~~~

只選符合安裝位置的一段。`eval` 在此載入 Homebrew 的環境設定；這一行僅影響目前視窗，仍應依 Next steps 完成啟動設定。再用 `brew --version` 確認。

**步驟 3：安裝兩堂共用工具。**

~~~bash
brew install git python samtools bcftools
~~~

`python` 是套件名稱，執行時仍叫 `python3`。不要在 `brew install` 前加 `sudo`。套件名稱見 [SAMtools formula](https://formulae.brew.sh/formula/samtools)與 [BCFtools formula](https://formulae.brew.sh/formula/bcftools)。

**步驟 4：第一堂另裝 PLINK。** 第二堂可以跳過。於 [PLINK 1.9 官方頁](https://www.cog-genomics.org/plink/1.9/)選 macOS 64-bit stable，不要選 PLINK 2。以下固定使用 2026-09-27 版本；本次實際檢查它是包含 x86_64 與 arm64 的 Universal binary，Intel 與 Apple Silicon 可用同一檔案。

~~~bash
mkdir -p "$HOME/bioinfo-tools/plink19-20260927"
cd "$HOME/bioinfo-tools/plink19-20260927"
curl -fL \
  https://s3.amazonaws.com/plink1-assets/plink_mac_20260927.zip \
  -o plink.zip
unzip -n plink.zip
file plink
./plink --version
~~~

`mkdir -p` 建立工具目錄；`curl -fL` 下載並在 HTTP 錯誤時失敗；`unzip -n` 解壓但不覆蓋既有檔案；`file` 顯示程式架構。每一步無錯誤才繼續。版本應顯示 PLINK v1.9.0。本例不用一律加裝 Rosetta；如果另用 Intel-only 舊版，才需核對 [Apple Rosetta 說明](https://support.apple.com/en-us/102527)。

為了與 Ubuntu 一樣使用 `plink1.9` 命令，把已確認來源的程式放到個人工具目錄。若目的地已有其他版本，先備份或改名，不要直接取代。

~~~bash
mkdir -p "$HOME/.local/bin"
install -m 755 ./plink "$HOME/.local/bin/plink1.9"
export PATH="$HOME/.local/bin:$PATH"
plink1.9 --version
~~~

`install -m 755` 複製並賦予執行權限；`PATH` 是終端機搜尋程式的目錄清單。`export` 只在目前視窗與子程式有效，**每次新開 Terminal 執行第一堂前，再執行 `export PATH="$HOME/.local/bin:$PATH"`**。熟悉 shell 者可自行寫入個人啟動檔。不要只設定 alias，因為子腳本未必能使用。

若 macOS 阻擋下載程式，確認官方來源後依「隱私權與安全性」提示或洽資訊人員處理，不要全域停用 Gatekeeper。完成後前往 A5。

### A4. Linux：套件安裝與相容性

Linux 不需安裝 WSL 或 Homebrew。打開 Terminal，確認發行版與 CPU：

~~~bash
cat /etc/os-release
uname -m
~~~

以下以 **Ubuntu 24.04 LTS、x86_64** 為基準。Debian 可使用相同套件管理命令，但套件版本與架構須另確認。Fedora、Rocky、Arch 不是 apt 系統，請由資訊人員用該系統的套件管理方式提供 A1 工具，再從 A5 檢查，不要直接照貼 apt。

~~~bash
sudo apt update
sudo apt install -y git python3 samtools bcftools
~~~

第一堂另外執行：

~~~bash
sudo apt install -y plink1.9
plink1.9 --version
~~~

若 `Unable to locate package plink1.9`，先查拼字、`apt update` 是否成功及發行版。Ubuntu 的套件位於 **universe**；只有院內允許新增來源時才執行：

~~~bash
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo apt install -y plink1.9
~~~

這段新增來源只適用 Ubuntu，不適用 Debian。伺服器沒有 sudo 者，請管理員安裝或啟用既有環境，不要修改系統權限。

**ARM64 限制：** [Ubuntu 24.04 的 plink1.9 套件頁](https://packages.ubuntu.com/en/noble/plink1.9)目前沒有 ARM64 套件。Windows ARM 的 WSL、ARM Linux 不應下載 x86_64 程式硬跑。若 Python、SAMtools、BCFtools 可用，仍可完成第一堂定序部分及第二堂命令列練習；array 部分請資訊人員提供經確認的 PLINK 1.9 ARM 編譯版，或改用核准的 x86_64 Ubuntu 電腦／伺服器。本教材不宣稱已驗證 ARM Linux 的 array 流程。使用遠端主機時，安裝與腳本都在遠端執行，供 IGV 使用的結果需另下載到桌面電腦。

### A5. 共同步驟：確認工具與下載專案

Windows 在 Ubuntu，macOS／Linux 在 Terminal 執行。後文 `.sh` 都用 `bash` 呼叫，因此 Mac 預設是 zsh 也能操作。

~~~bash
git --version
python3 --version
bash --version
samtools --version
bcftools --version
~~~

每行應印出版本，不是 `command not found`；SAMtools／BCFtools 顯示多行編譯資訊正常。Python 至少 3.8，因第二堂使用 `math.comb`。第一堂加跑 `plink1.9 --version`，確認是 PLINK 1.9／1.90 系列，不是 2.x 或 PuTTY 的同名連線工具。

**第一次下載：** 假設家目錄尚無 `ClinicalBioinfoCourse` 資料夾：

~~~bash
cd ~
git clone https://github.com/godkin1211/ClinicalBioinfoCourse.git
cd ClinicalBioinfoCourse
pwd
ls
git rev-parse --short HEAD
~~~

公開專案不需 GitHub 帳號或 token。`cd ~` 回到目前使用者的家目錄；WSL 的家目錄是 `/home/帳號`，不是 `C:\Users\帳號`。`git clone` 下載整個專案，`pwd` 顯示位置，`ls` 列出內容。應看到 `lessons`、`demos`、`scripts`、`README.md`。最後一行是教材版本識別碼，請保留。

**已下載過：** 不要再次 clone。先進入既有專案查看狀態：

~~~bash
cd ~/ClinicalBioinfoCourse
git status --short
~~~

若顯示自己的修改，先保留並詢問協助；不要執行 `reset --hard`。確認沒有要保留的未完成修改，再更新：

~~~bash
git pull --ff-only
~~~

`--ff-only` 只允許快轉更新；若失敗請停下，勿強制覆蓋。舊專案若叫 `KCGMH_Cource_Series` 也可繼續使用，只要把後面每個 `~/ClinicalBioinfoCourse` 換成實際位置，不必搬動或刪除舊資料。

只能用瀏覽器時，在 GitHub 選 `Code → Download ZIP`，解壓完整內容，放到家目錄並命名 `ClinicalBioinfoCourse`。ZIP 沒有 Git 紀錄，不能執行 `git pull`、`git rev-parse`，請改記下載日期。Windows 可於 Ubuntu 執行 `explorer.exe ~` 開啟 Linux 家目錄，再以檔案總管複製解壓資料夾。無網路時請講師經核准管道提供完整副本與版本資訊。

### A6. 看懂指令與路徑，再開始分析

Script（腳本）是依序執行的指令檔：`.py` 用 `python3`；`.sh` 用 `bash`。不要雙擊，也不要貼進 Python 的 `>>>`。本教材直接呼叫 Bash，不需先對腳本做 `chmod +x`。

| 寫法 | 意思與用途 |
|---|---|
| `cd 目錄` | 切換目前目錄，失敗就先停止，不執行下一行 |
| `.`／`..` | 目前目錄／上一層；在練習目錄內，`../prepare.sh` 才會指到上一層腳本 |
| `ls`／`head -n 5 檔案` | 列出檔案／讀前五行，核對位置與欄名 |
| `# 說明` | 註解；不要連終端機提示符號一起複製 |
| `>`／`>>` | 把輸出寫到檔案並覆蓋／附加到檔案末尾 |
| `2>&1` | 把錯誤訊息與一般輸出保存在同一份 log |
| 行尾 `\` | 指令接續下一行，後面不可留空白 |

路徑有空白時加雙引號，例如 `cd "/Users/你的帳號/My Courses/ClinicalBioinfoCourse"`。看到 `Error`、`Traceback`、`command not found` 先停止；不能只因為後面有檔案就認為成功。

以下使用新的 `practice-local01`。專案若已有 `practice01`，那是既有示範，不要重用。產生器拒絕覆蓋任何已存在目錄；重做請換 `practice-local02`，並同步修改下一行的 `cd`。個人 `practice-local*` 目錄已加入 Git 忽略規則。分析腳本會取代同名輸出，兩次比較應各用一個新目錄。

### A7. 第二堂：準備 BAM、檢查證據、驗證結果

**步驟 1：進入本堂腳本目錄。** 不需要第一堂的輸出或 PLINK：

~~~bash
cd ~/ClinicalBioinfoCourse/demos/lesson-02-somatic
pwd
ls generate.py prepare.sh audit_reads.py verify.py models.py
~~~

五個檔案都列出才繼續。`generate.py` 造出合成資料；`prepare.sh` 轉檔與索引；`audit_reads.py` 從讀段重算證據；`verify.py` 檢查答案；`models.py` 列出 VAF、純度、CN 與抽樣的簡化模型。

**步驟 2：產生新練習資料。**

~~~bash
python3 generate.py practice-local01
cd practice-local01
pwd
ls
~~~

成功時會印出 `Created ...` 與 A/B、D 的預期比例。應出現 `reference.fa`、`tumor.sam`、`normal.sam`、`candidates.vcf`、`copy_number.seg`。第一堂與第二堂各自目錄下同名的 `practice-local01` 是不同資料夾，內容不可互換。

這些 SAM 的位置、VCF 的候選與 FILTER 都是人工設定。`prepare.sh` 不執行 aligner、Mutect2 或 CN caller；SEG 來自獨立的模型，不能當成 BAM 深度推估結果。

**步驟 3：執行資料整理。**

~~~bash
bash ../prepare.sh > prepare.run.log 2>&1
echo $?
tail -n 12 prepare.run.log
ls *.bam *.bai *.tbi *.tsv
~~~

`bash` 執行上一層的腳本，`> prepare.run.log 2>&1` 保留一般與錯誤輸出。等待提示符號回來後，緊接的 `echo $?` 應為 0；非 0 先停下查 log。成功時 log 可能很短，不能用文字多寡判斷成敗。

腳本為 reference 建 `.fai`，把兩份 SAM 轉成排序 BAM、建立 `.bai`、執行 quickcheck 與 flagstat；再壓縮 VCF、建立 `.tbi`、查詢欄位，最後把 BAM 讀段交給 `audit_reads.py` 重新統計證據。

**步驟 4：確認檔案可讀及樣本正確。**

~~~bash
samtools quickcheck -v tumor.bam normal.bam
echo $?
bcftools query -l candidates.vcf.gz
cat tumor.evidence.tsv
cat normal.evidence.tsv
cat candidates.tsv
~~~

quickcheck 正常時通常**沒有輸出**且退出碼 0；它檢查基本結構，不代表每條 read 都可信。VCF 樣本名稱依序應是 `TUMOR`、`NORMAL`，不要因欄位位置就自行猜測。

| 位點 | 腫瘤 ALT／深度 | 正向／反向 ALT | 端部 ALT | 正常 ALT／深度 |
|---|---:|---:|---:|---:|
| chrToy:500 | 20／400 | 10／10 | 0 | 0／200 |
| chrToy:1500 | 20／400 | 20／0 | 20 | 0／200 |
| chrToy:2500 | 200／400 | 100／100 | 0 | 100／200 |

前三列都應出現在證據表。500 與 1500 都是 VAF 5%，但後者的 ALT 完全單向且接近讀段末端。這是教材設計的可疑模式，不應只憑方向偏差就宣告真偽。正常樣本在 2500 的支持則提醒你注意 germline／normal evidence，而非把腫瘤裡所有變異都當 somatic。

**步驟 5：執行自動核對。**

~~~bash
python3 ../verify.py . > verification.txt 2>&1
echo $?
cat verification.txt
~~~

應為退出碼 0，並顯示以下完整訊息（畫面自動換行正常）：

~~~text
PASS: BAM-derived counts, bias patterns, VCF samples/flags, CN/VAF models, indexed artifacts
~~~

`.` 指目前目錄。程式確認 BAM 衍生計數、方向／端部模式、VCF 樣本與標記、模型及索引檔；**不是**驗證 somatic caller 的敏感度或臨床效能。

**步驟 6：執行模型與保存紀錄。**

~~~bash
python3 ../models.py > models.txt
echo $?
cat models.txt
python3 --version > versions.txt
samtools --version >> versions.txt
bcftools --version >> versions.txt
uname -a >> versions.txt
git rev-parse HEAD > course-commit.txt
~~~

`models.py` 只用 Python 標準函式庫，不需 pip。`low_purity` 的預期 VAF 為 0.050000，`gain_one_mutant_copy` 為 0.071429，`CN6 purity=0.2` 的 log2ratio 約 0.485427；這些是條件指定後的計算，不是從病人資料反推的估計。ZIP 使用者跳過 Git 一行，另記下載日期。保留輸入、版本、`prepare.run.log`、`verification.txt`、`models.txt` 及所有結果。

### A8. 三種系統的 IGV 安裝與啟動

IGV 是桌面圖形程式，不是另一個 caller。命令列 PASS 與 IGV 載入成功是兩個不同檢查；GUI 暫不可用時可先完成證據表判讀。

到 [IGV 官方下載頁](https://igv.org/doc/desktop/DownloadPage/)選與作業系統、CPU 相符的穩定版，優先使用 **包含 Java runtime** 的套件。不要為本課改裝 beta；若下載不含 Java 的版本，按當版需求另備 Java。核對時官方說明為 IGV 2.19.1 起需 Java 21 以上；下載頁改版時以當版文件為準。

**Windows：** 在 Windows 瀏覽器下載 Windows 安裝包，依精靈選目的地並完成，從開始選單開啟 IGV。不是在 Ubuntu 執行 `.exe`。若電腦是 Windows ARM，先確認當版 Windows 套件與 Java 支援該架構，不把 x64 支援視為 ARM 原生支援。院內禁止安裝時請資訊人員部署。

**macOS：** 在下載頁選符合 Apple Silicon／Intel 的 Mac app，開啟下載的封裝；若為 ZIP 先解壓，把 IGV.app 拖到 Applications，再從 Applications 啟動。若出現安全提示，確認來源後依系統允許的操作或洽資訊人員處理，不要全域關閉安全機制。

**Linux 桌面：** x86_64 使用官方 Linux 套件（包含 Java），於檔案管理員解壓，開啟解壓目錄中的終端機，確認 `igv.sh` 存在，再執行：

~~~bash
pwd
ls igv.sh
bash igv.sh
~~~

需有可用的桌面顯示環境。官方 Linux 包附的是 x64 Java；ARM64 不可直接使用，應選「Command line IGV for all platforms」並由資訊人員安裝相容架構的 Java 21 以上，確認 `java -version` 後再啟動。這個名稱仍是啟動桌面 GUI 的方式，不代表能在沒有顯示環境的 SSH 視窗直接顯示。遠端／無桌面的伺服器可完成命令列分析，再把本課合成結果下載到本機桌面 IGV。

啟動後於 About 對話框（依系統在 Help 或應用程式選單）記下版本。下一步不需下載 hg38；使用本課 `chrToy`。

### A9. 把結果交給 IGV，完成視覺核對

**步驟 1：找到結果資料夾。** 在目前練習目錄執行 `pwd`。Mac 可用 `open .` 在 Finder 開啟；Linux 桌面可用檔案管理員前往該路徑；Windows 在 Ubuntu 用：

~~~bash
explorer.exe .
~~~

它會用 Windows 檔案總管開啟 WSL 的目前資料夾。若 IGV 無法直接讀 WSL 路徑，透過檔案總管把下面整組合成檔案複製到一個新的 Windows 資料夾，例如 `Documents\ClinicalBioinfoLesson02`，不要只複製 BAM。不要在分析尚未結束時複製。

| 一起保留的檔案 | 理由 |
|---|---|
| `reference.fa`、`reference.fa.fai` | 人工 reference 與位置索引 |
| `tumor.bam`、`tumor.bam.bai` | 腫瘤讀段與索引 |
| `normal.bam`、`normal.bam.bai` | 正常讀段與索引 |
| `candidates.vcf.gz`、`candidates.vcf.gz.tbi` | 壓縮候選檔與 tabix 索引 |
| `copy_number.seg` | 人工設計的 CN 區段示意 |

這裡總共 **9 個檔案**。保持檔名相配；不要單獨改名 `tumor.bam` 卻不改 `tumor.bam.bai`。`.vcf.gz` 不需自行解壓。

**步驟 2：載入正確 reference。** 在 IGV 選 `Genomes → Load Genome from File`，選 `reference.fa`。同目錄保留 `.fai`；成功時應能選到 `chrToy`，不是 chr1 或 hg38。如果 GUI 選單文字略不同，以當版 reference 載入功能為準。

**步驟 3：載入結果。** 選 `File → Load from File`，載入 `tumor.bam`、`normal.bam`、`candidates.vcf.gz`、`copy_number.seg`。索引不需當成獨立軌道載入，但必須在旁邊。應出現兩個 alignment／coverage 軌道、候選軌道與 CN 區段。

**步驟 4：逐位點查看。** 搜尋 `chrToy:450-550` 並按 Enter。放大到可見鹼基，點選／移到 coverage 及 read 以查看實際數值；在 alignment 軌道右鍵選 `Color alignments by → Read strand`（名稱依版本可能略異）。不要把不同顯示配色直接當作固定生物學意義。

接著查 `chrToy:1450-1550`，比較 ALT 方向與讀段末端位置；查 `chrToy:2450-2550`，看 normal 也支持 ALT。最後查 `chrToy:1-5000`，應見 3000–4000 的 SEG 約 0.485427；該模型與本例 BAM depth 獨立，不要把它說成同一份資料算出的 CN 結果。

**步驟 5：定義完成。** 你應能指出：500 與 1500 同為 5% VAF 但支持模式不同；2500 有 normal evidence；CN 軌道是獨立示意。若畫面 read 數比表格少，先檢查 downsampling（抽樣顯示）設定，回查完整 BAM 統計；螢幕可見數量不是深度的唯一依據。保存座標與判讀筆記，截圖只能補充，不能取代 BAM／VCF 與執行紀錄。

### A10. 第二堂常見問題

| 現象 | 檢查與處理 |
|---|---|
| `command not found` | 先查是否在正確終端機，再以 `command -v python3`、`command -v samtools`、`command -v bcftools` 找路徑 |
| `FileExistsError` | 改 `practice-local02`，並同步更改 `cd`；不要覆蓋既有練習 |
| 找不到 `reference.fa`／`../prepare.sh` | 用 `pwd`、`ls` 確認正在第二堂的練習子目錄 |
| `$'\r': command not found` | 腳本換行格式錯誤；用文字編輯器存為 UTF-8／LF，或重新取得教材 |
| 沒有 BAM 或索引 | 先查 `prepare.run.log` 的第一個錯誤，不直接跳到 IGV |
| `math.comb` 不存在 | 檢查 Python 是否至少 3.8、`python3` 是否指到舊環境 |
| 程式說只支援 150M | 可能用了其他資料；本例不是通用 pileup 工具 |
| IGV 空白／找不到 chrToy | 先載入本課 reference，再放大到指定座標，不用 hg19/hg38 |
| 找不到 index | 核對完整 9 檔、同目錄與檔名；索引要配對本次 BAM／VCF |
| IGV 不能啟動／Java 錯誤 | 確認套件的 OS、CPU、Java 版本；Linux 確認桌面環境；優先用官方附 Java 套件 |
| 顯示 read 數不足 | 檢查 downsampling 與縮放，用 `*.evidence.tsv` 比較完整計數 |
| 沒有 sudo／管理員權限 | 使用資訊人員核准環境；可以先做輸出表判讀，不繞過政策 |

求助請提供系統／CPU、版本、`pwd`、完整命令、第一個錯誤及合成資料的 log；不要提供病人資料、token 或密碼。每次重跑若改參數，另建新的練習目錄保存差異。

## 附錄 B：實作邊界與延伸閱讀

本教材的 SAM、VCF 與 CN 區段都是人工設計；BAM 證據統計與模型計算會實際執行，但不代表已完成 somatic discovery。IGV 用於視覺核對，與正交驗證不同。欲處理真實資料，需依研究目標選定相容、可重現且經過適當驗證的流程。

- [Mutect2](https://gatk.broadinstitute.org/hc/en-us/articles/360037593851-Mutect2)：somatic short-variant calling 的工具案例。
- [GATK somatic workflow](https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2)：方向性、污染與過濾步驟。
- [BCFtools](https://samtools.github.io/bcftools/bcftools.html)：VCF 查詢與格式操作。
- [IGV alignment 文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/)：讀段與 coverage 的顯示限制。
- [IGV paired-end 文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/paired_end_alignments/)：配對方向與結構變異證據。

安裝文件核對日期：2026-09-30。實際測試環境、驗證內容與未測試項目見[第二堂示範說明](../demos/lesson-02-somatic/README.md)。
