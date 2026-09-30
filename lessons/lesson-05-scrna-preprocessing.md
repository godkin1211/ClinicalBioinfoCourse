# Lesson 05 — Single-cell RNA-seq：技術與前處理

## 課程目標

完成本堂後，學員能：

1. 說明 cell barcode、UMI 與 gene-by-cell count matrix 如何形成。
2. 辨認 empty droplets、ambient RNA、low-quality cells 與 doublets。
3. 理解 normalization、feature selection、PCA、neighbors、UMAP 與 clustering 的角色差異。

## 臨床案例

分析腫瘤切除檢體中的免疫微環境，希望辨認少量耗竭 T cell population。

- 決策：哪些 QC 能去除技術問題，又不會先把罕見細胞刪掉？
- 故意問題：直接使用固定 mitochondrial percentage threshold。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–10 | 臨床問題 | Bulk 平均值與 cell heterogeneity；single-cell 能回答什麼 | 選擇 bulk 或 single-cell |
| 10–20 | 技術與檔案 | Droplet、barcode、UMI、reads、matrix、H5/H5AD | 從 read 配對重建一筆 count |
| 20–35 | QC 原理 | Empty droplets、ambient RNA、genes/counts、mitochondrial fraction、doublets | 比較不同 QC evidence |
| 35–55 | 示範 | QC distributions、filtering、normalization、PCA、neighbors、UMAP、clustering | 調整一個 threshold 並觀察影響 |
| 55–60 | 決策題 | 高 mitochondrial fraction 是否一律刪除？ | 說明情境 |

## 核心資料流

```text
tissue dissociation / nuclei isolation
        ↓
cell barcode + UMI + sequencing reads
        ↓
barcode × gene raw count matrix
        ↓
empty droplet / ambient RNA / doublet / cell QC
        ↓
normalization → feature selection → PCA → neighbor graph
        ↓
UMAP + clustering
```

## 必講概念

- Barcode 不自動等於一個完整細胞。
- UMI 降低 PCR duplication 影響，但不能消除所有技術偏差。
- QC threshold 應根據每個 sample 的分布、組織與預期 cell type 評估。
- Mitochondrial-high 可能是 dying cell，也可能與組織／細胞型態有關。
- Doublet detector 是風險分數，不是絕對真值。
- UMAP 是 visualization；clustering 通常基於 neighbor graph，不是直接在 UMAP 上切群。
- QC 與 annotation 需要迭代，但不可為了符合預期答案而任意調 threshold。

## 示範

使用公開 PBMC 或 tumor dataset：

1. 顯示 empty droplets 與 cell-containing barcodes。
2. 畫 genes、counts、mitochondrial fraction 的 joint distributions。
3. 比較固定門檻與 sample-aware threshold。
4. 顯示 doublet-rich cluster。
5. 比較過度過濾前後罕見 cell population。

## 不深入

- 每種 ambient RNA correction 方法
- UMAP objective function
- 大規模 GPU workflow

## 決策題

**題目：** 所有 mitochondrial percentage > 10% 的細胞是否都應移除？

**正確決策：** 不應直接套用通用固定門檻。

**理由：** 需看 sample-specific distribution、組織、生物情境、其他 QC 指標及下游結果，並保存 threshold 與排除數量。

## 講師檢查

- [ ] 圖中使用 barcode 而非過早稱為 cell
- [ ] QC 前後各 cell type 數量有被比較
- [ ] UMAP 未被描述成 quantitative distance
- [ ] threshold 決策有 provenance
