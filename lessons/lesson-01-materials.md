# 從 SNP Array 到 WES/WGS：基因體資料分析入門

`講師`: OO醫院精準醫學核心實驗室組長邱XX

本教材適合臨床醫師、臨床工作者及初次接觸基因體資料分析的研究人員。你不需要預先具備程式設計經驗；閱讀時可先理解資料與分析結果，再依指令完成練習。

這堂課將帶你沿著兩條路徑認識基因體分析：一條從 SNP array 的探針訊號走到基因型與區域分析，另一條從定序讀段走到比對檔與變異。重點是理解資料如何產生、分析方法依賴哪些假設，以及結果是否有足夠證據支持，而不是個別變異的致病性分類或檢測報告解讀。所有操作使用合成資料，不包含病人資訊，也不能用來驗證臨床檢測效能。

## 教材使用方式

你可以依序閱讀概念、操作練習及結果解析。第一次接觸指令時，不必記住所有參數；先確認每一步讀入什麼、產生什麼，以及輸出能回答哪個問題。若想跟著操作，請先完成附錄 A 的安裝；暫時無法安裝，也可以利用文中的結果表完成判讀練習。

| 主題 | 你將學會什麼 |
|---|---|
| 一、研究問題與平台選擇 | 選平台並說明需要保留的資料 |
| 二、技術與資料格式 | 辨認訊號、基因型、比對與變異檔 |
| 三、Array 分析與 QC | 解釋 missingness、HWE、親緣與 PCA |
| 四、Array 實作與情境練習 | 找出一個樣本問題與一個位點問題 |
| 五、WES/WGS 分析 | 串接 FASTQ、BAM、VCF 與 QC |
| 六、整合判讀與區域分析 | 區分 ROH、CNV 與序列變異證據 |
| 七、自我檢核與研究應用 | 檢查理解程度，整理自己的分析需求 |

完成後，你應能選擇適合研究問題的技術、描述兩條資料流程、讀懂基本檔案與 QC 指標，並知道何時應暫停下游推論、回到原始證據。

閱讀與操作時，建議在筆記中保留三欄：「我的觀察」、「支持這項觀察的檔案或數值」、「還需要確認的資訊」。這能幫助你區分已知事實與待驗證的推論。

## 一、由研究問題選擇資料平台

### 1.1 研究案例：一份檢體能回答哪些問題？

研究團隊有一組心血管疾病病例與對照，希望回答：「常見變異是否與疾病相關？樣本是否存在重複或親緣關係？是否有罕見編碼變異？是否出現較大的拷貝數改變？」

這四個問題需要的測量方式、解析度、樣本數及統計方法不同。選擇平台前，你需要先確定想找的是哪一類變異，或想檢查哪一種資料特性。採用涵蓋範圍最大的技術，也不等於自動回答所有問題。

| 平台 | 測量方式 | 適合切入的問題 | 重要限制 |
|---|---|---|---|
| SNP array（單核苷酸多型性晶片） | 探針測量預設位點的等位基因訊號 | 常見變異、族群結構、親緣、ROH；有強度資訊時可分析部分 CNV | 受探針位置、密度與設計族群影響，不能全面找新序列變異 |
| Panel（目標基因套組） | 定序選定基因或區域 | 聚焦特定基因集合的研究 | 未涵蓋區域通常無法評估，版本間目標區不同 |
| WES（全外顯子定序） | 捕捉並定序外顯子等設計目標 | 編碼區 SNV、小型 indel 等 | 捕捉效率不均，非編碼區與部分外顯子仍可能不足 |
| WGS（全基因體定序） | 不以外顯子捕捉限制定序範圍 | 更廣的序列變異、部分 CNV/SV 分析 | 重複序列與複雜區域仍困難；不同變異需要不同演算法 |

SNV 是單一鹼基的序列差異；SNP 通常指族群中的單核苷酸多型性，實務用語未必嚴格區分頻率。Indel 是短片段插入或缺失；CNV 是一段 DNA 的拷貝數變化；SV 是較大型的結構變異，例如倒位或易位。不要把所有變異都當成同一種 caller 可以解決。

### 1.2 練習：為問題選擇資料

請先不看解析，為以下需求各選一個資料來源，並寫下選擇理由：

1. 比較病例與對照的常見 SNP。
2. 尋找罕見的編碼區變異。
3. 探索非編碼區的序列變異。
4. 確認兩份資料是否可能來自同一個人。

參考解析：可分別從 array、WES、WGS、既有高品質 genotype 資料切入。這不是唯一答案；還要考慮目標區域的覆蓋、成本、樣本數與既有資料。例如，檢查重複樣本未必需要重新定序，既有且足夠的高品質 genotype 可能已能提供線索。

本節重點：面對分析結果，先問「它來自什麼訊號、經過哪些假設算出來」，再判斷它能回答什麼問題。

## 二、從測量訊號到檔案

