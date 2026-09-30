# 第一堂合成資料示範

配合[詳細教材](../../lessons/lesson-01-materials.md)。資料由固定種子的 Python 標準函式庫產生，無病人資料、不需下載人類基因體。目標為教學，不是效能評估或臨床驗證。

## 執行

初次操作請先照[教材附錄 A](../../lessons/lesson-01-materials.md#附錄-a依作業系統安裝到第一次成功執行)：A2 為 Windows／WSL2，A3 為 macOS（Intel／Apple Silicon），A4 為 Linux（Ubuntu／Debian），A5 下載專案，A7 從產生資料到 PASS，A8 保存版本，A9 排錯。安裝涵蓋 Git、Python、SAMtools、BCFtools、PLINK 1.9；ARM Linux 的 PLINK 限制有另外說明。

已完成安裝者，在 Windows 的 Ubuntu、macOS Terminal 或 Linux Terminal 執行；專案路徑不同時調整第一行。Mac 新開視窗請先依 A3 設定個人工具 PATH。

```bash
cd ~/ClinicalBioinfoCourse/demos/lesson-01-genomics
python3 generate.py practice-local01
cd practice-local01
PLINK=plink1.9 bash ../run-array.sh
bash ../run-sequence.sh
python3 ../verify.py .
```

手動安裝版若叫 `plink`，改成 `PLINK=plink`；附錄的 macOS 路線已將它安裝為 `plink1.9`。產生器拒絕覆蓋既有目錄；重做改用 `practice-local02` 並同步更改 `cd`。不要使用已隨教材提供的 `practice01`。分析腳本重跑會替換同名結果，不要在研究資料目錄中執行。

成功時最後應顯示 `PASS: sizes, missingness, duplicate, PCA, ROH, called SNV and review cases`。附錄另提供 log、退出碼、逐檔核對與版本紀錄，不以「有產出檔案」取代驗證。

## 內容與界線

- `generate.py`：40 樣本、6,000 SNP 的 PED/MAP；理想化 intensity.csv；2 kb reference、40 條 FASTQ reads 與人工指定位置的 SAM；獨立編寫的 review.vcf。
- `run-array.sh`：missingness、MAF、HWE、heterozygosity、兩階段缺失篩選、LD pruning、IBD、PCA、ROH。
- `run-array.sh` 已逐行註解 Bash 設定、參數、輸入／輸出及判讀限制；搭配[第 20 頁完整說明（原第 19 頁）](../../lessons/lesson-01-slide-19-array-commands.md)。整份執行不會在 QC 報表產生後暫停；若要先人工判讀，請分開執行指令。
- `run-sequence.sh`：SAM 轉 BAM、排序索引、depth、最小 variant calling、VCF 查詢。
- `verify.py`：確認輸出關鍵值，避免把「程式結束」誤當「教材結果正確」。

SAM 已比對，不是 aligner 的結果；不包含原始 array calling、性染色體檢查、真實族群模擬、正式 CNV/SV calling 或 joint genotyping。review.vcf 是人工案例，不能當成 run-sequence.sh 的偵測結果。PCA 留有已知重複樣本，故只供問題展示，不可直接作關聯分析。

## 已實測結果（2026-09-13）

環境：macOS，Python 3.9.6；PLINK v1.9.0-rc1 64-bit（9 Sep 2026）官方 macOS 執行檔、SAMtools 1.22、HTSlib 1.22.1、BCFtools 1.22。

| 檢核 | 結果 |
|---|---|
| 原始尺寸 | 40 人 × 6,000 SNP |
| S40 missingness | 2,000/6,000 = 0.333333… |
| v1 missingness | 11/40 = 0.275 |
| 分階段 QC 後 | 39 人 × 5,999 SNP |
| S01/S02 | PI_HAT=1 |
| PCA | 39 筆樣本、4 個 PC 座標 |
| ROH | S03 有一段 chr1 ROH |
| 真正執行 caller 的輸出 | chrToy:1000 A>C，GT=0/1、DP=40、AD=20,20 |
| 人工 VCF 案例 | 四筆資料均可被 BCFtools 正確解析 |

選用延伸單元也已實測：移除已知合成複本後為 38 人，重新 pruning 與 PCA 成功。

2026-09-30 再驗證：macOS arm64、Python 3.14.3、官方 PLINK v1.9.0（27 Sep 2026，Universal binary）、SAMtools／BCFtools 1.22、HTSlib 1.22.1。在新目錄（含空白路徑）重建資料、執行兩條流程及 `verify.py`，上述尺寸與 SNV 均符合預期，完整 PASS。未重新安裝整個 macOS 環境。

Windows／WSL 與 Linux 安裝程序依官方文件核對，本次未在這些主機實測。不同 PLINK 或 HTSlib 版本可能改變 PCA 方向、ROH 邊界或品質值；verify.py 不比對這些不穩定數值，也不宣稱驗證完整生物學正確性。安裝來源與相容性見[查核紀錄](../../sources/lesson-01-02-practical-setup-sources.md)。
