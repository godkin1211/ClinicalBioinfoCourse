# Panel、WES、WGS：差異與選擇

對應第一堂 HTML 投影片第 24–29 頁（新增格式總覽前為第 23–28 頁）。本段以常見的短讀長、基因體 DNA 定序為例，重點是研究設計與生物資訊分析，不是個別病人的檢測建議。圖形與數字均為教學示意，沒有使用病人資料。

## 第 24 頁：先看「讀哪裡」

Panel 指選定基因或區域的定序；WES（whole-exome sequencing）是全外顯子定序，通常以捕捉編碼外顯子為主；WGS（whole-genome sequencing）是全基因體定序，廣泛取樣編碼及非編碼序列。

投影片四條軌道使用同一組座標：第一條為 DNA 地圖，接著是 Panel、WES、WGS 的設計範圍。Panel 範例只選基因甲的編碼外顯子；WES 延伸到三個基因的編碼外顯子；WGS 涵蓋更廣的區域。著色表示「打算讀哪裡」，不是「已經在每個位置得到可靠結果」，也不代表實際基因組中外顯子的比例。

真實 panel 不一定只涵蓋外顯子，也可能選特定內含子或其他區域；WES 的範圍則取決於捕捉試劑、轉錄本定義與版本，不能把「全」理解成每個外顯子都完整無缺。應索取實際 target BED，而不是只看產品名稱。[WES／WGS 範圍](https://www.illumina.com/techniques/sequencing/dna-sequencing/whole-genome-sequencing/whole-genome-vs-exome.html)

和 SNP array 的關鍵差別是：array 主要對預先設計的位點讀取 allele 訊號；定序則讀取片段中的鹼基序列，因此在有效覆蓋、可可靠比對的區域，可以尋找未預先列入變異清單的 SNV 或 indel。捕捉區域預先設計，不等於變異必須事先已知。

## 第 25 頁：為什麼取樣範圍不同？

文庫（library）是接上接頭、可供定序的 DNA 片段集合。流程圖是概念總覽；不同試劑中片段化、加接頭、PCR、富集的實際順序可能不同。

WES 常使用 hybrid capture：探針與目標 DNA 片段結合，讓這些片段在後續定序中占比較高。探針和區域特性會影響富集效率，所以不同外顯子的深度可能差很多。DNA panel 可採捕捉，也可用特定引子的 PCR 擴增；應依建庫方式調整 primer trimming、重複讀序及覆蓋等分析處理，而非套用同一套參數。[捕捉富集](https://www.illumina.com/techniques/sequencing/dna-sequencing/targeted-resequencing/target-enrichment.html)、[Amplicon 技術](https://www.illumina.com/products/by-brand/ampliseq.html)

一般 WGS 不先選特定基因或外顯子，但仍有文庫、GC 含量、讀長及比對限制；WGS 也不必然是 PCR-free。WES 和 WGS 在這裡都是 DNA 檢測，不是測 RNA 的表現量。

Read 是儀器讀出的一段序列。Paired-end 是同一 DNA 片段的兩端各產生一條 read。例如片段長 500 bp、兩端各讀 150 bp，中間可能仍有未直接讀出的部分；片段短時兩端也可能重疊。這有助於理解為什麼 read 長度與片段長度不是同一件事。[Paired-end 說明](https://www.illumina.com/science/technology/next-generation-sequencing/plan-experiments/paired-end-vs-single-read.html)

## 第 26 頁：測量能力不只由平台名稱決定

編碼區的 SNV／短 indel，三種定序策略都可能分析，但前提是該區域有效覆蓋、比對及 calling 可靠。研究深部內含子或調控區時，一般 WES 常缺少直接資料；WGS 可提供更多序列，但「找到差異」仍不等於「知道其功能影響」。

CNV 是拷貝數變化，SV 還包含倒位、易位等結構事件。Panel／WES 可用目標深度等資訊分析部分 CNV，但能力受探針分布、捕捉批次及參考模型影響。WGS 可提供更廣的深度、read-pair 及斷點相關證據，仍需依事件類型配置及驗證分析方法。執行 SNV／indel caller，不等於已完成 CNV／SV 分析。[GATK CNV 流程文件](https://gatk.broadinstitute.org/hc/en-us/articles/360056969372-PostprocessGermlineCNVCalls)

短讀長資料在重複序列或高度相似區域仍可能不易定位；某些重複擴增需要專用演算法，必要時考慮長讀長或其他驗證技術。不能把 WGS 說成能排除所有類型的變異。[NHGRI：完整基因體與重複序列的挑戰](https://www.genome.gov/about-genomics/educational-resources/infographics/Completing-the-human-genome-sequence)

## 第 27 頁：100× 不一定比 35× 更適合問題

這張比較同一組 10 個等長目標區段，並刻意假設每格內深度一致；不是在拿 WES 的目標平均與 WGS 的全基因體平均直接比較。

- 甲：8 格 110×、1 格 120×、1 格 0×。平均為 `(8 × 110 + 120 + 0) / 10 = 100×`，達到至少 20× 的目標比例是 90%。
- 乙：10 格都是 35×。平均為 35×，達到至少 20× 的目標比例是 100%。

如果關心的 exon 正好在甲的 0× 區段，其他區段讀得再深也不能補回那裡的資訊。這不是說 WGS 必然比較好，而是說「平均」會掩蓋空缺。20× 只是算例，並非所有位點或所有變異類型的足夠深度標準。

比較資料時先固定相同目標範圍與過濾條件，再看目標鹼基達到指定深度的比例、低覆蓋位置、重複 reads、base quality 及 mapping quality。不能只拿供應商報告上的兩個平均值排名。[Picard 覆蓋指標](https://broadinstitute.github.io/picard/picard-metric-definitions.html)

## 第 28 頁：對生物資訊流程的實際影響

共同骨架是 FASTQ → 比對 → BAM／CRAM → 依變異類型分析 → VCF 與 QC 報表。流程圖省略各工具特有的前處理與過濾步驟；不是可直接用於臨床的完整 pipeline。

對 Panel／WES，要保存 target BED、捕捉或引子設計版本、reference 及建庫方式。On-target 是評估讀序／鹼基落在指定目標上的情形，計算分母與過濾條件須依工具確認；還要回報低覆蓋 exon，不能只回報平均深度。此處 BED 是區間文字檔，不是 PLINK 的二進位 genotype `.bed`。

WGS 則要規劃全域與重要區域的品質評估、排除或難分析區域，以及多種 caller 的工作量。常見設計下 WGS 的資料與運算負擔通常較大，但實際大小仍受樣本數、深度、檔案格式與保留策略影響，不宜訂出一個通用的 GB 數或成本倍數。

跨 WES 試劑與批次比較時，除了統一 reference，還須確認各樣本在哪些區域具備可比較的證據；某位置沒有 VCF 記錄，可能是沒有覆蓋或未輸出，不能直接補成 0/0。Reference 與資源版本要一起記錄。[GATK 資源文件](https://gatk.broadinstitute.org/hc/en-us/articles/360035890811-Resource-bundle)

## 第 29 頁：如何把差異轉成選擇？

以下是討論的起點，不是只憑疾病名稱自動決定檢測：

1. **候選範圍很明確**：可評估 Panel，核對完整目標、低覆蓋區，以及所需變異類型的偵測能力。所需片段若不在設計中，平均深度再高也無法回答問題。
2. **主要找編碼變異，但候選基因未定**：可評估 WES，同時規劃捕捉版本、關鍵區域的品質與樣本／家系設計。父母與個案共同分析可提供遺傳線索，但會增加樣本與分析需求，仍須核對身分、親緣及各樣本品質。
3. **問題指向非編碼區或結構變異**：可評估 WGS，並確認是否具備相應 caller、困難區域處理、結果解釋與驗證能力，而不是只增加定序範圍。

總預算須兼顧範圍、每人深度、樣本數、分析人力、運算、儲存與驗證。這是研究設計上的權衡，不能只比較單一樣本的報價。

若 WES 沒有找到可解釋結果，先問缺口在哪：目標外？目標內但覆蓋不足？calling 沒涵蓋該變異類型？過濾或註解遺漏？還是已有候選但缺少解釋證據？再依證據評估重分析、補測、WGS 或其他技術。「未找到」不能直接翻譯成「沒有」。[GATK callset 評估](https://gatk.broadinstitute.org/hc/en-us/articles/360035531572-Evaluating-the-quality-of-a-germline-short-variant-callset)

本段最後應能回答：**我要找什麼、平台是否讀得到、流程是否分析得到，以及結果不確定時要回到哪個檔案查證。**
