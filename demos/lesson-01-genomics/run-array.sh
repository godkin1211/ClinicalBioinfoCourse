#!/usr/bin/env bash
# 上一行是 shebang：直接執行此檔案時，由 env 在 PATH 中尋找 Bash。
# 執行位置：先 cd 到 generate.py 建立的練習目錄（內含 array.ped / array.map）。
# 本腳本不會自行切換目錄；所有輸入與輸出路徑都相對於「目前工作目錄」。
# 用法：PLINK=plink1.9 bash ../run-array.sh
# 重跑會替換同名前綴的結果與 .log；請在獨立練習目錄使用，不要混入研究資料。
# 以下 # 開頭的文字是註解，不會當作命令執行。

# Bash 安全設定：-e 遇未被條件等語法處理的命令失敗時停止；-u 禁止使用未定義變數；
# -o pipefail 讓管線中任一步失敗都能反映為管線失敗（本腳本目前沒有管線）。
set -euo pipefail

# 選擇 PLINK 執行檔：若外部 PLINK 變數未設定或是空字串，就使用 plink1.9。
# 例如 PLINK=/path/to/plink 可指定位置；此變數只放執行檔名稱／路徑，不放參數。
PLINK=${PLINK:-plink1.9}

# 1. 將文字 genotype 轉成 PLINK 二進位格式，尚未做缺失率篩選。
# "$PLINK"：執行上方指定的程式；雙引號避免路徑中的空白被拆成多個參數。
# --file array：讀取 array.ped（樣本與基因型）和 array.map（位點資訊）。
# --make-bed：產生 .bed / .bim / .fam 三件組；此 .bed 不是區間座標文字 BED。
# --out raw：指定輸出前綴，得到 raw.bed、raw.bim、raw.fam 與 raw.log。
# 這是資料格式轉換，不是從晶片強度重新判定 genotype；原始 PED/MAP 仍保留。
"$PLINK" --file array --make-bed --out raw

# 2. 在篩選前留下 QC 證據；這一行只產生報表，不會依這些指標排除資料。
# --bfile raw：讀取 raw.bed / raw.bim / raw.fam；前綴不加副檔名。
# --missing：輸出 qc.imiss（每個樣本）與 qc.lmiss（每個位點）的缺失率。
# --freq：輸出 qc.frq，包含較少見 allele 的頻率 MAF。
# --hardy：輸出 qc.hwe 的 HWE 檢定；不是執行篩選的 --hwe。
# --het：輸出 qc.het，含觀察／預期純合數與 F；F 不是雜合百分比。
# --out qc：以上報表共用 qc 前綴，執行紀錄為 qc.log。
# 頻率與 HWE 預設使用 founders（家系中未登錄父母的樣本），不一定是所有人；
# HWE 的 TEST 欄另區分 ALL / AFF / UNAFF 等群組。此合成資料均未登錄父母。
"$PLINK" --bfile raw --missing --freq --hardy --het --out qc

# 3. 先按「樣本」缺失率篩選，讓高缺失樣本不再影響下一步位點缺失率。
# --bfile raw：仍從完整的 raw 三件組開始。
# --mind 0.05：排除缺失 genotype 比例 > 5% 的樣本；不是隨機刪除 5% 的人。
# --make-bed --out sample_qc：把留下的資料另存為 sample_qc 三件組與 .log。
# raw 不被覆寫。5% 只是操作示例，不是通用或臨床門檻。
"$PLINK" --bfile raw --mind 0.05 --make-bed --out sample_qc

# 4. 再按「位點」缺失率篩選；分母是 sample_qc 內留下的樣本。
# --bfile sample_qc：接續第 3 步的資料，而不是重新讀 raw。
# --geno 0.05：排除在剩餘樣本中缺失率 > 5% 的位點。
# --make-bed --out clean：另存 clean.bed / clean.bim / clean.fam 與 clean.log。
# clean 只代表通過本例兩階段缺失率篩選，並不代表所有 QC 都已合格。
"$PLINK" --bfile sample_qc --geno 0.05 --make-bed --out clean

# 5. 建立 LD pruning 位點清單，減少高度相關 SNP 對親緣／PCA 的重複影響。
# --bfile clean：讀取缺失率篩選後的三件組。
# --maf 0.05：本次只讓 MAF >= 5% 的位點進入 pruning，不改寫 clean 檔案。
# --indep-pairwise 50 5 0.2：視窗含 50 個位點，每次移動 5 個位點；
# 對視窗內成對 r² > 0.2 的位點進行修剪，留下較不冗餘的集合。
# 50 的單位是位點數，不是 kb；r² 是基因型 allele 計數的相關程度平方。
# --out prune：輸出 prune.prune.in（保留 ID）、prune.prune.out（pruning 排除 ID）
# 與 prune.log。此行沒有 --make-bed，因此不產生新的 genotype 三件組。
# .prune.out 不是完整 QC 排除名單；先被 MAF 過濾掉的位點不在 pruning 候選中。
"$PLINK" --bfile clean --maf 0.05 --indep-pairwise 50 5 0.2 --out prune

# 6. 用選出的位點估計兩兩樣本的遺傳相似／親緣程度。
# --bfile clean：讀取 clean 三件組。
# --extract prune.prune.in：本次只使用清單中的「位點」，不是挑選樣本。
# --genome：在常染色體 SNP 上計算 IBS/IBD；不是進行 WGS 或 CNV 分析。
# --out related：輸出 related.genome 與 related.log；報表含 PI_HAT 等指標。
# PI_HAT 接近 1 時可查重複或同卵雙生，仍需紀錄佐證；此行不自動刪除樣本。
"$PLINK" --bfile clean --extract prune.prune.in --genome --out related

# 7. 用相同的 pruning 位點做主成分分析（PCA），摘要樣本間的基因型差異。
# --bfile clean --extract prune.prune.in：與第 6 步使用相同輸入與位點清單。
# --pca 4：計算前 4 個主成分；不是把樣本硬分成 4 群。
# --out structure：輸出 structure.eigenvec（每人 PC 座標）、structure.eigenval
# （特徵值）與 structure.log；此行不畫圖、不校正批次，也不移除離群樣本。
# 合成資料故意保留已知重複樣本供判讀，不可直接把此結果當成關聯分析的定稿。
"$PLINK" --bfile clean --extract prune.prune.in --pca 4 --out structure

# 8. 找連續純合區（ROH），回到未經 LD pruning 的 clean，以保留位點密度。
# --bfile clean：沒有 --extract，也沒有 --maf；第 5 步的篩選不會自動延續。
# --homozyg：啟動以滑動視窗搜尋 ROH 的分析。
# --homozyg-snp 100：候選 ROH 至少包含 100 個 SNP。
# --homozyg-kb 1000：候選 ROH 至少長 1,000 kb（1 Mb）。
# 仍須同時滿足預設的密度、位點間距、視窗缺失／雜合容許量等條件；不只看上述兩值。
# --out roh：輸出 roh.hom（區段）、roh.hom.indiv（每人摘要）、
# roh.hom.summary（各位點摘要）與 roh.log。ROH 不是缺失或單親二體的直接診斷。
"$PLINK" --bfile clean --homozyg --homozyg-snp 100 --homozyg-kb 1000 --out roh

# 完成後仍需人工判讀報表、保存版本／log 與排除理由，並用 verify.py 核對教學結果。
# 指令參考：https://www.cog-genomics.org/plink/1.9/
# 本頁講解：../../lessons/lesson-01-slide-19-array-commands.md（相對於腳本所在位置）
