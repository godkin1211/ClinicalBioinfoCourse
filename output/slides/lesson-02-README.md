# 第二堂 HTML 投影片：癌症體細胞基因體分析

用 Chrome、Edge 等現代瀏覽器開啟 [lesson-02-somatic.html](lesson-02-somatic.html)。64 張、16:9；第 1–46 張為主課程，第 47–64 張為選讀附錄與參考資源。與第一堂視覺風格一致，採學員導向文字，不標示各部分授課時長。

敘事主線：為什麼需要癌症基因檢測 → 效益與限制 → 實務設計 → 採樣與製備 → 下機 QC → 生物資訊分析 → 結果解讀。主課程先建立全貌，命令與深入模型留在附錄。

## 加強說明版

2026-09-28 新增第 18 頁 FastQC 判讀，並將原第 40 頁拆成 TMB、MSI、HRD 三頁（現第 40–42 頁），共 64 頁。非封面頁皆有直接可見的「理解這一頁」：用具體例子、數字、讀圖順序或判讀步驟，補足原本只有關鍵詞的內容。

每頁（含封面與附錄）另有三段完整詳解，包含概念、推理與結論邊界；按 `E` 或「逐頁詳解」開啟，按 Esc 關閉。這是學員也能閱讀的說明，不是只對講師下指令的備註。

也可直接開啟 [完整逐頁詳解閱讀版](lesson-02-explanations.html)，依頁碼閱讀或使用瀏覽器列印。說明文字來源為 [lesson-02-slide-explanations.md](../../lessons/lesson-02-slide-explanations.md)，建置腳本會核對每個標題，避免投影片與詳解錯配。

## 內容導覽

| 頁次 | 主題 |
|---|---|
| 1–5 | 癌症分子差異、檢測的效益與邊界、學習路線 |
| 6–9 | 實務全流程、panel／WES／WGS 的選擇、somatic 來源、tumor–normal／tumor-only |
| 10–16 | 採樣與保存、病理評估、核酸萃取、文庫、FFPE、分子數及資料交接 |
| 17–20 | 樣本拆分／FASTQ QC、FastQC 圖表判讀、比對／逐區域覆蓋、QC 異常回饋與下一步 |
| 21–30 | 前處理、SNV/indel／CNV／SV 流程、normal／PoN、calling／filtering／annotation、資料格式 |
| 31–39 | 相同 5% VAF 的不同讀段證據、VAF／CCF、合成案例 A／B／C／D 判讀 |
| 40 | TMB：突變納入規則、分母與跨平台比較 |
| 41 | MSI：微衛星長度分布、模型與可評估性 |
| 42 | HRD：BRCA 證據、LOH／TAI／LST 疤痕與功能限制 |
| 43–46 | 液態切片、技術／生物／臨床三層判讀、自我檢核及總結 |
| 47–54 | 操作附錄：環境、檔案、建立練習、VCF 查詢、IGV、prepare.sh 與驗證 |
| 55–63 | 延伸附錄：方向性／duplex、VAF／CN 模型、縱向比較、抽樣、cohort 分母及名詞 |
| 64 | 來源與課後資源 |

## 操作

- 方向鍵、Page Up／Down、空白鍵：翻頁；Home／End：首末頁。
- `O`：目錄；`F`：全螢幕；Esc：關閉目錄。
- `E`：目前頁面的完整詳解；Esc：關閉詳解。開啟詳解期間，方向鍵不會切換背後的投影片。
- 判讀題點選「先想一想，再展開解析」。列印時解析一併顯示。
- 「列印全部」使用瀏覽器列印。建議啟用背景圖形，關閉頁首頁尾。
- `#slide-19` 等網址片段可跳到指定頁面。

單一 HTML 已內嵌文字、圖形與程式，播放不需網路或伺服器，不會自行執行投影片中的命令。外部來源連結需網路；教材、PDF 與腳本連結需保留本專案結構。

## 課堂使用界線

以講者示範、學員共同判讀為預設；不要求先會 command line。64 張不是全部必講；主課程在第 46 張結束，混合模型推導、命令列操作及抽樣機率為選讀。教學重點是從檢測目的連到資料來源、QC 決策與證據解讀。

所有數值案例為人工 chrToy 資料或明示的數學假設。第 18 頁為 FastQC 判讀指南，非實際檢體結果；第 33 頁是 ALT 支持讀段形狀示意，不是真實 IGV 截圖；第 40–42 頁為生物標記原理與假設案例，沒有執行檢測或提供通用治療閾值；第 59 頁與事件 C 的 CN 模型獨立於 toy BAM。完整 GATK／CNV／SV caller 不在實作範圍。課程不提供臨床處方或正式 actionability 分級；檢體與 QC 決策須依經驗證的方法及院內 SOP。

2026-09-27 已重跑既有合成練習並通過 verify.py。Windows／WSL 安裝及 IGV Desktop 操作仍需課前在授課電腦確認，瀏覽器排版測試不等於實體投影機測試。

## 維護與驗證

修改 [建置腳本](../../scripts/build-lesson02-slides.py) 或 [逐頁詳解文字](../../lessons/lesson-02-slide-explanations.md) 後，在專案根目錄執行（同時更新投影片與閱讀版）：

```bash
python3 scripts/build-lesson02-slides.py
```

只需 Python 標準函式庫，不會改動第一堂投影片。瀏覽器 QA 腳本 `scripts/check-lesson02-slides.cjs` 使用本機 Codex Playwright 與 Chrome 路徑，其他電腦需調整；播放 HTML 本身不需要它。

來源與數值：[lesson-02-slides-sources.md](../../sources/lesson-02-slides-sources.md)。檢查紀錄：[lesson-02-QA.md](lesson-02-QA.md)。
