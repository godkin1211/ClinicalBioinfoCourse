# 第二堂：癌症體細胞基因體分析練習

配合[學員教材](../../lessons/lesson-02-materials.md)。全部為合成資料，不包含病人資訊。這是 candidate review 練習，不是正式 somatic caller 或臨床流程驗證。

## 執行

初次操作請先照[教材附錄 A](../../lessons/lesson-02-materials.md#附錄-a依作業系統安裝到第一次成功執行)：A2 為 Windows／WSL2，A3 為 macOS，A4 為 Linux（Ubuntu／Debian），A5 下載專案，A7 執行並驗證，A8–A9 安裝 IGV 與載入完整結果，A10 排錯。第二堂不需 PLINK，也不需第一堂的輸出。

已完成安裝者，在 Windows 的 Ubuntu、macOS Terminal 或 Linux Terminal 執行；路徑不同時調整第一行：

```bash
cd ~/ClinicalBioinfoCourse/demos/lesson-02-somatic
python3 generate.py practice-local01
cd practice-local01
bash ../prepare.sh
python3 ../verify.py .
python3 ../models.py
```

產生器拒絕覆蓋既有資料夾，重做改用 `practice-local02` 並同步更改 `cd`。`prepare.sh` 重跑會取代同名結果。分析只需 Python 3.8 以上、SAMtools、BCFtools；圖形操作另用 IGV Desktop。無 Python 第三方套件。

驗證成功應顯示 `PASS: BAM-derived counts, bias patterns, VCF samples/flags, CN/VAF models, indexed artifacts`。附錄提供各步驟的輸入／輸出、log、退出碼、數值核對與 9 個 IGV 所需檔案；圖形操作尚未完成不影響命令列驗證，但兩者應分別記錄。

## 檔案與限制

- `generate.py`：建立固定種子的 5 kb 人工 reference、三個位點的 tumor/normal SAM、人工 VCF、獨立 CN 模型的 SEG。
- `prepare.sh`：SAM → sorted/indexed BAM、VCF 壓縮與 TBI 索引、讀段計數。
- `audit_reads.py`：針對三個已知位點從 SAM stdin 計數。僅支援本例 150M，排除指定 flags 並使用 MAPQ/BQ≥20；非通用 caller/pileup。
- `models.py`：VAF/purity/CN 的簡化混合模型，以及獨立讀段的二項抽樣模型。
- `verify.py`：對照已知預期輸出。模型核對不驗證模型對真實樣本的適用性。

本例未模擬原始分子獨立性、UMI、PCR、paired-end、FFPE 化學損傷或真實 alignment；不執行 Mutect2/CNV/SV caller。VCF FILTER 與 GT 是人工指定，不能當成算法實測結果。CN SEG 不是從 toy BAM 深度估計，不能把兩者當成同一套 CN 分析。

## 預期結果與實測紀錄

2026-09-13，命令列流程於 macOS、Python 3.9.6、SAMtools 1.22、HTSlib 1.22.1、BCFtools 1.22 實測。

| 事件 | 腫瘤證據 | 正常證據 | 解析重點 |
|---|---|---|---|
| A，chrToy:500 C>T | 20/400，正反 ALT 各 10，末端 0 | 0/200 | 相對一致，但不是驗證過的 somatic 真值 |
| B，chrToy:1500 C>T | 20/400，ALT 全正向、全在末端 5 bp | 0/200 | VAF 相同，技術證據不同 |
| D，chrToy:2500 C>T | 200/400 | 100/200 | Germline-like 的正常樣本支持 |
| C，chrToy:3000–4000 | 獨立 SEG，log2 ratio=0.485427 | 模型基準為 CN2 | p=0.2、腫瘤 CN6 的理論混合結果 |

核心流程與 `verify.py` 通過；另以 SAMtools mpileup 獨立核對兩份 BAM 的三個位點，深度與正反向 ALT 計數均相符，BCFtools norm 的 reference 檢查亦通過。教材內 Bash 區塊通過語法檢查，本地連結可解析。

2026-09-30 再驗證：macOS arm64、Python 3.14.3、SAMtools／BCFtools 1.22、HTSlib 1.22.1。在新目錄（含空白路徑）產生資料、執行 `prepare.sh`、`verify.py`、`models.py` 與 BAM quickcheck，完整 PASS；模型的 0.05、0.071429、0.485427 均符合教材。

Windows／WSL、Linux 的安裝，以及三種系統的 IGV 圖形操作依官方文件整理，本次未在對應環境逐一實測，也未重新安裝整套 macOS 工具。IGV 的 downsampling、比例尺及配色可能因版本／偏好而異，請以完整 BAM 計數核對，不以畫面可見讀段數代替計數。來源與相容性見[查核紀錄](../../sources/lesson-01-02-practical-setup-sources.md)。

## 核對 checklist

- [ ] 兩份 BAM 的 SM 為 TUMOR 與 NORMAL，reference 均為 chrToy。
- [ ] 每個腫瘤位點 400 reads、正常位點 200 reads；A/B 的 VAF 同為 5%。
- [ ] B 有方向／末端偏差，A 沒有設定這些偏差。
- [ ] VCF 和證據表的樣本、AD、DP、AF 相符。
- [ ] IGV 載入本例 reference，而非 hg19/hg38。
- [ ] CN 模型與 read-depth 實測明確分開。
- [ ] 讀段抽樣機率未被稱為臨床 LOD。
