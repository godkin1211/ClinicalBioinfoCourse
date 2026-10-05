# 第一堂 HTML 投影片

第二堂另見：[癌症體細胞基因體分析投影片](lesson-02-somatic.html)與[操作說明](lesson-02-README.md)。

第三堂另見：[Bulk RNA-seq 與可變剪接投影片](lesson-03-bulk-rnaseq.html)、[逐頁詳解](lesson-03-explanations.html)與[操作說明](lesson-03-README.md)。

用 Chrome、Edge 或其他支援現代 HTML 的瀏覽器開啟 `lesson-01-genomics.html`。

- 54 張、16:9；第 1–46 張為主課程，第 47–54 張為操作附錄與參考資料。
- 第 7 張以 Infinium II 示意單一 SNP 位點的探針結合、單鹼基延伸、訊號掃描與基因型判定；第 8 張說明 A/B 代號與基因型對照。圖形已內嵌，不需另帶圖檔。
- 第 9 張以兩個同為 AB 的樣本說明 hard call 的資訊限制；另附[完整講解與問答](../../lessons/lesson-01-slide-09-explanation.md)。
- 第 10 張對照 BAF 與 LRR 的定義、典型值及限制；另附[講解與算例](../../lessons/lesson-01-slide-10-baf-lrr.md)。
- 第 11 張新增 SNP array 常見格式總覽：IDAT／CEL、GTC、Final Report、PLINK；另說明 manifest／EGT。原有 BED／BIM／FAM 詳解在第 12 張。
- 第 13 張以四個檢查層次連結 QC 指標、查證方向與高 call rate 案例；另附[完整說明與判讀案例](../../lessons/lesson-01-slide-12-qc.md)（保留原檔名）。
- 第 20 張逐行對照格式轉換、QC 報表、樣本與位點篩選；附[每行參數、輸出檔與算例](../../lessons/lesson-01-slide-19-array-commands.md)及[完整註解腳本](../../demos/lesson-01-genomics/run-array.sh)（說明檔保留原檔名）。
- 第 24–29 張為 Panel／WES／WGS 範圍示意、建庫差異、變異偵測限制、覆蓋率算例、分析設計與選擇情境；另附[完整說明](../../lessons/lesson-01-sequencing-choice.md)。FASTQ／BAM／VCF 流程在第 30 張。
- 第 31 張新增 NGS 常見格式總覽：FASTQ、SAM／BAM／CRAM、VCF／BCF、gVCF、FASTA／區間 BED，以及索引用途。
- 一小時課程可將既有命令列實作頁留作課後延伸，課堂優先保留技術選擇與判讀；正文不標示分段授課時長。
- 方向鍵、Page Up／Down、空白鍵翻頁；Home／End 跳到首末頁。
- `F` 切換全螢幕，`O` 開啟目錄，Esc 關閉目錄。
- 判讀題可點選「先想一想，再展開解析」。
- 「列印全部」使用瀏覽器列印；建議開啟背景圖形、關閉頁首頁尾。

播放不依賴網路、CDN 或外部字型。參考文件的外部連結需要網路；教材及腳本的相對連結需要保留本專案目錄結構。投影片中的命令是教學文字，不會在瀏覽器中執行。

投影片依現有第一堂教案、學員教材與已驗證合成資料編寫，不新增病人資料。圖中的概念示意與合成結果均已標示。正文不標示各部分授課時長。

## 更新

修改 `scripts/build-lesson01-slides.py` 中的內容後，在專案根目錄執行：

```bash
python3 scripts/build-lesson01-slides.py
```

來源整理見 `sources/lesson-01-slides-sources.md`。
