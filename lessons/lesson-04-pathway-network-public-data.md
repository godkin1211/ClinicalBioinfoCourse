# Lesson 04 — Pathway、網路與公開資料分析

## 課程目標

完成本堂後，學員能：

1. 根據輸入資料選擇 over-representation analysis 或 ranked-list enrichment。
2. 說明 background universe、gene-set redundancy 與 multiple testing 如何影響結果。
3. 使用公開 cohort 做外部驗證，同時避免資料洩漏與過度推論。

## 臨床案例

Bulk RNA-seq 得到 420 個差異基因，其中多個免疫與代謝 pathway 顯著。

- 決策：這些 pathway 能否支持免疫活化或治療機轉？
- 外部資料：以 TCGA 或 GEO cohort 檢查方向是否可重現。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–10 | 問題 | 從 gene list 到 biological question | 選 ORA 或 GSEA |
| 10–20 | 輸入與資料庫 | Ranked list、background universe、GO/Reactome/MSigDB、ID mapping | 找出錯誤 universe |
| 20–35 | 方法原理 | Hypergeometric intuition、running-sum intuition、FDR、leading edge、redundancy | 比較兩種分析輸出 |
| 35–55 | 示範 | Enrichment map、gene-concept network、TCGA/GEO validation | 找出 circular validation |
| 55–60 | 決策題 | 顯著 pathway 是否等於 pathway 被活化？ | 用一句話限制結論 |

## 核心資料流

```text
DE result / ranked statistic
        ↓
gene ID harmonization + appropriate universe
        ↓
ORA or ranked-list enrichment
        ↓
redundancy reduction + leading-edge inspection
        ↓
independent cohort / orthogonal validation
        ↓
bounded biological interpretation
```

## 必講概念

- ORA 的 universe 應接近「實際有機會被檢出的基因」，不是任意使用全基因組。
- 先用 p-value 篩 gene list 再做 ORA，會把任意 threshold 帶入結果。
- Ranked-list 方法保留整體排序資訊，但排序統計量與方向必須合理。
- 大型且重疊的 gene sets 容易重複出現，不能把每列當成獨立機轉。
- Network hub 可能來自資料庫研究偏差或 degree，不自動等於 therapeutic target。
- 同一 cohort 同時做 discovery 與 validation 不算外部驗證。

## 示範

使用同一份 DE 結果比較：

1. 錯誤 background universe 與正確 universe。
2. 只看顯著 gene list 的 ORA 與完整 ranked list GSEA。
3. 顯示 top 20 redundant pathways，再依 shared genes 合併。
4. 在獨立資料集中檢查 effect direction，而不是只找另一個 p-value。

## 不深入

- 每個 pathway database 的 ontology 維護細節
- Network centrality 的完整數學推導
- 以 pathway 結果直接進行藥物推薦

## 決策題

**題目：** Interferon pathway FDR < 0.05，是否可寫成「腫瘤中的 interferon signaling 已被活化」？

**正確決策：** 不能只依 enrichment 結果下此結論。

**理由：** Enrichment 顯示相關 genes 在排序或 gene list 中集中；仍需確認方向、cell composition、gene-set 定義及蛋白／功能驗證。

## 講師檢查

- [ ] 所有示範提供 background universe
- [ ] 同時呈現 pathway 名稱與 leading-edge genes
- [ ] 指出至少一個 ID mapping loss
- [ ] 外部驗證與 discovery cohort 完全分離