### 2.1 SNP array：連續訊號變成離散基因型

Probe（探針）是設計用來辨識特定位點的短序列。儀器取得 fluorescence intensity（螢光強度），再經背景處理與 normalization（正規化），減少技術尺度差異。Genotype calling 依兩種等位基因訊號的群聚位置，推估 AA、AB、BB 或無法判定。

```text
平台原始訊號（例如 IDAT 或 CEL；依廠牌／晶片而異）
  → 背景處理、正規化、使用適當 manifest／cluster reference
  → genotype calls + 品質分數 + 強度衍生資訊
  → 樣本與位點 QC
  ├─ genotype → PLINK → PCA、親緣、ROH 等
  └─ intensity／BAF／LRR → 區域分段與 CNV 評估
```

Manifest 是探針身分、位置及設計資訊；cluster reference 是用來判定基因型群聚的參考。不同平台不可任意混用。PLINK 不會直接把所有 IDAT/CEL 轉成可靠 genotype；原始訊號處理需要相容的平台流程。

Hard call 是把不確定性壓縮成 AA／AB／BB 等單一判定。沒有被保留下來的強度資訊，不能單靠 hard call 完整還原。

### 2.2 定序：讀段變成比對與變異

```text
FASTQ（讀段及鹼基品質）
  → read QC → alignment（對到參考基因體）
  → BAM／CRAM（比對位置及證據）
  → variant calling（估計基因型與變異）
  → VCF／BCF → filtering、annotation、cohort analysis
```

Reference genome（參考基因體）是共同座標與序列基準，不代表每個人的正常或健康基因體。GRCh37 與 GRCh38 座標不能直接混用；即使版本名稱相同，也需確認 contig、decoy、FASTA 內容及索引一致。

### 2.3 常見檔案速查

| 檔案 | 存什麼 | 第一眼要檢查什麼 |
|---|---|---|
| IDAT／CEL | 平台相關的原始晶片訊號 | 晶片型號、樣本對照表與處理版本 |
| PED／MAP | 教學易讀的 genotype 文字檔與位點表 | 每個樣本的 ID、每個位點兩個 allele；缺失以 0 表示 |
| PLINK BED／BIM／FAM | 二進位 genotype、位點資訊、樣本資訊 | 三檔前綴一致，樣本與位點數正確 |
| FASTQ | 每筆通常四行：名稱、序列、分隔符號、品質字元 | 序列長度與品質長度一致、paired-end 配對完整 |
| SAM／BAM／CRAM | 文字／二進位／壓縮比對資料 | reference、樣本 read group、排序、索引 |
| VCF／BCF | 文字／二進位的變異與基因型 | header 定義、reference、樣本名稱及 FILTER |

注意：PLINK 的 `.bed` 是二進位 genotype，不是描述基因體區間的文字 BED。VCF POS 為 1-based；一般區間 BED 起點為 0-based、終點不包含在區間內。CRAM 的解碼可能需要相符的 reference，交付時不能只留下單一 CRAM 檔。

想一想：拿到 VCF，是否就能把沒有列出的位點視為「沒有變異」？

解析：不行。它可能是只記錄變異的 variant-only 檔；未列出也可能是未覆蓋或未通過輸出條件。判讀前，先確認檔案的輸出規則。

## 三、SNP array 品質控制與分析原理

### 3.1 先檢查樣本，再檢查位點，必要時反覆檢查

Missingness 是缺失基因型的比例；call rate = 1 − missingness。假設一個樣本 6,000 個位點中有 2,000 個無法判定，其 call rate 約 66.7%。假設某位點 40 人中 10 人無法判定，該位點 call rate 是 75%。前者是樣本問題，後者是位點問題。

| 層級 | 指標／問題 | 原理與後續調查 |
|---|---|---|
| Sample | call rate 偏低 | 可能為 DNA 品質、批次或 calling 問題；查看板位與原始訊號 |
| Sample | heterozygosity 異常 | 雜合比例偏高可能與污染有關，偏低可能與近親或技術因素有關；須結合族群背景 |
| Pair | duplicates／relatedness | 比較共同基因型與等位基因共享；查樣本來源，不自動刪除其中一人 |
| Cohort | ancestry PCA | 看主要變異方向；也可能顯示批次、親緣或品質問題 |
| Variant | missingness、MAF、HWE | 分別看資料完整性、較少見 allele 的頻率及基因型分布偏離 |
| Region | BAF／LRR、ROH | 檢查連續多個探針的訊號，而非只看單點 |

Threshold（門檻）需由研究設計、樣本品質與分布支持。本課 `--mind 0.05` 與 `--geno 0.05` 是示範「缺失超過 5%」的篩選，不是所有研究或臨床樣本的標準。

### 3.2 MAF、HWE 與異常雜合度

