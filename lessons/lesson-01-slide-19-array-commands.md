# 第 20 頁：先保留 QC 報表，再篩選

新增檔案格式總覽後，由原第 19 頁順延；檔名保留以維持連結。

這四行不是同時執行的四種檢查，而是依序完成「轉格式 → 留下篩選前的證據 → 篩樣本 → 篩位點」。先知道哪些資料有問題，再決定要排除什麼，才能說明最後留下的資料從哪裡來。

投影片顯示 `plink1.9`；[完整腳本](../demos/lesson-01-genomics/run-array.sh) 使用 `"$PLINK"`，讓你可以指定執行檔名稱或路徑。腳本內已逐行解釋 Bash 設定，以及後續的 LD pruning、親緣、PCA 與 ROH 指令。

## 執行前先確認

- 目前所在目錄應是 `generate.py` 產生的練習資料夾，內有 `array.ped` 與 `array.map`。腳本本身不會切換目錄。
- `array`、`raw`、`qc`、`sample_qc`、`clean` 都是檔名前綴，不是資料夾名稱，也不是 PLINK 保留字。
- `--` 開頭的是選項；有些後面要接值，例如 `--out raw`，有些只是啟用功能，例如 `--missing`。
- 每次執行另有對應前綴的 `.log`，應與報表一起保存。重跑會替換同名輸出，請使用獨立的練習目錄。

## 第 1 行：把 genotype 轉成適合分析的格式

```bash
plink1.9 --file array --make-bed --out raw
```

| 部分 | 意義 |
|---|---|
| `plink1.9` | 啟動 PLINK 1.9 程式。 |
| `--file array` | 讀取 `array.ped` 的樣本／基因型與 `array.map` 的位點資訊。 |
| `--make-bed` | 產生 PLINK 二進位 genotype 三件組。 |
| `--out raw` | 將輸出前綴命名為 `raw`。 |

