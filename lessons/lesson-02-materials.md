# 癌症體細胞基因體分析：從定序證據到可信的候選事件

`講師`: OO醫院精準醫學核心實驗室組長邱XX

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

本練習不需要第一堂的輸出。在 Ubuntu／WSL 執行以下 Bash 指令；若專案路徑不同，只修改第一行：

```bash
cd ~/KCGMH_Cource_Series/demos/lesson-02-somatic
python3 generate.py practice01
cd practice01
bash ../prepare.sh
```

`practice01` 必須是新資料夾；產生器拒絕覆蓋既有資料。若重做，改成 `practice02`。`prepare.sh` 重跑會取代同名分析輸出，重要版本應分開保存。

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

IGV（Integrative Genomics Viewer）能同時顯示 reference、coverage、reads 與候選事件。先依附錄安裝 Windows 桌面版，再開啟練習資料：

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

## 附錄 A：Windows 軟體安裝與課前檢查

### A1. 需要哪些工具？

| 工具 | 執行位置 | 用途 |
|---|---|---|
| WSL2 Ubuntu | Windows 上的 Linux 環境 | 執行 Bash 與命令列工具 |
| Python 3 | Ubuntu | 產生資料、核對讀段、計算模型；不需額外 pip 套件 |
| SAMtools | Ubuntu | SAM/BAM 排序、索引與資料讀取 |
| BCFtools | Ubuntu | VCF 格式檢查、壓縮索引與查詢 |
| IGV Desktop | Windows | 查看 reference、BAM、VCF、CN 區段 |

本課不需要 PLINK、R、Conda、Docker 或 GPU。GATK/Mutect2 僅作分析原理案例，不在本次操作中執行，因此不要求安裝。準備環境前確認院內權限；不得為安裝工具繞過資訊安全限制。

### A2. 安裝 WSL2 Ubuntu

已完成第一堂安裝者可略過。Windows 11，或符合 Microsoft 簡易安裝需求的 Windows 10，可在系統管理員 PowerShell 執行：

```powershell
wsl --install -d Ubuntu
```

依提示重新開機，開啟 Ubuntu 並設定 Linux 帳號與密碼。密碼輸入時不顯示字元是正常現象。在 PowerShell 檢查：

```powershell
wsl --list --verbose
```

Ubuntu 的 VERSION 應為 2；若為 1，先確認硬體、虛擬化與政策允許，再依實際發行版名稱設定：

```powershell
wsl --set-version Ubuntu 2
```