MAF（minor allele frequency）是較少見等位基因的比例。在無缺失的 40 名二倍體樣本中有 80 個 allele，若較少見 allele 有 8 個，MAF 為 0.1。不同族群與資料集的 MAF 可以不同；稀有變異研究不應套用常見變異分析的 MAF 排除規則。

HWE（Hardy–Weinberg equilibrium，哈溫平衡）在理想隨機交配等條件下，預期基因型比例為 p²、2pq、q²。例如 p=0.7、q=0.3，預期比例為 0.49、0.42、0.09。偏離可由技術錯誤、族群混合、親緣、選擇或疾病相關因素造成；不能把低 p-value 等同探針壞掉。病例對照研究常先檢查適當的對照與祖源分層；本課先產生報表，不自動 HWE 過濾。

Heterozygosity（雜合度）表示可判定位點中雜合基因型的程度。PLINK `.het` 的 F 是相對預期雜合度的估計量，不是直接的雜合百分比，也不是診斷結論。離群值應先回查污染、族群與相關樣本等因素。

### 3.3 PCA 與親緣分析

PCA（主成分分析）把許多 genotype 變數壓縮成少數方向。PC1 是資料變異最大的方向，PC2 與其正交。它沒有預先知道疾病或祖源標籤，群聚不能直接稱為離散種族，也不能證明疾病機制。

LD（連鎖不平衡）指位點間 allele 非獨立。LD pruning 先挑選較少冗餘的位點，避免某些高度相關區域過度主導 PCA 或親緣估計。`50 5 0.2` 表示以 50 個位點的視窗、每次前進 5 個位點，依 r² 門檻 0.2 進行修剪。