得到 `raw.bed`（基因型）、`raw.bim`（位點）、`raw.fam`（樣本）與 `raw.log`。這裡只是把已判定的 genotype 換成另一種格式，並不是從晶片訊號重新 calling，也還沒有用缺失率篩選樣本或位點。PLINK 的 `.bed` 不同於記錄基因體區間的文字 BED。[PLINK 輸入格式](https://www.cog-genomics.org/plink/1.9/input)、[資料管理](https://www.cog-genomics.org/plink/1.9/data)

## 第 2 行：留下「篩選前」的 QC 報表

```bash
plink1.9 --bfile raw --missing --freq --hardy --het --out qc
```

| 部分 | 意義與輸出 |
|---|---|
| `--bfile raw` | 讀取 `raw.bed`、`raw.bim`、`raw.fam`。 |
| `--missing` | `qc.imiss`：每人的缺失率；`qc.lmiss`：每個位點的缺失率，重點欄位為 `F_MISS`。 |
| `--freq` | `qc.frq`：allele 頻率報表，包含較少見 allele 的頻率 `MAF`。 |
| `--hardy` | `qc.hwe`：基因型計數與 Hardy–Weinberg equilibrium（HWE）檢定。 |
| `--het` | `qc.het`：每人的觀察／預期純合數、非缺失位點數與 `F`。 |
| `--out qc` | 以上報表使用 `qc` 前綴，另留 `qc.log`。 |

這一行沒有指定排除門檻，因此不會因為報表出現高缺失率、HWE 偏離或雜合度異常就刪掉資料。特別注意 `--hardy` 是產生報表，`--hwe` 才是另一個用於篩選的選項；`.het` 的 `F` 也不是雜合百分比。[PLINK 基本統計](https://www.cog-genomics.org/plink/1.9/basic_stats)

頻率與 HWE 的預設統計對象是 founders，即家系資料中未登錄父母的樣本，不一定涵蓋所有人；本例合成樣本均未登錄父母。HWE 報表的 `TEST` 欄還會區分分析群組，例如全部、病例、對照；不能把不同列混成同一個檢定結果。

## 第 3 行：先篩掉缺失比例過高的樣本

```bash
plink1.9 --bfile raw --mind 0.05 --make-bed --out sample_qc
```

- `--bfile raw`：從完整的 raw 三件組開始。
- `--mind 0.05`：排除缺失 genotype 比例**超過 5%** 的樣本，不是隨機刪掉 5% 的人。
- `--make-bed`：將篩選後保留的資料輸出成三件組。
- `--out sample_qc`：產生 `sample_qc.bed/.bim/.fam` 與 `sample_qc.log`，不覆寫 raw。

例如一人測量 6,000 個位點，其中 2,000 個沒有 genotype，缺失比例約 33.3%，就會被此設定排除。這是本教材的合成案例；5% 不代表所有研究都適用的品質標準。

## 第 4 行：用剩下的人，重新評估每個位點

```bash
plink1.9 --bfile sample_qc --geno 0.05 --make-bed --out clean
```

- `--bfile sample_qc`：接著讀取第 3 行留下的樣本，不是重新讀 raw。
- `--geno 0.05`：排除在剩餘樣本中缺失比例**超過 5%** 的位點。
- `--make-bed --out clean`：把留下的樣本與位點另存為 `clean.bed/.bim/.fam`，附 `clean.log`。

為什麼分成兩行？假設一個位點原本在 40 人中有 3 人缺失，缺失率是 7.5%；如果這 3 人中有 2 人先因整體品質不佳而被移除，該位點在剩餘 38 人中就只有 1 人缺失，即約 2.63%。這個**獨立的假設算例**說明：先篩樣本，會改變下一步位點缺失率的分子與分母，不能直接把 `qc.lmiss` 的篩選前比例當成篩選後比例。[PLINK 缺失率篩選](https://www.cog-genomics.org/plink/1.9/filter#missing)

`clean` 只是這份腳本給的名稱，意指通過這兩次缺失率篩選；它沒有保證樣本身分、親緣、批次、HWE 或區域訊號都沒有問題。

## 「先保留」不等於腳本會停下來等待

整份執行 `run-array.sh` 時，程式會依序跑完，**不會在產生 qc 報表後等待人工核准**。要練習「先看證據，再選門檻」，應先分開執行前兩行，讀完報表後再決定是否執行後兩行。保留原始資料、報表、工具版本、參數與排除理由，才能追溯分析過程。

## 腳本後半段怎麼接續？

| 步驟 | 使用哪些位點？ | 主要產物／要回答的問題 |
|---|---|---|
| LD pruning | clean 中 MAF ≥ 5% 的位點，再減少高相關位點 | `prune.prune.in`：後續使用的位點 ID 清單；不是新的 genotype 檔。 |
| 親緣估計 | clean 中列於 `.prune.in` 的位點 | `related.genome`：哪些樣本組合可能重複或有親緣？ |
| PCA | 與親緣估計相同的清單 | `structure.eigenvec/.eigenval`：每人前四個 PC 座標及特徵值，不是四個群組。 |
| ROH | 未經 pruning 的 clean | `roh.hom` 等：哪些區域呈現連續純合？不是直接判定 CNV。 |

每一行都是重新啟動一次 PLINK：前一行的 `--maf` 或 `--extract` 不會自動延續到下一行。後續親緣與 PCA 是明確使用 `.prune.in` 才共享選出的位點；ROH 那行沒有 `--extract`，所以回到 clean 的完整位點集合。所有參數與輸出細節均已寫在 [run-array.sh 的逐行註解](../demos/lesson-01-genomics/run-array.sh)。

參考：[PLINK LD pruning](https://www.cog-genomics.org/plink/1.9/ld)、[親緣與 ROH](https://www.cog-genomics.org/plink/1.9/ibd)、[PCA](https://www.cog-genomics.org/plink/1.9/strat)。
