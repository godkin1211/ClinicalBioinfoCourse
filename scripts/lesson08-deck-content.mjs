// Learner-facing slide content derived from lessons/lesson-08-materials.md.
// Code excerpts are reading aids unless the slide explicitly says to execute them.
const s = (kind, title, subtitle, content) => ({kind, title, subtitle, ...content});
export const slides = [
  s('cover','Nextflow 生物資訊工作流程入門','',{}),
  s('triple','一批 RNA-seq 資料的流程管理問題','每個樣本有 R1、R2。當樣本增加，人工執行需要更多追蹤。',{
    columns:[['樣本是否完整','哪些樣本已完成？R1、R2 是否一起分析？是否混入上次的報告？'],['環境能否重現','同一支 script 換電腦後，工具版本與相依套件是否仍相同？'],['失敗如何恢復','中途停止後，哪些工作可重用？哪些工作需要重新計算？']],
    bottom:'Shell script 與 notebook 也能寫得可重現。Nextflow 將依賴、排程、快取與紀錄整合管理。',section:'1'}),
  s('overview','本課的 FASTQ QC 流程','以人工合成資料理解資料流，不建立臨床品質門檻。',{
    lines:[['輸入','2 個樣本，每個樣本有 R1 與 R2，共 4 個 FASTQ。'],['FastQC','每個樣本啟動 1 個 task，一次處理兩個 read 檔。'],['MultiQC','收齊 4 個 FastQC ZIP 後，啟動 1 個整合 task。']],
    bottom:'總共 3 個 task，產生 4 份 FastQC HTML／ZIP 與 1 份 MultiQC HTML。',section:'2'}),
  s('table','Pipeline、Process 與 Task','同一個步驟定義，可以對不同輸入執行多次。',{
    rows:[['名稱','意思','本例'],['Pipeline','輸入、步驟、設定與輸出的整體','整個 QC 專案'],['Process','需要什麼輸入、執行什麼、交付什麼','FASTQC 定義'],['Task','Process 對一組具體輸入的一次執行','FASTQC(sampleA)'],['Workflow','呼叫步驟並連接資料流的區塊','FastQC 與 MultiQC 的串接']],section:'2'}),
  s('concept','Process、Channel 與 Workflow','Nextflow 根據輸入是否就緒安排工作。',{
    left:[['Process','包裝一個工具步驟，定義輸入、指令與輸出契約。'],['Channel','傳遞值或檔案參照的資料流，不是實體資料夾。'],['Workflow','串接分析步驟。下游收到輸入後才啟動。']],section:'2'}),
  s('triple','執行位置與軟體環境','分析邏輯可以與執行設定分開管理。',{
    columns:[['Parameter','--input、--outdir 是流程參數，讓同一流程接收不同資料。'],['Executor','決定 task 交給哪裡執行。本例 local，HPC 可用 Slurm 等後端。'],['Container','封裝工具與套件。本例分別固定 FastQC 與 MultiQC 的映像 tag。']],
    bottom:'移轉 HPC／雲端仍需確認路徑、權限、資源、排程器與容器後端相容。',section:'2'}),
  s('compare','work/ 與 results/ 的不同','Nextflow 先在 task 工作目錄執行，再發布供使用者閱讀的結果。',{
    columns:[['work/：計算與追溯','每個 task 有獨立子目錄。\n放入 staged 輸入、實際指令、標準輸出、錯誤與產物。\n快取恢復需要原工作產物。'],['results/：交付與閱讀','publishDir 將產物複製至結果目錄。\n報告方便交付，但不代表包含完整快取。\n下游應接 output channel，避免掃到舊報告。']],section:'2.1'}),
  s('triple','安裝與執行路線','Nextflow 26.10.3、FastQC 0.12.1、MultiQC 1.30 為本教材測試基準。',{
    columns:[['Windows','使用 WSL2 Ubuntu，啟用 Docker Desktop 的 WSL Integration。'],['macOS','啟動 Docker Desktop，安裝相容 Java。Apple Silicon 需留意容器架構。'],['Linux','安裝相容 Java 與 Docker Engine，確認服務與權限正常。']],
    bottom:'Java／Nextflow 裝在主機，FastQC／MultiQC 在容器執行。完整安裝指令見附錄。',section:'3'}),
  s('code','樣本清單與輸入路徑','以下指令與相對路徑，都以 demos/nextflow-qc 為起點。',{
    code:'sample_id,fastq_1,fastq_2\nsampleA,data/sampleA_R1.fastq,data/sampleA_R2.fastq\nsampleB,data/sampleB_R1.fastq,data/sampleB_R2.fastq',
    wide:true, points:[['sample_id','用來追蹤樣本。每列將 ID 與對應 FASTQ 綁在一起。'],['相對路徑','相對於啟動指令的目錄，不是 CSV 所在目錄。'],['輸入限制','使用不衝突的檔名，避免引號與 shell 特殊字元。範例沒有完整 schema／安全驗證。']],section:'4.1'}),
  s('code','FASTQ 的四行結構','一筆 read 包含識別碼、序列、分隔符與每個鹼基的品質字元。',{
    code:'@sampleA_read1/1\nACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n+\n!IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII',
    points:[['第 1、2 行','@ 後是 read ID，下一行是讀到的序列。'],['第 3、4 行','+ 是分隔符。品質字元數須等於序列長度。'],['配對限制','R1、R2 來自片段兩端。\nFastQC 不驗證配對或病人身分。']],section:'4.2'}),
  s('compare','合成資料與 Phred 品質值','每個 FASTQ 有 4 reads，每筆長度 40 bases。',{
    columns:[['讀數如何計算','4 個檔案合計 16 筆 read 紀錄。\n雙端資料相當於 8 組 read pairs。\n只用於驗證程式是否運作，不能推論真實文庫品質。'],['Q 值如何理解','Q = −10 log10(Perror)\nPhred+33 的 I 為 Q40，! 為 Q0。\nQ40 的名義錯誤機率是 0.0001，不是保證每個鹼基正確。']],
    bottom:'第一筆第一個字元刻意用 !，避免全部為 I 時 FastQC 自動誤認成 Phred+64。',section:'4.2'}),
  s('code','FastQC process：輸入與輸出','程式片段供閱讀，執行時請使用專案中的完整 main.nf。',{
    code:'process FASTQC {\n    tag "${sample_id}"\n    label \'fastqc\'\n    input:\n    tuple val(sample_id), path(reads)\n    output:\n    path "*_fastqc.html", emit: html\n    path "*_fastqc.zip", emit: zip\n    // script 見下一頁\n}',
    points:[['tag 與 label','tag 顯示樣本名稱。label 讓設定檔集中指定資源與容器。'],['tuple／val／path','tuple 綁定 ID 與讀檔。val 是一般值，path 宣告要 staging 的檔案。'],['output／emit','glob 指定預期產物，emit 為輸出 channel 命名。']],section:'5.1'}),
  s('code','FastQC process：工具指令與發布','script 組成真正交給 shell 執行的命令。',{
    code:'publishDir "${params.outdir}/fastqc",\n    mode: \'copy\'\n\nscript:\ndef read_args = reads.collect { read ->\n    "\'${read}\'"\n}.join(\' \')\n"""\nfastqc --threads ${task.cpus} \\\n    --outdir . ${read_args}\n"""',
    points:[['task.cpus','從設定讀取 CPU 數，避免把資源寫死在工具命令。'],['--outdir .','這個點是 task 的工作目錄，不是啟動 Nextflow 的目錄。'],['publishDir','工具完成後複製產物。下游仍使用 output channel，不等待發布目錄。']],section:'5.1'}),
  s('code','從 CSV 建立 Channel','每列轉成「樣本 ID，加上一組 FASTQ 檔案」。',{
    code:'samples = channel\n    .fromPath(params.input,\n        checkIfExists: true)\n    .splitCsv(header: true)\n    .map { row ->\n        // 完整程式另檢查空白欄位\n        def reads = [file(row.fastq_1,\n            checkIfExists: true)]\n        if (row.fastq_2)\n            reads << file(row.fastq_2,\n                checkIfExists: true)\n        tuple(row.sample_id, reads)\n    }',
    points:[['fromPath／splitCsv','先取得清單檔，再依欄名解析每列資料。'],['map','轉換每列的資料結構。完整版本使用 trim、?. 與缺欄檢查。'],['checkIfExists','只確認檔案路徑存在，不代表 FASTQ 內容或配對正確。']],section:'5.2',small:true}),
  s('code','collect() 讓 MultiQC 整批整合','兩個 FastQC task 各輸出兩個 ZIP，MultiQC 收到一個四檔清單。',{
    code:'workflow {\n    // samples 建立方式見前頁\n    FASTQC(samples)\n\n    fastqc_archives = FASTQC.out.zip\n        .flatten()\n        .collect()\n\n    MULTIQC(fastqc_archives)\n}',
    points:[['flatten()','把每個 task 輸出的 ZIP 集合攤平成個別項目。'],['channel collect()','等上游關閉，收成一個清單，才啟動一次 MultiQC。'],['同名不同層次','reads.collect {…} 是集合轉換。channel.collect() 是彙整資料流。']],section:'5.3'}),
  s('code','MultiQC 讀取什麼資料？','它整合既有 FastQC 統計，不重新分析 FASTQ，也不從 HTML 圖片推算。',{
    code:'input:\npath fastqc_archives\n\noutput:\npath \'multiqc_report.html\', emit: report\npath \'multiqc_data\', emit: data\n\nscript:\n"""\nmultiqc --force --outdir . \\\n    ${fastqc_archives.join(\' \')}\n"""',
    points:[['真正的統計來源','FastQC ZIP 內的 fastqc_data.txt。'],['本次輸入明確','從 channel 收檔，避免混入上一批結果或尚未發布完成的檔案。'],['檔名衝突','相同 basename 可能在 staging 衝突。正式流程需 metadata／子目錄策略。']],section:'5.3'}),
  s('code','nextflow.config 管理資源與環境','完整設定另含 MultiQC、Conda／standard profile 及執行紀錄。',{
    code:'process {\n    executor = \'local\'\n    withLabel: fastqc {\n        cpus = 2\n        memory = \'2 GB\'\n        container = \'quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0\'\n    }\n}\nprofiles { docker { docker.enabled = true } }',
    points:[['label 選取設定','FastQC 使用 2 CPUs／2 GB。MultiQC 使用 1 CPU／2 GB。'],['啟用後端','需用 -profile docker 啟用 Docker 後端。'],['命令列區別','-profile 是 Nextflow 選項。--input、--outdir 是流程參數。']],section:'5.4',small:true,wide:true}),
  s('compare','容器固定了什麼？','容器讓工具與使用者空間套件較一致，仍需完整紀錄分析環境。',{
    columns:[['本教材固定版本','Nextflow 26.10.3\nFastQC 0.12.1\nMultiQC 1.30\nJava 建議 21 LTS，主機需相容版本。'],['仍會影響重現的因素','輸入、參考資料與設定仍需追蹤。\nNextflow 版本、host kernel 也有影響。\n映像 tag 可以改指向其他內容。正式分析應記錄映像 digest。']],section:'3.1、5.4'}),
  s('code','第一次執行：先用一個樣本','先確認位於 demos/nextflow-qc，而且 docker info 成功。',{
    code:'nextflow lint .\n\nnextflow run . -profile docker \\\n    --input data/samplesheet-one.csv \\\n    --outdir results/one',
    points:[['lint 的範圍','檢查語法等問題，不證明工具可執行，也不證明資料正確。'],['預期工作數','1 個 FastQC task，加上 1 個 MultiQC task。'],['成功訊號','流程回報 SUCCESS 後，仍要檢查實際產物與 QC 內容。']],section:'6.1'}),
  s('code','擴充到兩個樣本並驗證產物','這次不加 -resume，預期建立 3 個新的 task。',{
    code:'nextflow run . -profile docker \\\n    --input data/samplesheet.csv \\\n    --outdir results/two\n\npython3 verify.py results/two \\\n    --samples sampleA sampleB',
    points:[['FastQC','2 個 task，各處理同一樣本的兩個 read 檔。'],['MultiQC','1 個 task，彙整四個 ZIP。'],['verify.py','檢查檔案與 ZIP 可讀、每檔 reads 數／長度及四個 read 檔是否納入。預期 PASS。']],section:'6.2'}),
  s('code','結果目錄與檔案用途','時間、路徑及報告欄位可能改變，不要求每次 HTML 位元完全一致。',{
    code:'results/two/\n├── fastqc/\n│   └── 4 份 HTML 與 4 份 ZIP\n├── multiqc/\n│   ├── multiqc_report.html\n│   └── multiqc_data/\n└── pipeline_info/\n    ├── execution_report.html\n    ├── execution_timeline.html\n    ├── execution_trace.txt\n    └── pipeline_dag.html',
    points:[['工具報告','FastQC 看單一 read 檔，MultiQC 看整批比較。'],['執行報告','trace、report、timeline 與 DAG 分別提供不同執行證據。'],['數值單位','MultiQC 1.30 的 reads 欄以百萬匯出，4e-06 代表 4 reads。']],section:'6.2'}),
  s('report','MultiQC 報告的閱讀順序','畫面來自已執行的人工合成測試，不是臨床樣本。',{
    points:[['先核對檔名','sampleA／sampleB 各有 R1、R2，共四個 read 檔。'],['再看基本數值','每檔 4 reads。Seqs 以百萬顯示，四捨五入成 0.0M，不代表零筆。'],['最後看品質分布','比較 cycle 品質、組成、GC、重複、接頭及離群樣本。']],section:'6.4'}),
  s('table','FastQC 指標與本例的限制','PASS／WARN／FAIL 是模組規則提示，不能直接當作臨床檢體合格證。',{
    rows:[['指標','回答的問題','本例如何理解'],['Per-base quality','各 cycle 品質是否惡化？','首 cycle 平均 Q30，其餘 Q40'],['組成與 GC','鹼基比例是否偏離預期？','重複人工序列並不自然'],['Duplication／過量序列','是否有高度重複訊號？','極小樣本單一序列占比很高'],['Adapter content','是否出現已知接頭？','未標記不代表排除所有污染']],section:'6.4'}),
  s('compare','執行成功與品質合格','Nextflow SUCCESS 與 FastQC FAIL 可以同時出現。',{
    columns:[['執行成功','工具正常結束，交付了流程宣告的產物。\n仍需確認檔案內容及樣本是否完整。'],['品質與方法判斷','品質規則可能觸發 FAIL。\n需依檢體、建庫、資料特性與下游目的判斷，不能只把旗標改成綠燈。']],
    bottom:'本例的人工序列與極少 reads 可能觸發警示，不能據此建立真實文庫門檻。',section:'6.4、10.2'}),
  s('code','原樣重跑與 -resume','緊接兩樣本執行後，從同一目錄使用同一 profile。',{
    code:'nextflow run . -profile docker \\\n    --input data/samplesheet.csv \\\n    --outdir results/two -resume\n\nhead -n 5 \\\n    results/two/pipeline_info/execution_trace.txt',
    points:[['預期三個 CACHED','重用既有 task 產物，並非重新運算。'],['命中條件','選定 session 的 hash 相符，而且預期工作產物仍存在。'],['必要保留','task cache 與 work/ 都重要。只留 results/ 不足以恢復。']],section:'7.1'}),
  s('code','新增樣本時，哪些工作會重跑？','以下是獨立實驗，先建單樣本 run，再立即擴充。',{
    code:'nextflow run . -profile docker \\\n    --input data/samplesheet-one.csv \\\n    --outdir results/grow-one\n\nnextflow run . -profile docker \\\n    --input data/samplesheet.csv \\\n    --outdir results/grow-two -resume',
    points:[['sampleA','原輸入相同，FastQC 可重用。'],['sampleB','新增輸入，需要新的 FastQC task。'],['MultiQC','收到的 ZIP 清單改變，需要重跑整合。只改發布目錄不強迫重算。']],section:'7.2'}),
  s('table','快取命中與失效的判斷','一般檔案快取不一定逐位元雜湊，預設會使用名稱、大小、修改時間等資訊。',{
    rows:[['變更','本例預期','需要確認'],['原樣 -resume','重用已完成工作','session、cache、work 仍在'],['新增 FASTQ','新樣本 QC／整合重跑','舊樣本路徑與內容不變'],['改指令或容器','重新評估受影響工作','逐 task 檢查狀態'],['只改 --outdir','計算可能仍重用','發布目錄不是計算輸入'],['刪除 work/ 或 cache','可能無法重用','不要先刪 cache 再排錯']],section:'7.3'}),
  s('table','執行紀錄各自在回答什麼？','DAG 顯示依賴，不是時間軸，也不證明每個樣本成功。',{
    rows:[['紀錄','用途'],['execution_trace.txt','逐 task 狀態、exit code、耗時與資源'],['execution_report.html','整次執行概況與資源摘要'],['execution_timeline.html','任務的開始、結束與重疊時序'],['pipeline_dag.html','流程步驟與相依關係'],['nextflow log','查看 run name，必要時 -resume <run_name>']],section:'7.4'}),
  s('compare','可追溯分析需要保存的證據','快取只管理計算重用，臨床分析性能與結果責任仍需獨立建立。',{
    columns:[['計算與輸入','啟動指令、sample sheet、資料 checksum、程式 commit。\nNextflow／Java 版本、容器 digest、設定與參考資料。'],['結果與人工審核','QC、工具輸出、執行紀錄、排除／重跑原因及人工判讀。\n分享設定前檢查帳號、路徑與敏感資訊。']],
    bottom:'參考資料必須成為可追蹤依賴，不能假設換參考基因體一定自動重跑。',section:'7.3、7.4'}),
  s('code','故障練習：不存在的 FASTQ','使用提供的錯誤清單，在獨立輸出目錄觀察真正失敗。',{
    code:'nextflow run . -profile docker \\\n    --input data/samplesheet-missing.csv \\\n    --outdir results/missing',
    points:[['預期結果','非零退出碼、缺檔訊息，沒有有效 MultiQC 報告。'],['本例特性','第一列缺檔，尚無 FastQC task。一般清單可能已有其他 task 排程。'],['修正方向','修正路徑或使用正確清單重跑。不建立空 FASTQ 偽裝修好。']],section:'8.1',wide:true}),
  s('table','從 task 工作目錄排錯','依錯誤訊息或 trace 的 hash 找到 work/ 子目錄，用 ls -a 看隱藏檔。',{
    rows:[['檔案','用途'],['.command.sh','真正交給 shell 的工具指令'],['.command.run','Nextflow 的執行與容器包裝腳本'],['.command.out\n.command.err','標準輸出／標準錯誤，進度也可能在 err'],['.exitcode','退出碼，0 通常表示程式正常結束'],['.nextflow.log','啟動目錄中的流程層級診斷資訊']],
    bottom:'修改來源或設定後受控重跑，不直接改已快取的工作產物。',section:'8.2'}),
  s('table','常見故障與優先檢查','先確認環境，再追查具體 task，不以放寬權限或刪檔當作第一步。',{
    rows:[['現象','優先確認'],['command not found／Java 錯誤','PATH、java -version、JAVA_HOME'],['Docker daemon 無法連線','Desktop／Engine 是否啟動，docker info 是否成功'],['Permission denied','Docker socket、輸入／輸出權限，請資訊人員協助'],['no matching manifest／exec format error','主機與映像 CPU 架構、核准的模擬支援'],['Missing output／CACHED 比預期少','工具錯誤與產物名稱／session、hash、work 是否改變']],section:'8.3'}),
  s('triple','Nextflow 26.10 的延伸功能','本課維持既有 DSL2 範例，延伸功能不直接混入主實作。',{
    columns:[['靜態型別','啟用 typed 型別。\nlint 檢查型別。\nrun 警告仍可執行。'],['Global Cache','透過 Seqera Platform 使用雲端共用快取，本機 -resume 不會自動啟用。'],['模組與組合','以明確介面重用 process 或 workflow。需確認版本、參考資料與驗證範圍。']],
    bottom:'型別旗標：nextflow.enable.types = true。型別不驗證病人身分。\n雲端共用快取仍需評估權限、敏感資料隔離、儲存與下載成本。',section:'9.1–9.3'}),
  s('compare','成熟流程與 nf-core','從教學 QC 流程走向實際研究，優先評估已有的受維護流程。',{
    columns:[['可重用的工程基礎','nf-core 提供社群維護的 pipelines 與 modules。\n檢查輸入格式、參數、工具／參考版本、測試與執行需求。'],['仍需機構自行驗證','本例不是 nf-core 認證流程，也不是臨床驗證流程。\n正式檢測仍需建立適用範圍、分析性能、版本變更與結果核發規範。']],section:'9.3'}),
  s('compare','Nextflow agent 與 MultiQC AI 摘要','兩者都是選配，資料外送前需要機構核准。',{
    columns:[['Nextflow agent（preview）','宣告輸入、提示詞、工具與輸出，將 agent 納入 task 模型。\n快取可重播舊結果，不保證重新呼叫模型會得到相同答案。'],['MultiQC AI 摘要','將 QC 報告資料送給服務產生文字摘要，不需要 Nextflow agent 語法。\n一般 -profile docker 不會自動呼叫 AI。']],
    bottom:'AI 可協助整理資訊，不自行排除樣本、修改臨床門檻或形成診斷。',section:'9.4、9.5'}),
  s('code','Nextflow secrets：先登錄具名憑證','使用自己的 token 檔，放在 repository 外。不要將 token 值貼進教材。',{
    code:'set +x\nseqera_token_path=\'/absolute/path/to/seqera-token\'\ntest -s "$seqera_token_path" && \\\n  nextflow secrets set SEQERA_ACCESS_TOKEN \\\n    "$(tr -d \'\\r\\n\' < "$seqera_token_path")"\n\nnextflow secrets list',
    wide:true,points:[['登錄不等於取用','set 建立／更新名稱，list 只看名稱。並未呼叫 AI 或驗證服務權限。'],['安全限制','不要投影 secrets get 或啟用 set -x。註冊值仍短暫出現在程式參數，共用主機需評估。']],section:'9.5.1'}),
  s('code','現有 Seqera AI 範例仍使用唯讀 token 檔','完成 secrets 登錄，不會自動取代本例的檔案掛載。',{
    code:'nextflow run . -profile seqera_ai \\\n    --seqera_token_file /absolute/path/to/seqera-token \\\n    --input data/samplesheet.csv \\\n    --outdir results/seqera-ai\npython3 verify.py results/seqera-ai \\\n    --samples sampleA sampleB --ai',
    wide:true,points:[['目前取用方式','檔案只唯讀掛載至 MultiQC。值不插入 Nextflow 設定或 task 指令。'],['版本與驗證','1.30 使用教材相容入口。\n此入口更新摘要路由。\n--ai 確認摘要存在。'],['成本與人工核對','AI 模式不快取。\n重跑可能消耗配額。\n摘要仍需人工核對。']],section:'9.5.3'}),
  s('compare','Gmail 通知的是整個 workflow 結束狀態','採機構核准帳號。Gmail 憑證與 Seqera token 不可互用。',{
    columns:[['啟用方式','建立 Google 應用程式密碼，登錄兩個 Gmail secrets。\n額外載入 conf/gmail.config，使用 -N 指定獲准的收件者。\n詳細指令與設定見附錄。'],['通知與分析的邊界','成功與失敗可通知，不是 task 進度或定時心跳。\n只傳 run name、狀態、時間及退出碼，避免病人資料。\n主機斷電或程序被強制終止不保證寄出。']],
    bottom:'教材只驗證設定語法與信件模板，尚未用真實 Gmail 驗證認證或送達。',section:'9.5.2'}),
  s('triple','Take-home messages','可重現流程讓輸入、方法與執行證據可以一起被檢查。',{
    columns:[['資料流','Process 定義步驟。\ntask 對具體輸入執行。\nchannel 與 workflow\n串接依賴。'],['運行與驗證','容器控制工具環境。\n-resume 控制計算重用。\nverify.py 與 QC\n檢查實際產物。'],['責任與邊界','SUCCESS、QC 合格與臨床有效性是不同問題。AI 與通知仍需權限及人工審核。']],
    bottom:'課後可用附錄完成安裝、單樣本、雙樣本、快取與缺檔練習。',section:'10'}),
  s('links','教材、實作檔案與官方資源','點選以下連結可開啟公開教材或技術文件。',{
    links:[['課程 repository 與實作檔案','https://github.com/godkin1211/ClinicalBioinfoCourse'],['Nextflow 學員講義','https://github.com/godkin1211/ClinicalBioinfoCourse/blob/main/lessons/lesson-08-materials.md'],['Nextflow 官方文件','https://docs.seqera.io/nextflow'],['MultiQC 與 AI 摘要','https://docs.seqera.io/multiqc/ai/'],['nf-core pipelines','https://nf-co.re/pipelines']],section:'10.3'}),
  s('appendix','附錄：課後安裝與實作參考','依序完成環境檢查，再執行教材命令。',{
    body:'以下包含 Windows、macOS／Linux、固定版 Nextflow、容器檢查、完整 channel 轉換與 Gmail 通知。\n\n未實測的作業系統與選配服務，不應視為已保證成功。',section:'3、5、9'}),
  s('code','Windows：WSL2 Ubuntu 與 Docker','第一段在系統管理員 PowerShell，第二段在 Ubuntu 終端機。',{
    code:'# PowerShell：依提示重新啟動\nwsl --install -d Ubuntu\nwsl --list --verbose\n\n# Ubuntu 終端機\nsudo apt-get update\nsudo apt-get install -y \\\n  openjdk-21-jre-headless curl \\\n  git unzip python3\njava -version\ndocker info',
    points:[['WSL2','確認 Ubuntu 的 VERSION 為 2，並建立 Ubuntu 使用者帳號。'],['Docker Desktop','使用 WSL2 backend，在 WSL Integration 啟用 Ubuntu。'],['專案位置','放在 WSL Linux 使用者目錄，避免 /mnt/c/ 同步資料夾。遵守院內安裝權限。']],section:'3.2'}),
  s('code','macOS 與 Linux 的主機準備','先安裝核准的 Docker，啟動服務後檢查 docker info。',{
    code:'# macOS：已有 Homebrew 時\nbrew install --cask temurin@21\nbrew install git python\n\n# Ubuntu／Debian\nsudo apt-get update\nsudo apt-get install -y \\\n  openjdk-21-jre-headless curl \\\n  git unzip python3\n\njava -version\ndocker info',
    points:[['macOS','依 Apple Silicon／Intel 安裝 Docker Desktop。也可用 Temurin 官方 JDK 安裝包。'],['Linux','依官方發行版文件安裝 Docker Engine，確認服務及 socket 權限。'],['ARM 容器','架構不合時用核准 x86_64 主機，或另行測試模擬，不任意換工具版本。']],section:'3.3、3.4、8.3'}),
  s('code','安裝固定版 Nextflow','適用 macOS、Linux 與 WSL 的 Bash／Zsh。先確認沒有同名檔案。',{
    code:'mkdir -p course-tools\ncd course-tools\ncurl -fsSL https://get.nextflow.io \\\n    -o install-nextflow.sh\n# 先檢閱安裝程式\nNXF_VER=26.10.3 bash install-nextflow.sh\nchmod +x nextflow\nexport PATH="$PWD:$PATH"\nnextflow -version\ncd ..',
    points:[['版本確認','已有可用 26.10.3 可直接檢查，不必重複覆寫。'],['PATH','export 只影響目前 shell，新終端機需重新設定。'],['連線需求','安裝器與第一次啟動可能下載套件。只有 launcher 不代表可離線。']],section:'3.5'}),
  s('code','取得教材與預先下載容器','已有專案者直接進入原 demos/nextflow-qc，不要重複 clone。',{
    code:'git clone https://github.com/godkin1211/ClinicalBioinfoCourse.git\ncd ClinicalBioinfoCourse/demos/nextflow-qc\nls main.nf nextflow.config data/samplesheet.csv\nnextflow -version\ndocker info\ndocker pull quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0\ndocker pull quay.io/biocontainers/multiqc:1.30--pyhdfd78af_0\ndocker run --rm \\\n  quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0 fastqc --version\ndocker run --rm \\\n  quay.io/biocontainers/multiqc:1.30--pyhdfd78af_0 multiqc --version',
    wide:true,small:true,points:[['預期版本','FastQC v0.12.1 與 MultiQC 1.30。--rm 只移除該次暫時容器，不刪輸入、結果或映像。']],section:'3.6'}),
  s('code','完整 CSV 轉換邏輯','執行仍使用 main.nf。此處保留空欄位處理，方便逐行對照。',{
    code:'.map { row ->\n    def sample_id = row.sample_id?.trim()\n    def fastq_1 = row.fastq_1?.trim()\n    def fastq_2 = row.fastq_2?.trim()\n    if (!sample_id)\n        error "missing sample_id: ${row}"\n    if (!fastq_1)\n        error "${sample_id}: missing fastq_1"\n    def reads = [file(fastq_1,\n        checkIfExists: true)]\n    if (fastq_2)\n        reads << file(fastq_2,\n            checkIfExists: true)\n    tuple(sample_id, reads)\n}',
    points:[['?. 與 trim','欄位不存在時避免直接呼叫方法，存在時移除頭尾空白。'],['條件分支','sample_id 與 fastq_1 必填。fastq_2 空白可代表單端輸入。'],['限制','存在檢查不驗證序列。本課四檔仍是雙端示意。']],section:'5.2',small:true}),
  s('code','開啟報告與保留版本證據','伺服器報告請移到核准工作站，不為開啟 HTML 將資料上傳公開網站。',{
    code:'# macOS\nopen results/two/multiqc/multiqc_report.html\n# Linux 桌面\nxdg-open results/two/multiqc/multiqc_report.html\n# WSL：開檔案總管，再選報告\nexplorer.exe .\n\nnextflow log\ngit rev-parse HEAD\ndocker image inspect \\\n  quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0 \\\n  --format \'{{json .RepoDigests}}\'',
    wide:true,small:true,points:[['Digest','同樣使用 docker image inspect 記錄 MultiQC 映像 digest，並保存本次命令與資料 checksum。']],section:'6.3、7.4'}),
  s('code','Gmail：應用程式密碼與 secrets','先啟用兩步驟驗證，建立 Google 的 16 字元應用程式密碼。',{
    code:'set +x\nnextflow secrets set GMAIL_SMTP_USER \\\n    \'your.sender@gmail.com\'\ngmail_password_path=\'/absolute/path/to/gmail-app-password\'\ntest -s "$gmail_password_path" && \\\n  nextflow secrets set GMAIL_APP_PASSWORD \\\n    "$(tr -d \'[:space:]\' < "$gmail_password_path")"\nnextflow secrets list',
    wide:true,small:true,points:[['密碼種類','不是平常 Google 登入密碼、驗證碼或 Seqera token。政策不允許時請問管理員。'],['儲存與顯示','檔案放 repo 外，tr 移除分組空白及換行。不用 secrets get 投影密碼。']],section:'9.5.2'}),
  s('code','Gmail：SMTP 設定與通知內容','專案已提供可選 conf/gmail.config，不會由主設定自動載入。',{
    code:'mail {\n    from = secrets.GMAIL_SMTP_USER\n    smtp {\n        host = \'smtp.gmail.com\'\n        port = 587\n        user = secrets.GMAIL_SMTP_USER\n        password = secrets.GMAIL_APP_PASSWORD\n        auth = true\n        starttls.enable = true\n        starttls.required = true\n        ssl.enable = false\n    }\n}',
    points:[['587 與 STARTTLS','連線後升級加密，required 要求升級成功。不同於 465 一開始即加密。'],['最小通知內容','只列 run name、狀態、時間與退出碼。不放病人識別資料。'],['憑證取用位置','由 Nextflow 主機寄出，不把 Gmail 憑證傳給分析容器。']],section:'9.5.2',small:true}),
  s('code','Gmail：成功與失敗都需要測試','先改成自己的獲准收件地址，再以合成資料測試。',{
    code:'nextflow run . -profile docker -c conf/gmail.config \\\n    --input data/samplesheet-one.csv \\\n    --outdir results/gmail-success \\\n    -N learner@example.org\n\nnextflow run . -profile docker -c conf/gmail.config \\\n    --input data/samplesheet-missing.csv \\\n    --outdir results/gmail-failure \\\n    -N learner@example.org',
    wide:true,small:true,points:[['-c 與 -N','-c 載入 SMTP 設定，-N 指定收件者並啟用完成通知。本例不呼叫 AI。'],['確認送達','通知失敗不一定使分析 FAILED。需看收件匣、垃圾郵件與 .nextflow.log。']],section:'9.5.2'}),
  s('table','Gmail 與替代執行路線的限制','選配環境與服務需要另外驗證，不能由 Docker 測試成功推論全部可用。',{
    rows:[['情況','處理與限制'],['Gmail 535／逾時','確認應用程式密碼、完整地址、帳號政策、587 出站連線'],['TLS 錯誤','檢查系統時間、JDK 憑證與代理，不停用憑證驗證'],['standard／conda profile','需已有工具／Conda 並另測，不等於 Docker 路線'],['-stub-run','只產生占位產物，不執行 FastQC／MultiQC，不能驗收分析'],['正式院內通知','優先使用核准 SMTP relay，不開 mail.debug 暴露認證資訊']],section:'8.3、9.5.2'}),
  s('compare','課後自我檢核','回到原始產物回答，而不只記住名詞或命令。',{
    columns:[['執行與觀察','能說明 2 樣本／3 task／4 read 檔。\n真正執行工具並通過 verify.py。\n原樣重跑出現 3 個 CACHED，新增樣本時辨識哪些工作重跑。'],['錯誤與解讀','缺檔測試確實失敗，沒有有效報告。\n能區分 workflow SUCCESS、QC 旗標與臨床有效性。\n知道型別、容器、快取、AI 各自的限制。']],section:'10.1、10.2'}),
];

export const sourceLinks = {
  process:'https://docs.seqera.io/nextflow/process',
  workflow:'https://docs.seqera.io/nextflow/workflow',
  cache:'https://docs.seqera.io/nextflow/cache-and-resume',
  migrate:'https://docs.seqera.io/nextflow/migrations/26-10',
  agent:'https://docs.seqera.io/nextflow/agent',
  ai:'https://docs.seqera.io/multiqc/ai/',
  secrets:'https://docs.seqera.io/nextflow/secrets',
  notifications:'https://docs.seqera.io/nextflow/notifications',
  google:'https://support.google.com/accounts/answer/185833?hl=zh-Hant',
};
