# 2026-10-24 LDTs 生物資訊專題

- [HTML 投影片](ldt-20261024-bioinformatics.html)：32 頁，主課程 28 頁＋備查 4 頁，16:9。
- [逐頁詳解](ldt-20261024-explanations.html)：完整概念、算例前提與限制，適合課後閱讀。
- [PDF 投影片](../pdf/ldt-20261024-bioinformatics.pdf)：同版面備援，包含全部 32 頁，不包含互動詳解。
- [濃縮架構與原課對應](../../lessons/ldt-20261024-outline.md)、[來源及圖像紀錄](../../sources/ldt-20261024-sources.md)。

講者：奇美醫院精準醫學核心實驗室組長邱家軍。面向沒有程式經驗的臨床／實驗室人員。原九堂系列不變，此檔為另外整理的一小時專題。

## 播放

直接用 Chrome 或 Edge 開啟 HTML。方向鍵、空白鍵翻頁；`E` 展開目前頁詳解、`Esc` 關閉；`O` 目錄；`F` 全螢幕；Home／End 到首尾。開啟詳解時，方向鍵不會換投影片。

正文、八張原創 SVG 與一張官方 IGV 範例已嵌入 HTML，可離線播放；外部來源連結需連網。獨立閱讀版與原課連結需保留專案相對路徑，單獨攜帶主 HTML 仍可使用內嵌逐頁詳解。PDF 可備用，但不含可展開說明。

## 重建

先安裝 Python 3 與 Pandoc。在專案根目錄執行：

```bash
python3 scripts/build-ldt-slides.py
node scripts/check-ldt-slides.cjs
```

第二步使用現有 Playwright 與 Chrome；可透過 `PLAYWRIGHT_MODULE`、`CHROME_PATH` 指定本機位置。它會產生 QA 截圖、檢查互動，並以瀏覽器列印同時產生 PDF。未安裝這些工具仍可直接使用已生成的 HTML／PDF。

PDF 的補充驗證使用 Poppler、Python 的 Pillow、pypdf 與 pdfplumber：

```bash
pdftoppm -png -scale-to 1280 output/pdf/ldt-20261024-bioinformatics.pdf output/playwright/ldt-20261024/pdf
python3 scripts/check-ldt-pdf.py
```

自動檢查之外，仍需目視檢查 HTML 截圖、PDF contact sheets 與原理圖標籤。尚未在實際會場投影機測試，建議授課前以主課程 28 頁完整預演一次，再依聽眾背景取捨備查內容。

`scripts/build-ldt-slides.py` 重用第三堂的基礎版型與導覽，不修改前三堂的來源或產物。八張圖的可編輯 SVG 另存 `figures/ldt-20261024/`。合成圖只說明原理，不能當作實驗室性能證據。官方 IGV 圖保留出處；未執行臨床分析。PDF 與畫面 QA 結果見 [檢查紀錄](ldt-20261024-QA.md)。
