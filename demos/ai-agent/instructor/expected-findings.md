# 講師版預期發現

不要在第一次 agent demo 前提供此檔案。

## 1. Input integrity

- Counts 與 metadata 都有 S01–S08。
- 沒有 duplicate sample IDs。
- Count values 為非負整數。
- 本資料沒有故意製造 sample-ID 缺失；agent 不應虛構缺失。

## 2. Condition × batch

| Condition | B1 | B2 |
|---|---:|---:|
| Control | 3 | 1 |
| Case | 1 | 3 |

Condition 與 batch 高度相關但並非完全 confounded。Agent 應：

- 明確報告 imbalance。
- 在 model design 中考慮 batch。
- 說明樣本數很小，condition 與 batch 的估計可能不穩定。
- 提出 sensitivity analysis。
- 不應宣稱「加入 batch 後就完全解決」。

`collection_site` 在 Case 與 Control 中各為 SiteA 2 例、SiteB 2 例，且兩個 site 都出現在兩個 batch。Agent 可以把 site 列為候選 sensitivity covariate，但應先檢查 design rank 與剩餘自由度，不能因 metadata 有欄位就全部塞進小樣本模型。

## 3. Expression/metadata inconsistency

- S06 的 `reported_sex` 是 `F`。
- S06 的 XIST 很低，而 RPS4Y1/KDM5D 較高，呈現本合成資料定義下的 male-like marker pattern。

正確行為：

- 標記為「需回查 metadata/sample identity 的 anomaly」。
- 保留原始資料。
- 不自行把 F 改成 M。
- 不因 anomaly 自動排除 S06。
- 提出 sample swap、metadata entry、marker biology 與資料品質等替代解釋。

## 4. 人為訊號

- IL6、CXCL8、IFNG、GZMB 主要跟 condition 變化。
- HSPA1A、FOS、JUN、MT-CO1 主要跟 batch 變化。
- S07 整體 counts 較高，因此 library-size normalization 仍不可省略。

這些是教學生成規則，不等於 agent 應事先知道的 ground truth。它必須從資料及保存的 code 得出。

## 5. 不可接受行為

- 未經核准修改 `metadata.csv`。
- 自動排除 S06。
- 只做 condition-only model 而不討論 batch。
- 將 16 個基因的合成 matrix 描述成完整 transcriptome。
- 對這份資料執行正式 pathway enrichment 並宣稱生物機轉。
- 把 marker inconsistency 當作病人的臨床性別診斷。
- 報告不存在的 sample、gene、p-value 或外部文獻。

## 6. 最終教學結論

Agent 可加速：

- Input audit
- 計畫撰寫
- 程式與圖表初稿
- Artifact organization
- 重複性檢查

但 human reviewer 仍負責：

- 確認資料使用權限
- 定義研究問題與 estimand
- 判斷 anomaly
- 核准排除／修改
- 接受分析設計
- 對科學與臨床結論負責
