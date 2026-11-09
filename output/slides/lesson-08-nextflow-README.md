# Nextflow 課程投影片

## 目前分享版本

`lesson-08-nextflow-numbered.pptx` 以目前手動編輯的 54 頁 `lesson-08-nextflow.pptx` 另存。首頁不標頁碼，其餘 53 頁將既有頁碼移至右上角，保留原有頁序、內容、母片、圖像及 PowerPoint 原生頁碼欄位，沒有重建講義內容。原先手動編輯檔案不覆寫。

`scripts/number-lesson08-slides.cjs` 只調整頁碼 shape 的位置與文字樣式；逐一比對其他 shape 與 ZIP 成員皆未改變。`lesson-08-nextflow-numbered-build.json` 記錄這次的輸入、輸出雜湊及頁碼設定。重新執行時可傳入來源與新的輸出檔名，既有檔案不會覆寫。

以下記錄最初由講義產生的 52 頁版本，不包含後續手動新增或調整的內容。

## 最初製作版本

- 成品：`lesson-08-nextflow.pptx`，52 頁、16:9，可編輯文字、程式碼與表格。
- 第 1–40 頁：課堂主體、Summary 與資源連結。
- 第 41–52 頁：課後安裝、程式導讀、報告開啟與 Gmail 設定附錄。
- 依據：`lessons/lesson-08-materials.md` 的目前工作副本，包含原先既有的課程日期 `2026-11-10`。本次未變更講義正文。
- 範本：使用者提供的 `Nextflow Intro 2026.pptx`。保留深紫背景、薄荷綠重點色、母片、封面圖、圖示與 process 示意。舊活動、講者與統計數字沒有沿用為課程內容。
- 字體：範本的 Inter／Inter Light，程式碼使用 Menlo。中文由可用的中文字型補字。其他電腦若缺少字體，PowerPoint 可能替換字體，正式授課前請在該電腦確認換行。

## 使用與內容邊界

操作指令均以 `demos/nextflow-qc` 為起點。程式片段供閱讀，請使用 repository 的完整 `main.nf` 與設定檔執行。

QC 畫面取自已執行的合成測試資料，每個 FASTQ 僅 4 reads，不能建立臨床品質門檻。投影片不嵌入可重新操作的 MultiQC 程式，互動報告仍在 `lesson-08-materials.html` 及講義分享套件中。

一般 Docker 示範不呼叫 AI。`nextflow secrets` 登錄不會自動取代目前 `seqera_ai` profile 的唯讀 token 檔掛載。Gmail 設定只驗證過語法與模板，未驗證實際認證或信件送達。本次製作投影片沒有執行新分析、呼叫 AI 或寄信。

## 製作來源與重建

1. `scripts/lesson08-deck-content.mjs`：每頁的學員內容與對應講義章節。
2. `scripts/build-lesson08-deck.mjs`：Artifact Session callbacks。先匯入使用者原始 17 頁範本，再呼叫 `prepare` 複製／保留版面，依序小批呼叫 `buildBatch`。每次傳入 `input: {start, end, assetsRoot}`，索引從 0 開始，end 不含在內。
3. `scripts/capture-lesson08-deck.cjs`：從既有去敏感化 HTML 擷取流程圖與實際 QC 表格，產出 `assets/lesson-08/`。此步禁止外部 HTTP 請求。
4. 在同一 session 檢視並修正後匯出 PPTX draft，再執行 `scripts/finalize-lesson08-deck.mjs /absolute/path/to/draft.pptx`。設定 `RUNTIME_NODE_MODULES`、必要時設定 `PRESENTATIONS_SKILL_DIR` 與 `RUNTIME_PYTHON` 為目前安裝的工作環境路徑。Finalizer 不覆寫既有成品，修訂時請先選新版本檔名。

原始範本不另外公開重發，重建時需保留使用者提供的檔案。製作內容與成品可在本 repo 追蹤。`lesson-08-nextflow-build.json` 記錄講義雜湊、成品雜湊與頁面對應。

## 文件查核來源

延伸功能、快取與 AI 摘要於 2026-11-09 對照 [26.10 migration](https://docs.seqera.io/nextflow/migrations/26-10/)、[caching and resuming](https://docs.seqera.io/nextflow/cache-and-resume/)、[MultiQC AI summaries](https://docs.seqera.io/multiqc/ai/) 官方文件。其他技術背景與操作限制沿用講義及其參考資料。
