# 第一、二堂跨作業系統實作附錄：查核紀錄

核對日期：2026-09-30。用途為學員安裝與操作，不是新增臨床建議。沿用合成資料與原分析參數，未改變演算法或預設答案。

## 官方來源與採用範圍

| 來源 | 本次採用內容 |
|---|---|
| [Microsoft WSL 安裝](https://learn.microsoft.com/en-us/windows/wsl/install) | 管理員 PowerShell、發行版選擇、重新開機、Linux 使用者、VERSION 2 的確認 |
| [Microsoft WSL 命令](https://learn.microsoft.com/en-us/windows/wsl/basic-commands) | list／install／set-version 與發行版名稱 |
| [Homebrew 官網](https://brew.sh/)與[安裝文件](https://docs.brew.sh/Installation) | 官方安裝指令、shellenv、Apple Silicon／Intel 的 prefix 與支援條件；未假設所有舊 Mac 均可用 |
| [SAMtools formula](https://formulae.brew.sh/formula/samtools)與[BCFtools formula](https://formulae.brew.sh/formula/bcftools) | brew 套件名稱；教材不宣稱安裝最新版後一定等同已測版本 |
| [PLINK 1.9](https://www.cog-genomics.org/plink/1.9/) | stable macOS 官方連結，固定 2026-09-27 版本；不以 PLINK 2 取代 |
| [Ubuntu noble plink1.9](https://packages.ubuntu.com/en/noble/plink1.9) | universe 套件、列出的 amd64／armhf 架構，未提供 ARM64；不把 Windows ARM 的 WSL 當 x86_64 |
| [Apple Rosetta](https://support.apple.com/en-us/102527) | 僅在另用 Intel-only 舊程式時另核對，這次的 Universal PLINK 不需因此強制安裝 Rosetta |
| [IGV Desktop 下載](https://igv.org/doc/desktop/DownloadPage/) | 優先穩定版與附 Java 套件；IGV 2.19.1 起要求 Java 21；Linux 包附 x64 Java，其他架構另備相容 Java |
| [IGV reference](https://igv.org/doc/desktop/UserGuide/reference_genome/)與[alignment](https://igv.org/doc/desktop/UserGuide/tracks/alignments/viewing_alignments_basics/) | reference、讀段軌道與顯示限制；沿用教材既有核對內容 |

科學寫作技能用於學員操作順序、定義與失敗處理；research-lookup 的外部服務金鑰未設定，改以官方網頁直接核對，不宣稱使用了該服務產生的研究報告。

## 實際執行與未驗證範圍

- 官方 macOS 檔案：`plink_mac_20260927.zip`。下載解壓後以 `file` 確認同時包含 x86_64、arm64；`--version` 為 PLINK v1.9.0 64-bit（27 Sep 2026）。這是實際檔案檢查，不只由「macOS 64-bit」標籤推斷。
- 本機 macOS arm64，Python 3.14.3、SAMtools 1.22、BCFtools 1.22、HTSlib 1.22.1。
- 新的合成練習目錄使用含空白的路徑，第一堂兩條腳本及第二堂 prepare／verify／models 均通過；完整數值見各 demo README。
- 本次未在 Windows／WSL、原生 Linux、ARM Linux 主機執行；未重新安裝整套 Homebrew／WSL，未以三種系統逐一操作 IGV GUI。教材將步驟核對與實際測試分開標示。
- 原 macOS 2026-09-13 測試紀錄保留，不用此次較新版本取代歷史證據。

## 教材一致性與交付

- 兩份講義均保留完整附錄，不要求離線 PDF 讀者跳至另一堂才找得到安裝步驟。
- 共用 A1–A6 保持一致；第一堂 A7–A9 與第二堂 A7–A10 分別說明完整執行、成功結果與排錯。
- 新練習使用 `practice-local01`，避免第一堂已追蹤的 `practice01` 造成 FileExistsError；僅忽略個人 `practice-local*` 結果，不刪除既有範例。
- 這次更新講義、demo 操作入口與 PDF，未修改 HTML 投影片；投影片原本的簡短 Windows 附錄不等於此次完整跨系統手冊。
- 重新編譯第一堂 17 頁、第二堂 18 頁 PDF；兩份的文字、講者、跨系統關鍵字與頁面邊界檢查通過。全部頁面已渲染成圖片檢視，並放大檢查 macOS 安裝與第二堂執行頁，未見裁切／重疊。
- 第一堂 33 個、第二堂 29 個 Bash 區塊通過 `bash -n`；本地連結與共用 A1–A6 一致性核對通過。測試與 PDF 渲染中間檔留在 Git 忽略的 `tmp/`。
