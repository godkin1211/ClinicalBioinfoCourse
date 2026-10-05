# 第三堂 HTML 投影片

[開啟投影片](lesson-03-bulk-rnaseq.html) · [逐頁詳解閱讀版](lesson-03-explanations.html) · [完整 PDF 講義](../pdf/lesson-03-materials.pdf)

56 頁、16:9、繁體中文學員版。講師：奇美醫院精準醫學核心實驗室組長邱家軍。

## 內容路線

| 頁次 | 內容 |
|---|---|
| 1–5 | RNA、gene／transcript、bulk 混合訊號與兩條分析分支 |
| 6–9 | 臨床研究問題、病人單位、批次混雜、metadata |
| 10–14 | RNA 品質、富集策略、paired-end／方向性、常見格式與座標 |
| 15–20 | FastQC、RNA 特有 QC、比對、定量與 count matrix |
| 21–28 | CPM／TPM、組成偏差、size factor、VST、PCA 與熱圖 |
| 29–35 | 生物變異、負二項、design／contrast、配對、效應量、FDR 與 NA |
| 36–41 | 合成實作範圍、程式導讀、結果表、MA／volcano 與判讀練習 |
| 42–52 | 可變剪接背景、五類事件、DGE／DTE／DTU／DEU、junction、PSI／ΔPSI、工具與驗證 |
| 53–54 | 資料交付、重現指令與課後資源 |
| 55 | BEAVR、RNAdetector、RaNA-seq、iDEP 比較；依本堂目標推薦 iDEP |
| 56 | OpenAI NGS Analysis Workbench：定位、核准流程與限制 |

投影片搭配完整講義使用；不需要逐字念完全部詳解。第 14、30、32、37、50 頁是可依學員背景選讀的技術深化內容，目錄可直接跳頁；不標示每部分教授時長。

## 操作

- Chrome／Edge 等現代瀏覽器直接開啟 HTML；正文與四張實際合成分析圖已內嵌，可離線播放。
- 方向鍵、Page Up／Down、空白鍵翻頁；Home／End 到首末頁。
- `O` 開啟目錄，`E` 開啟該頁詳解，`F` 全螢幕，Esc 關閉對話框。
- 詳解由完整講義擷取對應段落，包含背景、算例與限制；另外提供可連續閱讀／列印的 HTML。
- 列印全部時開啟背景圖形，關閉瀏覽器頁首頁尾。未啟用 JavaScript 時顯示全部投影片。
- 外部參考與工具服務需網路；PDF／程式／詳解圖片等相對連結需保留 repository 結構。投影片中的命令不會在瀏覽器執行。

四工具與 Workbench 是文件查核的介紹，不是本次已執行的分析。課前另測平台功能與權限，使用公開或合成資料；不任意上傳院內病人資料。

## 維護與驗證

```sh
python3 scripts/build-lesson03-slides.py
node scripts/check-lesson03-slides.cjs
```

建置需要 Python 3 與 Pandoc（沿用講義工具），不需要額外 Python 套件。修改投影片主文在 `scripts/build-lesson03-slides.py`；一般詳解來自 `lessons/lesson-03-materials.md`，最後兩頁補充文字在建置程式中。講義若修改，除 PDF 外也要重建本堂 HTML。

檢查程式沿用專案本機的 Playwright／Chrome；其他環境可用 `PLAYWRIGHT_MODULE` 與 `CHROME_PATH` 指定路徑。截圖與 `qa.json` 放在忽略追蹤的 `output/playwright/lesson-03/`。結果見 [QA 紀錄](lesson-03-QA.md)，方法與工具來源見 [來源記錄](../../sources/lesson-03-slides-sources.md)。
