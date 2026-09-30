# Lesson 07 — 空間轉錄體分析

## 課程目標

完成本堂後，學員能：

1. 比較 spot-based、single-cell resolution 與 imaging-based spatial assays 的資訊與限制。
2. 說明影像配準、spatial domain、neighborhood、deconvolution 與 spatially variable genes。
3. 辨認組織結構、cell composition、technical artifact 與空間自相關造成的假象。

## 臨床案例

分析腫瘤侵襲前緣是否存在免疫排斥 niche，並比較腫瘤核心與邊緣。

- 決策：需要何種 resolution、多少張切片／病人、如何定義 region 與驗證？
- 故意問題：只分析一位病人的一張切片，卻推論普遍臨床機轉。

## 60 分鐘流程

| 時間 | 段落 | 教學內容 | 學員活動 |
|---:|---|---|---|
| 0–10 | 臨床問題 | Spatial question 不只是「把 UMAP 放回切片」 | 定義 region / neighborhood question |
| 10–20 | 技術與檔案 | Capture spot、single-cell resolution、imaging panel、image + coordinates + matrix | 選擇 assay |
| 20–35 | 分析原理 | Image registration、QC、domain、spatial neighbors、SVG、deconvolution、autocorrelation | 找出分析單位 |
| 35–55 | 示範 | H&E overlay、domain map、cell-type proportion、neighborhood enrichment | 區分 composition 與 state |
| 55–60 | 決策題 | 免疫基因高是否等於 immune infiltration？ | 列出替代解釋 |

## 核心資料流

```text
patient → tissue section → image + spatial assay
        ↓
registration + spot/cell QC + coordinate system
        ↓
expression matrix linked to spatial coordinates
        ↓
domains / neighbors / SVG / deconvolution
        ↓
patient-aware spatial comparison
        ↓
pathology or orthogonal validation
```

## 必講概念

- Resolution、gene coverage、tissue area、fresh/fixed specimen 與成本之間有 trade-off。
- Spot-based 資料可能混合多種細胞；deconvolution 依賴 reference 與 model assumptions。
- Spatial autocorrelation 使鄰近 observations 不獨立。
- Tissue edge、fold、necrosis、low RNA quality 與 segmentation error 可產生空間 pattern。
- Domain 名稱是 analysis-derived，不自動等於病理定義。
- 單張切片內很多 spots 不等於很多病人。
- Spatial association 不證明直接 cell–cell interaction 或因果。

## 示範

以公開 tumor spatial dataset：

1. H&E 與 capture grid／segmentation overlay。
2. Spot/cell QC map，辨認 tissue edge 與低品質區。
3. Spatial domain 與 pathologist annotation 對照。
4. Deconvolution 前後比較 immune-rich region。
5. 將同一病人的多 spots 與多病人的 replication 分開呈現。

## 不深入

- 各廠牌完整 wet-lab protocol
- 所有 spatial statistics
- 3D reconstruction

## 決策題

**題目：** 某些 tumor-edge spots 的 immune genes 較高，是否可直接宣稱 immune infiltration 增加？

**正確決策：** 不可直接宣稱。

**理由：** 需排除 spot composition、ambient signal、tissue quality、region definition 與病人間差異，並以病理或其他方法驗證。

## 講師檢查

- [ ] 清楚標示 patient、section、spot/cell 三個層級
- [ ] 同時呈現 histology 與 molecular signal
- [ ] 不把 deconvolution proportion 當作直接測量真值
- [ ] 結果有跨病人或正交驗證策略