簡易指令適用 Windows 10 version 2004、build 19041 以上或 Windows 11；作業系統維護狀態與院內規範另行確認。安裝與疑難排解依 [Microsoft 官方文件](https://learn.microsoft.com/en-us/windows/wsl/install)。

### A3. 安裝命令列工具

以下在 **Ubuntu**，不是 PowerShell 執行：

```bash
sudo apt update
sudo apt install -y python3 samtools bcftools
python3 --version
samtools --version
bcftools --version
```

不需要 `pip install`。Ubuntu 套件版本可能不同於本教材測試環境，請保留版本資訊；需要指定版本時應由研究流程統一管理，而非自行混用多個安裝來源。

### A4. 放置完整教材並測試

先在 Windows 解壓完整專案。假設位置是 `C:\Users\你的帳號\Downloads\KCGMH_Cource_Series`，且 Ubuntu 尚未有該資料夾，可在 Ubuntu 執行：

```bash
cp -r "/mnt/c/Users/你的帳號/Downloads/KCGMH_Cource_Series" ~/KCGMH_Cource_Series
cd ~/KCGMH_Cource_Series/demos/lesson-02-somatic
python3 generate.py preclass01
cd preclass01
bash ../prepare.sh
python3 ../verify.py .
python3 ../models.py
```

請將「你的帳號」換成實際值。若第一堂已複製專案，不要再次執行整個 `cp -r` 而產生巢狀資料夾；先確認第二堂的 `demos/lesson-02-somatic` 已更新進去。`preclass01` 已存在時換一個新名稱。

`verify.py` 應顯示 PASS；它核對合成輸出的預期值，不驗證 somatic caller 效能。保存版本：

```bash
python3 --version > versions.txt
samtools --version >> versions.txt
bcftools --version >> versions.txt
```

### A5. 安裝 Windows IGV Desktop

1. 開啟 [IGV 官方下載頁](https://igv.org/doc/desktop/DownloadPage/index.html)，選擇與 Windows／CPU 架構相符的桌面版本。
2. 優先使用包含 Java runtime 的 Windows 安裝包，依安裝程式提示完成。若改用不含 Java 的套件，依當版官方要求安裝相符 Java；目前文件標示自 IGV 2.19.1 起需 Java 21 或以上。
3. 啟動 IGV，確認可開啟本機檔案。記下 Help／About 中的版本供紀錄。
4. 按正文第 6.4 節載入本例 reference 與資料，不需要下載人類全基因體。

如果 Windows IGV 不便直接讀 WSL 路徑，可先在目前的練習資料夾執行 `explorer.exe .`，透過檔案總管複製所需檔案至新的 Windows 資料夾。需一起複製 `reference.fa/.fai`、兩份 `.bam/.bam.bai`、`candidates.vcf.gz/.tbi` 與 `copy_number.seg`；不要只複製 BAM 而遺漏索引。

你也可以在 Windows 檔案總管使用 `\\wsl.localhost\Ubuntu\home\你的Linux帳號\...` 找到資料；發行版與帳號依實際環境調整。只使用本課合成檔案；不得將院內病人檔案上傳至未核准網站。

### A6. 常見問題

| 現象 | 檢查方式 |
|---|---|
| `command not found` | 確認在 Ubuntu，且已完成 apt 安裝 |
| `FileExistsError` | 產生器保護既有資料；改用新練習資料夾 |
| 找不到 `../audit_reads.py` | 確認在 `lesson-02-somatic` 下產生的練習資料夾 |
| IGV 空白或沒有 chrToy | 載入本課 reference，不是人類 reference；縮放到指定座標 |
| IGV 看見的 read 數比 DP 少 | 可能 downsampling；回查完整 BAM 計數與顯示設定 |
| IGV 找不到索引 | BAM/BAI、VCF.gz/TBI 需一起複製並保持相符名稱 |
| Python 說只支援 150M | 你可能用了其他資料；本腳本不是通用 pileup 工具 |
| 腫瘤與正常顛倒 | 先查 read group 的 SM 與 VCF 的樣本名稱 |
| 沒有管理員權限 | 洽資訊部門或使用核准環境；可先做表格判讀 |

## 附錄 B：實作邊界與延伸閱讀

本教材的 SAM、VCF 與 CN 區段都是人工設計；BAM 證據統計與模型計算會實際執行，但不代表已完成 somatic discovery。IGV 用於視覺核對，與正交驗證不同。欲處理真實資料，需依研究目標選定相容、可重現且經過適當驗證的流程。

- [Mutect2](https://gatk.broadinstitute.org/hc/en-us/articles/360037593851-Mutect2)：somatic short-variant calling 的工具案例。
- [GATK somatic workflow](https://gatk.broadinstitute.org/hc/en-us/articles/360035531132--How-to-Call-somatic-mutations-using-GATK4-Mutect2)：方向性、污染與過濾步驟。
- [BCFtools](https://samtools.github.io/bcftools/bcftools.html)：VCF 查詢與格式操作。
- [IGV alignment 文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/)：讀段與 coverage 的顯示限制。
- [IGV paired-end 文件](https://igv.org/doc/desktop/UserGuide/tracks/alignments/paired_end_alignments/)：配對方向與結構變異證據。

文件核對日期：2026-09-13。實際測試環境、驗證內容與未測試項目見[第二堂示範說明](../demos/lesson-02-somatic/README.md)。
