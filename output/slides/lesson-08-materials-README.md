# 第八堂 HTML 講義：閱讀與重新編譯

_Nextflow 工作流程入門｜單檔 HTML，含已執行的合成資料 MultiQC 報告_

---

## 📚 閱讀方式

開啟 [lesson-08-materials.html](lesson-08-materials.html)。這是完整講義，不是投影片；左側有章節導覽，第 6 節包含互動 QC 報告，可放大、另開或下載。正文、流程圖、QC 圖表與已保存的 AI 摘要均可離線閱讀。連到程式碼或其他教材的相對連結，需保留 repository 目錄；外部參考資料需連網。

嵌入報告來自 2026-11-03 真正執行的兩個合成樣本：四個 FASTQ，每檔只有 4 reads。它包含已取得的 Seqera AI 回覆，不會重新執行分析或呼叫 AI。報告副本加入禁止連外的 CSP，無須也不應輸入任何 token。原始檔未修改；發布副本替換個人本機路徑，並將舊 MultiQC 顯示成資料結構的 AI 回覆整理為最終文字，未改 QC 數值。

## 🔧 重新編譯

需求：Pandoc、Node.js、Python 3、Playwright 與 Chrome。可沿用此專案既有的本機瀏覽器依賴；其他電腦可設定 `PLAYWRIGHT_MODULE`（Playwright 套件路徑）與 `CHROME_PATH`。Mermaid 僅在編譯時使用，產物為靜態 SVG，不需讓讀者下載繪圖程式。

在 repository 根目錄執行：

```bash
mkdir -p tmp/lesson08
curl -fL https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js \
    -o tmp/lesson08/mermaid.min.js
node scripts/build-lesson08-handout.cjs
node scripts/check-lesson08-handout.cjs
```

預設讀取本機已存在的 `demos/nextflow-qc/results/seqera-ai-20261103/multiqc/multiqc_report.html`；這個原始執行目錄按專案規則忽略，不在 Git 中。其他電腦可先從講義下載內嵌報告，再明確提供路徑：

```bash
node scripts/build-lesson08-handout.cjs /absolute/path/to/lesson-08-multiqc-report.html
```

編譯器會檢查合成樣本名稱與摘要內容，不會發出 AI 請求。Markdown 為講義主來源；對應來源及報告 SHA-256 保存在 [build manifest](lesson-08-materials-build.json)。此次依目前工作檔編譯，包含原有未提交的講義日期修改；該日期修改未被納入本次來源提交。

## ✅ 本次驗證

已在本機 Chrome 驗證：10 章完整正文、7 節點流程圖、Gmail 與 secrets 章節、非空最終 AI 摘要、四個 read 檔、Plotly 圖表、放大／另開報告，以及相對連結的檔案存在。手機 390px 寬度未出現整頁橫向溢出。自動檢查未發現 JavaScript 執行錯誤或自動 HTTP／HTTPS 請求。

畫面截圖保存在忽略目錄 `output/playwright/lesson-08/`，不提交。這是編譯與閱讀驗證，不代表 AI 摘要已經臨床驗證；Gmail 仍僅有設定與模板檢查，沒有實際寄信。