IBS 是觀察到相同 allele；IBD 是推估 allele 來自共同祖先。PLINK `--genome` 的 PI_HAT = Z2 + 0.5 × Z1，整合共享兩份與一份 IBD 的機率。接近 1 可提示重複樣本或同卵雙生，但需要來源紀錄與額外 QC 確認；族群混合也可能影響估計。[PLINK 親緣分析文件](https://www.cog-genomics.org/plink/1.9/ibd)

Reported-sex check 比較登錄欄位與性染色體訊號的相容性；須考慮 X 非 PAR 區、平台、倍體、嵌合與檢體來源。PAR 是 X/Y 可對應的偽常染色體區。異常只觸發資料核對，不自動修改紀錄，也不推論性別認同。本次合成資料只有常染色體，因此不執行此檢查。[PLINK QC 文件](https://www.cog-genomics.org/plink/1.9/basic_stats)

## 四、Array 實作與情境練習

### 4.1 操作練習：從 genotype 找出 QC 問題

這個練習要回答兩件事：「哪些資料需要先檢查？」以及「你的判斷依據在哪裡？」請依序開啟資料、產生 QC 報表並找出異常，在筆記中記錄一個暫停下游分析的理由。安裝方法見文末附錄。以下皆為 **Ubuntu／WSL 的 Bash 指令，不是 PowerShell**。

將專案放在 Ubuntu 的 `~/KCGMH_Cource_Series`。若路徑不同，只修改第一行。`cd` 切換資料夾；`head` 顯示前幾行；`--out` 指定輸出前綴。

```bash
cd ~/KCGMH_Cource_Series/demos/lesson-01-genomics
python3 generate.py practice01
cd practice01
PLINK=plink1.9 bash ../run-array.sh
head -n 5 raw.fam
head -n 5 raw.bim
head -n 5 qc.imiss
head -n 5 qc.lmiss
```

`practice01` 必須是新資料夾；產生器拒絕覆蓋既有資料。重做時使用 `practice02`。在既有練習目錄重跑分析腳本會取代同名結果，故重要比較應先保留整個練習目錄。

資料共有 40 人、6,000 個常染色體 SNP，採固定亂數種子，包含刻意加入的缺失、重複樣本及連續純合區。這些不是疾病樣本或真實人類族群模擬；分析結果僅供理解方法。你可以先檢查輸出，再對照後面的結果解析。

完整腳本的核心步驟如下，可逐行操作替代執行腳本：

```bash
plink1.9 --file array --make-bed --out raw
plink1.9 --bfile raw --missing --freq --hardy --het --out qc
plink1.9 --bfile raw --mind 0.05 --make-bed --out sample_qc
plink1.9 --bfile sample_qc --geno 0.05 --make-bed --out clean
plink1.9 --bfile clean --maf 0.05 --indep-pairwise 50 5 0.2 --out prune
plink1.9 --bfile clean --extract prune.prune.in --genome --out related
plink1.9 --bfile clean --extract prune.prune.in --pca 4 --out structure
plink1.9 --bfile clean --homozyg --homozyg-snp 100 --homozyg-kb 1000 --out roh
```

注意：這份練習資料仍保留重複樣本。因此，即使順利產生 PCA，也不代表資料已可用於正式關聯分析。真實研究需先處理重複／親緣、祖源、批次與研究設計。ROH 使用未做 LD pruning 的 QC genotype，因為它需要連續位點資訊。

先認識你會查看的輸出：

| 輸出檔 | 如何閱讀 |
|---|---|
| `qc.imiss` | 每列一個樣本；`F_MISS` 是該樣本缺失比例 |
| `qc.lmiss` | 每列一個位點；`F_MISS` 是該位點缺失比例 |
| `qc.het` | 查看樣本的觀察／預期純合數及 F，搭配資料背景判斷 |
| `related.genome` | 每列一對樣本；比較 `IID1`、`IID2` 與 `PI_HAT` |
| `roh.hom` | 查看樣本、染色體、區段起訖位置及支持的 SNP 數 |

FID 是家族識別碼，IID 是個體識別碼；本資料用人工編號，不代表真實家系。你可以用 `head` 先閱讀欄名，再以 `awk` 篩出指定列。下列指令已指出幾個值得核對的樣本與位點。

用下列指令迅速找到報表證據：

```bash
awk 'NR==1 || $2=="S40"' qc.imiss
awk 'NR==1 || $2=="v1"' qc.lmiss
awk 'NR==1 || ($2=="S01" && $4=="S02")' related.genome
head -n 6 structure.eigenvec
head -n 6 roh.hom
wc -l raw.fam clean.fam raw.bim clean.bim
```

結果解析：請將下列內容與你的輸出比較；若不同，先確認是否使用同一份資料與相同參數，不要直接修改結果檔。

| 問題 | 預期證據與解釋 |
|---|---|
| 哪個樣本缺失最多？ | S40，F_MISS 約 1/3；先查樣本品質 |
| 哪個位點缺失明顯？ | v1；原始資料缺失超過 1/4，先查 probe/calling |
| 篩選後留下多少？ | 39 個樣本、5,999 個位點 |
| 哪一對需要查重複？ | S01/S02，PI_HAT 接近 1；不能單憑這項結果判定資料應刪誰 |
| ROH 能直接當 CNV 嗎？ | 不行；S03 的長純合區沒有提供拷貝數證據 |

`.eigenvec` 前兩欄為 FID/IID，其後為 PC 座標；`.eigenval` 是各主成分的 eigenvalue（特徵值，反映變異量）。本次直接查看座標即可，不需要另外安裝繪圖套件。

### 4.2 情境練習：有結果，是否就能繼續分析？

以下練習不需要執行程式。請先寫下「是否能繼續分析」及「還需要哪些證據」，再閱讀解析。

1. 病例都在 A 批次、對照都在 B 批次，PCA 剛好分兩群。能說疾病造成基因體差異嗎？
2. 某樣本雜合度偏高但 call rate 正常。可以判定它通過 QC 嗎？
3. 只保留 genotype，還能完整重做原始晶片的 CNV 分析嗎？

參考解析：

1. 不能。疾病與批次完全混雜，單靠加入批次共變數也未必可辨識兩者。
2. 資訊不足。需要查污染、樣本混合、祖源與訊號分布，不能只依一個正常指標放行。
3. 通常不能完整重做。需要找回強度資料、manifest、cluster reference 與處理版本。

完成練習後，試著用一句話區分：「我已觀察到的異常」與「我懷疑但尚未證實的原因」。

## 五、WES/WGS：從讀段到變異

### 5.1 先讀 FASTQ，再談 alignment

FASTQ 品質常採 Phred 尺度：Q = −10 log10(P_error)。Q20 對應模型中的 1% 錯誤機率，Q30 對應 0.1%；不是已實測每條 read 一定有多少錯誤。示範檔以 `I` 表示 Phred+33 編碼的 Q40，為理想化資料。

Alignment（比對）找出 read 可能來源位置；短讀段在重複區可能有多個候選位置。Mapping quality（MAPQ）描述比對位置的不確定性，其定義與校準依工具而異；它與 base quality（BQ，單一鹼基品質）不同。CIGAR 描述 read 與 reference 的對應關係，例如 150M 表示 150 個比對位置，M 本身不區分 match 與 mismatch。

實際流程還需檢查接頭、重複讀段、污染、插入片段長度、capture target 與文庫特性。不能因為流程產出 BAM，就認為 QC 完成。

Depth（深度）是位置被多少 reads 覆蓋；breadth（覆蓋廣度）是目標區達到指定深度的比例。例：平均 100× 的 WES 仍可能有某外顯子 0×。應報告「多少目標鹼基達到事先定義的可分析條件」，而不只平均值。

### 5.2 最小可執行示範：SAM → BAM → VCF

為了讓一般筆電短時間執行，教材提供 chrToy 2,000 bp、40 條理想讀段；SAM 已由產生器指定正確位置，**這不是實際 aligner 的輸出，也沒有測試真實比對效能**。FASTQ 用來觀察格式；本段從已比對的 SAM 起跑，不在課中重跑完整人類 WES/WGS 流程。

在第四節建立的 `practice01` 中執行：

```bash
head -n 8 reads.fastq
head -n 5 aligned.sam
bash ../run-sequence.sh
cat calls.tsv
cat review.tsv
```

拆解程式：

```bash
samtools faidx reference.fa
samtools view -b aligned.sam | samtools sort -o sample.bam
samtools index sample.bam
samtools flagstat sample.bam
samtools depth -aa sample.bam > depth.tsv
bcftools mpileup -Ou -f reference.fa -a FORMAT/DP,FORMAT/AD sample.bam |
  bcftools call -mv -Oz -o calls.vcf.gz
bcftools index calls.vcf.gz
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT[\t%GT\t%DP\t%AD]\n' calls.vcf.gz
```

`|` 把前一步輸出傳給下一步；`>` 把輸出存檔。`faidx` 建立 reference 索引；`sort` 依座標排序；BAM index 支援依區域查詢。`mpileup` 整合讀段證據、估計基因型 likelihood；`call` 再進行變異／基因型推估。`-Ou` 是未壓縮 BCF 串流，`-Oz` 是壓縮 VCF。本例預期在 chrToy:1000 得到一個雜合 SNV，DP 約 40，AD 約 20,20；實際品質值可能隨版本改變。[SAMtools 文件](https://www.htslib.org/doc/samtools.html)、[BCFtools 文件](https://samtools.github.io/bcftools/bcftools.html)

只看觀察到 ALT read 數並不等於 variant calling。Caller 還會使用 read/base quality、錯誤模型與先驗等資訊；真實 germline 分析可能採局部組裝等不同方法，本示範不替任何 production pipeline 背書。

### 5.3 VCF 判讀練習

`review.vcf` 是另外人工設計的 QC 案例，**不是以上 caller 的輸出**。LowDP、LowMQ 為教材自行定義的標記，不是所有 caller 的通用欄位。

| 欄位 | 說明 |
|---|---|
| CHROM、POS | contig 與 1-based 位置 |
| REF、ALT | reference allele 與替代 allele；REF 不等於健康 allele |
| QUAL、FILTER | 位點層級品質及套用的篩選狀態；PASS 不保證正確，`.` 也不等於 PASS |
| GT | 0/0 為 reference homozygous；0/1 為 heterozygous；1/1 為 ALT homozygous；./. 為缺失 |
| AD | 各 allele 的支持讀段數，順序為 REF、ALT1、ALT2… |
| DP | 深度；可能與 AD 加總不同，依 caller 與過濾定義而定 |
| GQ | genotype quality；描述基因型信心，與位點 QUAL 不同 |

```bash
bcftools query -f '%POS\t%FILTER[\t%GT\t%AD\t%DP\t%GQ]\n' review.vcf
```

預期：1000 的 AD=20,20、DP=40；1100 的 DP=3、GQ=8；1200 的 AD=38,2、GQ=15；1300 標記 LowMQ。

練習：哪兩筆資料的 depth 雖然高，仍需要進一步檢查？請先指出欄位證據，再解釋理由。

解析：1200 的 AD=38,2，兩種 allele 的支持數明顯不平衡，且 GQ 偏低；1300 有 LowMQ 標記，需要回到比對證據確認。兩者都說明 DP 高不等於基因型可靠。

Allele balance 可用 ALT/(REF+ALT) 作簡單示範：20/(20+20)=0.5，2/(38+2)=0.05。二倍體 germline 雜合常期待接近 0.5，但不是固定規則；抽樣、比對偏差、CNV、污染、嵌合等都可能改變它。不要直接把不平衡當成特定生物學機制。

### 5.4 Cohort 與 joint calling

多樣本 VCF 在 FORMAT 後面有多個樣本欄位。各自的 variant-only VCF 直接合併，不能把沒有列出的樣本位點補成 0/0；必須知道那些位置是否真的有足夠 reference 證據。GVCF 可保存非變異區段的信心資訊供特定流程 joint genotyping 使用。

Joint calling／genotyping 是跨樣本整合證據進行判定，不只是橫向拼接表格；仍需每個樣本的深度與品質控制。不能混用不相容的 caller 輸出而假設統計意義相同。

## 六、ROH、CNV 與整合判讀

### 6.1 強度的兩個方向：BAF 與 LRR

BAF（B allele frequency）是單一樣本、單一探針的相對 allele 訊號指標，**不是族群中的 B allele 頻率**。正常二倍體常見約 0、0.5、1 三群。LRR（log R ratio）是觀察到的總訊號相對預期訊號之 log2 比值，經平台正規化後用來反映劑量變化。

下表是理想化示意，真實值受平台、批次、雜訊、嵌合與細胞比例等影響，不可作固定 CNV threshold：

| 情境 | BAF 群帶示意 | LRR 趨勢 | 需要的補充證據 |
|---|---|---|---|
| 正常二倍體 | 0、0.5、1 | 接近基準 | 強度與探針品質 |
| 缺失 | 常見只剩 0、1 | 下降 | 連續探針支持、邊界及其他證據 |
| 重複／增益 | 可見約 0、1/3、2/3、1 | 上升 | 正規化、區域分段與批次排查 |
| 長段純合 ROH | 0、1，缺乏中間雜合帶 | 可仍接近基準 | 拷貝數與全基因體背景 |

```bash
head -n 14 intensity.csv
awk -F, 'NR==1 || $1=="deletion" || $1=="ROH"' intensity.csv
```

資料內的 LRR −0.6／0.3 僅用來表示下降／上升，不表示所有單拷貝缺失或三拷貝區段都得到相同值。CNV caller 常使用 segmentation（區域分段）：整合相鄰探針，尋找共同訊號改變；單一探針異常不夠。

ROH（run of homozygosity，連續純合區段）是一段連續位點呈現純合。它可反映人口歷史、近親等因素，也受探針密度與錯誤影響。ROH 不等於 deletion，不可只憑一段 ROH 就診斷單親二倍體，也不應在沒有相應證據時稱為後天獲得的 LOH。

### 6.2 定序資料的區域證據

CNV 可利用正規化 read depth；SV 可能需異常 paired-end 距離、split reads 或組裝等證據。WES 的捕捉偏差使 read-depth CNV 分析需要適合的參考樣本與校正；本課的 `samtools depth` 只是觀察覆蓋，並不是完整 CNV caller。

看 toy 深度：

```bash
awk '$2>=995 && $2<=1005' depth.tsv
awk '{n++; if($3>=10) covered++} END {print "fraction >=10x:", covered/n}' depth.tsv
```

分母是這個 toy contig 的 2,000 個位置，不是外顯子目標區。真實 WES 必須對正確 capture target 區域計算，避免混用分母；本例大部分位置沒有 reads 是刻意設計，不代表人類 WGS 的品質水準。

### 6.3 合併資料前的五項核對

1. Sample ID：臨床表格、檢體、檔案與 read group 是否一致？有沒有重複？
2. Reference build：座標與 FASTA 是否匹配？chr1 與 1 命名是否相容？
3. Allele／strand：正反股是否一致？A/T、C/G 回文 SNP 單靠 allele 字母不易判斷方向。
4. 表型與批次：缺失是否與疾病組別、晶片、定序批次相關？
5. Provenance（分析來源紀錄）：資料來源、工具版本、參數、篩選理由與排除清單能否重建？

Ascertainment bias（選取偏差）在 array 常來自預先選定的 SNP 與參考族群；換一個族群時，資訊量與表現可能不同。Imputation（基因型填補）依 LD 與參考 haplotype 推估未測位點，不是直接測量，可靠性依族群匹配、頻率及參考品質而變。

## 七、自我檢核與研究應用

### 7.1 自我檢核

請先不看解析，用自己的話回答。若能指出相關檔案、欄位或需要補充的證據，就比只記住指令更接近理解分析流程。

1. 原始強度、genotype hard call、VCF annotation 哪一個最接近直接測量？
2. WES 平均 100×，能保證每個 exon 可靠嗎？
3. PCA 分成兩群，可以直接歸因於疾病或種族嗎？
4. 有 genotype 而沒有強度，能否完整重做 array CNV QC？
5. VCF 的 PASS 且 DP=40，是否足夠接受雜合結果？

### 7.2 參考解析

1. 原始強度。Hard call 是演算法推估的基因型；annotation 是後續加入的基因、功能或資料庫資訊。可回看第二節的兩條資料流。
2. 不能。平均值會掩蓋低覆蓋區，需要看逐區域覆蓋與可分析比例。可回看第五節的 depth 與 breadth。
3. 不能。需核對祖源、親緣、批次與 QC，避免把資料結構直接當成生物學解釋。可回看第三節與情境練習。
4. 通常不能。需要原始或衍生強度資料，不能從離散的 hard calls 完整重建 BAF/LRR。可回看第二節與第六節。
5. 不足。還需 AD、GQ、比對、區域與樣本背景等證據。可回看第五節的 VCF 判讀案例。

### 7.3 套用到自己的研究

選一個你正在進行或有興趣的研究，填寫以下清單。暫時不知道的項目可標記「待確認」，作為與生物資訊人員討論時的問題。

| 項目 | 你的筆記 |
|---|---|
| 研究問題：希望比較或找到什麼？ | |
| 平台與版本：晶片、panel、WES 或 WGS？ | |
| 檢體設計：來源、分組、批次與重複樣本？ | |
| 樣本對照表：檢體與檔案如何對應？ | |
| 目標變異：SNV、indel、CNV、SV 或其他？ | |
| Reference：版本與檔案來源？ | |
| 可取得的原始檔與衍生資料？ | |
| QC 計畫：要檢查哪些樣本、位點與區域指標？ | |
| 主要輸出：需要什麼表格、圖或分析結果？ | |
| 人工確認點：哪些決定需要回查資料與共同討論？ | |

## 八、延伸練習：移除已知重複樣本後會改變什麼？

如果你已完成基本練習，可以進一步比較 `raw` 與 `clean` 的樣本／位點數，以及移除已知合成複本前後的 PCA。這次除了觀察結果，也請保留「移除了誰、為什麼移除、使用哪些指令」的紀錄。

下列只針對已知合成複本 F02/S02，不應移用到病人資料自行排除樣本：

```bash
awk '$1=="F02" && $2=="S02" {print $1, $2}' clean.fam > duplicate.remove
plink1.9 --bfile clean --remove duplicate.remove --make-bed --out unrelated_demo
plink1.9 --bfile unrelated_demo --maf 0.05 --indep-pairwise 50 5 0.2 --out prune2
plink1.9 --bfile unrelated_demo --extract prune2.prune.in --pca 4 --out structure2
wc -l clean.fam unrelated_demo.fam
head -n 6 structure2.eigenvec
```

預期 39 → 38 人。PC 的正負號可翻轉；移除樣本後頻率、軸方向與尺度也可能改變，不能將座標逐項相減就當成改善程度。真正比較需看整體結構與原始 metadata。保留 `duplicate.remove`、log 與理由，本例理由為「教學產生器刻意建立的 genotype 複本」。

## 九、名詞複習卡

| 名詞 | 一句話解釋 |
|---|---|
| Genotype／allele | 個體在某位點的等位基因組合／該位點的一種序列版本 |
| QC | Quality control，判斷資料是否符合分析前提的品質控制 |
| Normalization | 將技術尺度調整到可比較的基準，不保證消除全部批次偏差 |
| Call rate／missingness | 可判定比例／缺失比例 |
| HWE／MAF | 基因型比例的理想平衡模型／較少見 allele 的頻率 |
| LD／pruning | 位點間的關聯／為特定分析減少冗餘位點 |
| PCA／PC | 將高維資料摘要為主成分／其中一個變異方向 |
| Relatedness／IBD | 個體間遺傳關聯／由共同祖先繼承相同 allele 的推估 |
| BAF／LRR | 相對 B allele 訊號／總訊號相對預期的對數比例 |
| ROH／CNV | 連續純合區／拷貝數變化，兩者不是同義詞 |
| Alignment／caller | 將 read 放到 reference／由證據推估變異或 genotype 的工具 |
| BQ／MAPQ／GQ | 鹼基品質／比對品質／基因型品質，各自描述不同不確定性 |
| Annotation | 為變異加上基因、功能與資料庫等資訊，不等於致病性證明 |
| Confounding | 兩個因素糾纏，無法把觀察到的差異簡單歸因其中之一 |
| Provenance | 保留資料如何取得、轉換、分析與人工修改的可追溯紀錄 |

## 附錄 A：Windows 課前安裝

### A1. 路線與權限

建議使用 Windows 11 與 WSL2 Ubuntu，統一執行 Linux 版 PLINK 1.9、SAMtools、BCFtools 與 Python 3。無須 R、Conda、Docker、付費晶片軟體或 GPU。玩具資料很小，但 WSL 與 Ubuntu 本身需要額外磁碟空間；課前預留數 GB 以上並確認院內政策。

WSL 的簡易安裝指令也支援 Windows 10 2004、build 19041 以上，但仍須確認作業系統支援與院內資訊安全規範。安裝需要系統管理員權限、適當虛擬化設定及網路；受管制電腦請先找資訊部門，不要繞過限制。[Microsoft WSL 安裝說明](https://learn.microsoft.com/en-us/windows/wsl/install)

### A2. 在 PowerShell 安裝 WSL

在 Windows 搜尋 PowerShell，按右鍵「以系統管理員身分執行」：

```powershell
wsl --install -d Ubuntu
```

依提示重新開機，開啟 Ubuntu，建立 Linux 使用者名稱與密碼。輸入密碼不顯示字元是正常現象。在 PowerShell 確認：

```powershell
wsl --list --verbose
```

Ubuntu 的 VERSION 應為 2。若列為 1，確認硬體與政策允許後執行：

```powershell
wsl --set-version Ubuntu 2
```

如果發行版名稱不是 Ubuntu，請使用清單上的實際名稱。已安裝者不必重複安裝；更新與問題排查以 Microsoft 官方文件為準。

### A3. 在 Ubuntu 安裝本課工具

以下改在 Ubuntu 終端機執行，不要在 PowerShell 貼入 `sudo apt`：

```bash
sudo apt update
sudo apt install -y python3 plink1.9 samtools bcftools
python3 --version
plink1.9 --version
samtools --version
bcftools --version
```

Python 執行合成資料產生器，僅用標準函式庫，不需 `pip install`。PLINK 1.9 負責 genotype QC、PCA、親緣與 ROH；SAMtools 負責比對檔處理；BCFtools 負責 VCF 與簡化 variant calling。不要將 PLINK 2 的指令直接混入此教材。

Ubuntu 套件庫版本可能不是最新版，但需實際記錄版本。若 `plink1.9` 找不到套件，請資訊人員確認 Ubuntu 的 universe repository 是否啟用；可參考 [PLINK 官方下載頁](https://www.cog-genomics.org/plink/1.9/)，選取與作業系統及 CPU 架構相符版本。手動安裝檔通常叫 `plink`，此時腳本使用 `PLINK=plink bash ../run-array.sh`，逐行指令也相應替換。不要下載不明來源執行檔。

### A4. 將教材從 Windows 放入 Ubuntu

先在 Windows 解壓完整專案，不要只複製單一 Markdown，否則沒有示範腳本。假設資料夾位於 Windows 的 `C:\Users\你的帳號\Downloads\KCGMH_Cource_Series`，在 Ubuntu 執行以下命令；請替換「你的帳號」並確認目的資料夾尚不存在：

```bash
cp -r "/mnt/c/Users/你的帳號/Downloads/KCGMH_Cource_Series" ~/KCGMH_Cource_Series
cd ~/KCGMH_Cource_Series/demos/lesson-01-genomics
ls
```

應看到 `generate.py`、`run-array.sh`、`run-sequence.sh` 與 `README.md`。Windows 路徑以 `/mnt/c/` 存取 C 槽；路徑有空白時加雙引號。建議在 Ubuntu 家目錄內分析，避免混淆兩套檔案路徑。

使用 Windows 記事本或既有文字編輯器閱讀 Markdown／CSV 即可；不需另外安裝編輯器。二進位 BED/BAM 不能用記事本正常閱讀，要用相應工具。

### A5. 課前完整測試與版本存檔

```bash
python3 generate.py preclass01
cd preclass01
PLINK=plink1.9 bash ../run-array.sh
bash ../run-sequence.sh
cat calls.tsv
wc -l clean.fam clean.bim
python3 --version > versions.txt
plink1.9 --version >> versions.txt
samtools --version >> versions.txt
bcftools --version >> versions.txt
```

確認有 39 個樣本、5,999 個 SNP，以及 chrToy:1000 雜合 SNV。保存產生器、兩個 shell 腳本、版本檔、PLINK log 與結果，不只留下截圖。

### A6. 無法安裝與常見問題

| 現象 | 處理 |
|---|---|
| 無管理員權限或院內不允許 WSL | 先洽資訊部門；也可與同學共用操作環境，或先完成第 4.2 節的情境練習 |
| `command not found` | 確認在 Ubuntu、安裝成功，以及名稱為 plink1.9 而非 plink2 |
| `No such file` | 先執行 `pwd`、`ls`；確認目前在產生出的練習資料夾 |
| `FileExistsError` | 產生器保護既有資料；改用新的 practice02 等名稱 |
| `$'\r': command not found` | 腳本被轉成 Windows CRLF；以編輯器改存 UTF-8／LF 後重跑 |
| 找不到 reference／索引 | 確認 reference.fa、其 .fai 及 BAM index 都在練習目錄 |
| PLINK 提示缺少 phenotype | 本課 FAM phenotype 刻意為 -9；只做 QC，不做疾病關聯分析 |
| 沒有性染色體可做 sex check | 本教材的設計限制，不是安裝錯誤 |

若只需 array 操作，可從官方下載 Windows 版 PLINK 1.9、解壓後在該資料夾的 PowerShell 用 ` .\plink.exe --version` 確認。但本文的 Bash 腳本、awk 與管線以 WSL 為標準路線；原生 Windows 方案不等於已具備完整示範環境。

## 附錄 B：示範範圍與後續學習

本課刻意不安裝或執行平台原始 intensity calling 軟體，不執行人類全基因體 alignment，也不執行正式 CNV/SV caller。這些步驟的原理與輸入需求已在正文說明；實作需另備平台資料、reference、足夠計算資源與驗證過的流程。不能將玩具資料成功運行視為臨床分析驗證。

進一步閱讀：

- [PLINK 1.9](https://www.cog-genomics.org/plink/1.9/)：指令、格式與下載。
- [PLINK 基本統計](https://www.cog-genomics.org/plink/1.9/basic_stats)：QC 欄位與限制。
- [SAMtools](https://www.htslib.org/doc/samtools.html)：比對檔操作。
- [BCFtools](https://samtools.github.io/bcftools/bcftools.html)：variant calling 與 VCF 查詢。
- [Microsoft WSL](https://learn.microsoft.com/en-us/windows/wsl/install)：Windows 安裝與權限。

軟體文件核對日期：2026-09-13。Windows 安裝步驟依官方文件整理；本專案的實際執行驗證環境與結果見[示範說明](../demos/lesson-01-genomics/README.md)，不宣稱已在所有 Windows／Ubuntu 組合測試。
