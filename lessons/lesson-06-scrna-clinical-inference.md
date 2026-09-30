# Lesson 06 — Single-cell RNA-seq：比較與臨床推論

## 課程目標

完成本堂後，學員能：

1. 使用 marker evidence、reference mapping 與 biological context 評估 cell annotation。
2. 區分 batch integration、cell-state visualization 與 patient-level group comparison。
3. 避免把細胞當成獨立病人，並理解 pseudobulk 與 compositional analysis 的角色。

## 臨床案例

比較 4 位 responder 與 4 位 non-responder 的腫瘤 single-cell RNA-seq，觀察到 responder 有較多「exhausted T cells」。

- 決策：差異來自 cell proportion、cell state、batch 或 annotation 嗎？
- 故意問題：把 40,000 個細胞當作 40,000 個 independent replicates。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–10 | 問題 | Cell type、cell state、abundance 與 patient outcome | 定義 estimand |
| 10–20 | Annotation | Marker panel、negative markers、reference mapping、uncertainty | 審核一個過度精細 annotation |
| 20–35 | Integration 與比較 | Batch correction、overcorrection、pseudobulk、mixed models、composition | 找出 pseudoreplication |
| 35–55 | 延伸推論 | Trajectory、RNA velocity、cell–cell communication 的假設與限制 | 將結論分為 evidence/inference/speculation |
| 55–60 | 決策題 | 細胞多是否等於 replicate 多？ | 寫出有效樣本數 |

## 核心資料流

```text
QC-reviewed cells
      ↓
annotation with uncertainty
      ↓
patient-aware integration and visualization
      ↓
cell abundance analysis + pseudobulk state comparison
      ↓
sensitivity analysis across annotations / methods
      ↓
patient-level, bounded clinical inference
```

## 必講概念

- Marker expression 必須看組合、negative evidence 與資料品質。
- Reference mapping 會繼承 reference taxonomy 與 training bias。
- Integration 用於處理 unwanted variation，但可能移除真實 disease biology。
- Group comparison 的 replicate 通常是 patient，而不是 cell。
- Pseudobulk 保留 patient-level replication，適合許多 cell-type-specific DE 問題。
- Cell proportion 是 compositional data；一類增加會影響其他類的相對比例。
- Trajectory 表示 model-implied ordering，不等於已直接觀察 lineage。
- Ligand–receptor co-expression 不等於已證實 cell–cell signaling。

## 示範

展示同一資料的三種錯誤／改進：

1. Cell-level t-test 產生大量極小 p-values。
2. Patient-level pseudobulk 後 evidence 明顯改變。
3. Integration 前後 disease-specific state 消失，要求判斷是去除 batch 還是 overcorrection。

最後將一段結果改寫為：

- **Observed evidence**
- **Model-dependent inference**
- **Requires experimental validation**

## 不深入

- 所有 integration benchmark
- RNA velocity kinetic model 推導
- 完整 ligand–receptor database 比較

## 決策題

**題目：** 每組各 4 位病人、每位約 5,000 個細胞，能否宣稱每組 n=20,000？

**正確決策：** 不能。

**理由：** 對 patient-level condition effect 而言，每組通常是 n=4；細胞是巢狀於病人的 observations。

## 講師檢查

- [ ] 所有 group comparison 標示 patient 數
- [ ] Annotation 有 unknown/uncertain 選項
- [ ] Integration 前後都檢查 known biology
- [ ] Trajectory 與 communication 使用限制性語言
