# 第三堂投影片 QA

日期：2026-10-05。交付：56 頁 HTML 與 56 頁對應的詳解閱讀版。

## 已執行

- `python3 scripts/build-lesson03-slides.py`：成功建置；所有指定講義章節存在，每頁均有詳解。
- `python3 -m py_compile scripts/build-lesson03-slides.py`、`node --check scripts/check-lesson03-slides.cjs`：通過。
- `node scripts/check-lesson03-slides.cjs`：使用本機 Chrome，1440×900 與 1366×768 共 112 張頁面截圖；最終 `issues=[]`、`errors=[]`、`network=[]`。
- 56 頁逐頁檢查主文、標題、表格及圖片的水平越界與頁尾侵入；所有主文圖檔成功載入。
- 56 份詳解皆可開啟、滾動與關閉；圖檔可載入，本機連結存在；詳解開啟時方向鍵不誤切投影片。
- 驗證上一頁／下一頁、方向鍵、Home、目錄跳頁、E、Esc、全螢幕及 URL 頁碼。
- 列印模式顯示全部 56 頁；關閉 JavaScript 時保留全部投影片。
- 詳解閱讀版共有 56 個對應區塊，錨點無重複。
- 最後兩頁順序斷言：第 55 頁四工具比較，第 56 頁 OpenAI NGS Analysis Workbench。
- 視覺檢視全部 5 張 contact sheets；放大檢查封面、PCA、程式、junction、PSI 與末兩頁。

## 檢查過程調整

首次詳解圖檢查在圖片尚未載入完成前讀取狀態；檢查程式改為等待載入完成，再驗證圖片尺寸，不放寬失敗條件。首次 1366×768 封面截圖有縮放後畫面殘影；改為等待兩次 animation frame 再截圖，重跑並放大確認完整封面與頁尾正常。新增 PSI 全名及 0–1／百分比說明後再次重建、重跑，無越界。

## 科學與資料範圍

已核對合成輸出的基因數、顯著數、GENE0001 數值及四張圖的尺度。沒有把 VST 宣稱為 batch-corrected，沒有把未收縮 log2FC 當成已收縮結果；PSI 與結構示意均與正式剪接檢定分開。新增工具介紹有來源與查核日期，未宣稱執行四套網站或 Workbench 分析。

## 尚未測試

未在實體投影機、Windows／Linux 瀏覽器實測；未匯出新的投影片 PDF；列印模式檢查不等同紙本印刷驗證。沒有執行四個遠端 RNA-seq 服務、安裝它們或測試全班並行容量；上課前仍須以指定公開資料演練並準備離線備援。

詳細截圖與機器報告存於忽略追蹤的 `output/playwright/lesson-03/`；不放入公開 repository。既有講義 PDF 與其他課程未修改，無須重建。
