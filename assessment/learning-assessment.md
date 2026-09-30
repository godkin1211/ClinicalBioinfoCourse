# 學習評量

## A. 課前／課後共同測驗

每題選出最合理答案。課前測不公布答案；課後逐題討論。

1. 一個大型 case–control cohort 主要要分析常見 SNP、族群結構、親緣關係及長段 ROH，在經費有限時首先應評估哪種平台？
   - A. Single-cell RNA-seq
   - B. SNP array，並確認 marker coverage、族群適用性及 intensity data 可得性
   - C. 只要 sequencing depth 夠高，任何 assay 都相同
   - D. Spatial transcriptomics

2. VCF 的主要用途為何？
   - A. 儲存原始影像
   - B. 描述相對於參考序列的變異及其註解／genotype 欄位
   - C. 儲存 normalized expression matrix
   - D. 儲存病理切片

3. Tumor-only variant calling 的重要限制為何？
   - A. 完全不能找到 somatic mutation
   - B. 較難區分 germline variant 與 somatic variant
   - C. 不能產生 VCF
   - D. 不需要考慮 tumor purity

4. RNA-seq 差異表現同時檢定一萬個基因時，為何需要調整 p-value？
   - A. 增加 read depth
   - B. 控制大量檢定造成的 false discoveries
   - C. 移除 batch effect
   - D. 改變 reference genome

5. scRNA-seq 中若每組各有 3 位病人、每位病人 5,000 個細胞，主要 group comparison 的 biological replicate 數最接近多少？
   - A. 30,000
   - B. 15,000
   - C. 每組 3
   - D. 只看 cluster 數

6. UMAP 上兩群細胞分開，最安全的結論是什麼？
   - A. 已證明兩群具有不同臨床預後
   - B. 在目前特徵與分析設定下，它們呈現不同的低維結構
   - C. 已證明一群演化成另一群
   - D. 已排除所有 batch effect

7. 空間轉錄體 spot 同時包含多種細胞時，最適合考慮哪類方法？
   - A. Variant calling
   - B. Deconvolution
   - C. Genome assembly
   - D. Phasing

8. Nextflow 的 `-resume` 主要用途為何？
   - A. 自動改善統計顯著性
   - B. 根據 cache 重用符合條件的既有 task
   - C. 自動上傳病人資料
   - D. 替每個樣本改名

9. AI agent 提議移除兩個 outlier 時，第一個合理動作是什麼？
   - A. 立即接受以得到更漂亮的 PCA
   - B. 要求列出預先定義的 QC 規則、證據與結果敏感度，經人員核准
   - C. 讓 agent 自己投票
   - D. 刪除原始資料

10. 要讓 AI 產生的分析可稽核，最低限度需要保留什麼？
    - A. 最後一張圖即可
    - B. Prompt、輸入、程式、版本、工具呼叫、輸出與人工修改
    - C. Agent 的自然語言摘要即可
    - D. 只保留顯著結果

### 答案

1B、2B、3B、4B、5C、6B、7B、8B、9B、10B。

## B. 逐堂決策題

| 堂次 | 題目 | 核心判斷 |
|---:|---|---|
| 1 | 只有 SNP genotype hard calls，能否完整重做 array CNV QC？ | 通常不能；CNV 與部分 array QC 仍需 intensity、BAF/LRR 或原始訊號 |
| 2 | VAF 5% 是否一定是假陽性？ | 不一定；需結合 depth、error model、tumor purity、matched normal 與正交驗證 |
| 3 | PCA 依 batch 分群時能否直接做 treatment DE？ | 先評估 confounding、design matrix 與可識別性 |
| 4 | 顯著 pathway 是否代表 pathway 被活化？ | 不必然；需看方向、gene set、背景、資料型態與驗證 |
| 5 | 高 mitochondrial percentage 的細胞是否一律移除？ | 不應使用跨組織固定門檻；需結合分布與生物情境 |
| 6 | 30,000 個細胞能否當作 30,000 個病人？ | 不能；病人通常才是 biological replicate |
| 7 | Spot 上免疫基因高是否等於免疫細胞浸潤增加？ | 需考慮 spot composition、ambient signal、組織位置與驗證 |
| 8 | 改了參考基因組後能否直接 `-resume` 並相信 cache？ | 必須確認輸入、參數及 cache invalidation 是否正確 |
| 9 | Agent 成功執行程式是否代表結果正確？ | 不代表；需驗證輸入、方法、數值、圖表及推論 |

## C. 系列課程通過條件

學員以一個自選公開案例完成 [一頁式分析需求書](../templates/analysis-request-template.md)，並達成：

- 清楚定義研究單位、group comparison 與主要 outcome。
- 指定 assay 並說明一項適用性及一項限制。
- 列出主要輸入格式、QC 與統計方法。
- 指定至少一種獨立驗證或 sensitivity analysis。
- 明確標示資料治理與人工核准點。
