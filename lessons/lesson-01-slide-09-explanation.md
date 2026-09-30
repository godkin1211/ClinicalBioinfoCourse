# 第九頁補充講解：Hard call 留下答案，卻壓縮了證據

本頁要傳達的重點是：**基因型是分析結果，不是原始測量；相同基因型標籤，可能來自不同品質的證據。**

## 可直接搭配投影片講解的文字

「前面我們看到，晶片先量到兩種 allele 的訊號，演算法再把樣本放到群聚圖上，判斷它比較符合 AA、AB 還是 BB。當程式最後選定一種基因型，例如 AB，這個離散的標籤就叫 hard call。如果證據不夠可靠，可以不給基因型，留下 no-call；hard 並不是『一定正確』的意思。

「現在看表格。假設同一位點有兩個樣本：樣本 1 靠近 AB 群的中心，樣本 2 靠近 AB 群的邊緣。兩者都達到本次分析的判定門檻，所以最後都得到 AB，但樣本 2 的訊號較不符合典型群聚，判定品質可能較低。我們把強度、群聚位置和品質分數拿掉，只看兩個 AB，就無法分辨這個差異。

「這不是說 hard call 沒有用。它讓資料容易整理成『樣本乘以位點』的表格，可以計算 allele frequency，也可以進行適當 QC 後的 PCA、親緣或關聯分析。但它回答的是『被判成哪一類』，不是『原始訊號長什麼樣、這個判定有多可靠』。

「例如幾個月後想重新檢查可疑樣本、換一套群聚模型，或進行以訊號強度為基礎的 CNV 分析，單靠 AB 這兩個字，無法還原當初 A、B 各有多強，也無法完整重建 BAF 與 LRR。因此，基因型表可以是交付成果之一，但不應是唯一保存的資料。」

## 這頁的三個層次

| 層次 | 代表資訊 | 能回答什麼 |
|---|---|---|
| 測量與處理後訊號 | 原始／正規化強度、群聚位置 | 偵測到什麼？訊號是否偏離典型模式？ |
| 品質與衍生指標 | GenCall score、BAF、LRR | 判定品質如何？allele 比例或總強度是否異常？ |
| Hard call | AA、AB、BB；未判定則 no-call | 演算法最後選定哪個基因型？ |

GenCall score 是判定品質指標，不能直接當成「正確率百分比」。BAF 反映相對 B allele 訊號，LRR 反映總訊號相對預期的偏離；它們由訊號、正規化及群聚參考等資訊產生，不是只用 AA／AB／BB 三種標籤就能精確還原。BAF 不應直接簡化成把 AA、AB、BB 一律填成 0、0.5、1。

## 「壓縮」的意思與例外

這裡的壓縮是**資訊摘要**，不是 ZIP 壓縮，也不是呼叫基因型時一定會刪除原始資料。多種不同訊號都可以得到同一個 AB，因此由 AB 無法反推唯一的原始訊號。

完整的分析報表可以同時保存 hard call、品質與強度欄位；只有只保留 genotype 標籤時，這些差異才會在交付資料中消失。僅憑 hard calls 仍可做某些分析，例如 ROH；本頁並不是說沒有強度就完全不能做任何區域分析，而是不能據此完整重建原始強度、重做 intensity-based CNV 分析或完整稽核 calling。

## 實際應保存哪些資料？

- 原始訊號檔：依平台保存 IDAT／CEL，以及樣本對照資料。
- 處理後資料：genotype、no-call、可取得的品質分數、正規化強度及 BAF／LRR。
- 重現分析所需資訊：晶片 manifest、cluster reference、reference build、軟體版本、參數、QC 與人工修改紀錄。

## 課堂提問

「兩個樣本在同一位點都寫 AB，是否代表兩個判定一樣可靠？」

預期回答：不一定。要回到強度、群聚位置及品質分數檢查；若只剩 AB 標籤，就沒有足夠資訊回答。

「只收到 PLINK 的 BED／BIM／FAM，是否足以重新分析晶片原始訊號？」

預期回答：不夠。這組 genotype 檔案不是晶片原始強度資料；須另索取對應的訊號、品質與處理紀錄。

## 來源與範例限制

- [Illumina：Infinium Genotyping Data Analysis](https://www.illumina.com/Documents/products/technotes/technote_infinium_genotyping_data_analysis.pdf)：群聚位置與 GenCall 品質指標。
- [Illumina：DRAGEN Array Output Files](https://help.connected.illumina.com/dragen-array/product-guides/output-files)：genotype、GC score、BAF 與 LRR 等可保存欄位。

表格是教學假設，不是實測資料，也不提供通用判定門檻。實際品質評估需考慮平台、演算法、群聚模型與多項 QC 指標，不能只依目視距離做判定。
