# 第一堂合成資料示範

配合[詳細教材](../../lessons/lesson-01-materials.md)。資料由固定種子的 Python 標準函式庫產生，無病人資料、不需下載人類基因體。目標為教學，不是效能評估或臨床驗證。

## 執行

Windows 使用 WSL2 Ubuntu；安裝步驟見教材附錄。在本資料夾執行：

```bash
python3 generate.py practice01
cd practice01
PLINK=plink1.9 bash ../run-array.sh
bash ../run-sequence.sh
python3 ../verify.py .
```

手動安裝版若叫 `plink`，改成 `PLINK=plink`。產生器拒絕覆蓋既有目錄；分析腳本重跑則會替換同名結果。不要在研究資料目錄中執行。

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

Windows／WSL 安裝程序依官方文件核對，尚未在 Windows 主機實測。不同 PLINK 或 HTSlib 版本可能改變 PCA 方向、ROH 邊界或品質值；verify.py 不比對這些不穩定數值，也不宣稱驗證完整生物學正確性。
