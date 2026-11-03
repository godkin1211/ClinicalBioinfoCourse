// Compile the current Markdown plus a previously executed, synthetic QC report.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'lessons/lesson-08-materials.md');
const out = path.join(root, 'output/slides/lesson-08-materials.html');
const reportPath = path.resolve(process.argv[2] || path.join(root, 'demos/nextflow-qc/results/seqera-ai-20261103/multiqc/multiqc_report.html'));
const mermaidPath = process.env.MERMAID_JS || path.join(root, 'tmp/lesson08/mermaid.min.js');
const hash = text => crypto.createHash('sha256').update(text).digest('hex');
const pandoc = args => cp.execFileSync('pandoc', args, {encoding:'utf8', maxBuffer:32*1024*1024});

(async () => {
  const markdown = fs.readFileSync(source, 'utf8');
  let report = fs.readFileSync(reportPath, 'utf8');
  if (!/id="global_ai_summary_response"[^>]*>\s*\S/.test(report)) throw Error('Report must contain an executed AI summary');
  if (!report.includes('sampleA_R1') || !report.includes('sampleB_R2')) throw Error('Expected synthetic sample IDs missing');
  const reportHash = hash(report);
  // The older provider formats rich response blocks as a Python repr. Publish
  // only the saved final text, never non-summary blocks or opaque signatures.
  const summaryPattern = /(<div id="global_ai_summary_response"[^>]*>)([\s\S]*?)(<\/div>)/;
  const summaryMatch = report.match(summaryPattern);
  let summaryNormalized = false;
  if (summaryMatch && summaryMatch[2].trim().startsWith('<p>[{')) {
    const extract = `import ast, html, json, re, sys
blocks = ast.literal_eval(html.unescape(re.sub(r'<[^>]+>', '', sys.stdin.read())).strip())
text = '\\n\\n'.join(b['text'] for b in blocks if b.get('type') == 'text')
if not text.strip(): raise ValueError('No final summary text')
print(json.dumps(text))`;
    const text = JSON.parse(cp.execFileSync('python3',['-c',extract],{input:summaryMatch[2],encoding:'utf8'}));
    const formatted = cp.execFileSync('pandoc',['-f','markdown','-t','html'],{input:text,encoding:'utf8'});
    report = report.replace(summaryPattern, (_,open,body,close)=>open+formatted+close);
    summaryNormalized = true;
  }
  // Publish a read-only snapshot: no local user paths or access to online APIs.
  report = report.replaceAll(root + '/', 'ClinicalBioinfoCourse/');
  if (report.includes('/Users/')) throw Error('Unrecognized private path; inspect before publishing');
  report = report.replace(/<head[^>]*>/i, `$&<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval' blob: data:; style-src 'unsafe-inline' data:; img-src data: blob:; font-src data:; connect-src 'none'; worker-src blob:;">`);
  const data = Buffer.from(report).toString('base64');
  const ast = JSON.parse(pandoc([source, '-f','markdown', '-t','json']));
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  let diagramCount = 0;
  try {
    const page = await browser.newPage();
    await page.setContent('<html><body></body></html>');
    await page.addScriptTag({path:mermaidPath});
    for (const block of ast.blocks) {
      if (block.t !== 'CodeBlock' || !block.c[0][1].includes('mermaid')) continue;
      const svg = await page.evaluate(async text => {
        mermaid.initialize({startOnLoad:false,theme:'neutral',flowchart:{htmlLabels:false}});
        return (await mermaid.render('qc_workflow', text)).svg;
      }, block.c[1]);
      block.t = 'RawBlock';
      block.c = ['html', `<figure class="workflow-diagram">${svg}<figcaption>樣本資料流與任務依賴關係</figcaption></figure>`];
      diagramCount++;
    }
  } finally { await browser.close(); }
  function walk(item) {
    if (!item || typeof item !== 'object') return;
    if (item.t === 'Link') {
      const target = item.c[2][0];
      if (!/^(https?:|mailto:|#)/.test(target)) {
        const [file, fragment] = target.split('#');
        const absolute = path.resolve(path.dirname(source), file);
        if (!fs.existsSync(absolute)) throw Error(`Missing local link: ${target}`);
        item.c[2][0] = path.relative(path.dirname(out), absolute) + (fragment ? '#' + fragment : '');
      }
    }
    for (const value of Object.values(item)) {
      if (Array.isArray(value)) value.forEach(walk);
      else if (value && typeof value === 'object') walk(value);
    }
  }
  walk(ast);
  const index = ast.blocks.findIndex(b => b.t === 'Header' && JSON.stringify(b).includes('6.4'));
  if (index < 0) throw Error('QC report insertion heading not found');
  ast.blocks.splice(index, 0, {t:'RawBlock',c:['html',`<section id="embedded-qc" class="report-panel">
<h3>實際執行結果：互動式 MultiQC 報告</h3>
<p>2026-11-03 執行的兩個人工合成樣本，FastQC 0.12.1 → MultiQC 1.30；包含已取得的 Seqera AI 摘要。這是已保存的結果，不會重新執行分析或呼叫 AI。每個 FASTQ 僅 4 reads，不能當作臨床品質標準。</p>
<div class="report-actions"><button id="expand-report" type="button">放大報告</button><button id="open-report" type="button">另開報告</button><a id="download-report" download="lesson-08-multiqc-report.html">下載 QC 報告</a></div>
<p class="small">此教學副本禁止連外。不需輸入 token；AI 按鈕不會呼叫服務。圖表、樣本篩選與既有摘要可離線檢視。個人本機路徑已替換；QC 數值不變，AI 回覆只呈現已保存的最終文字。</p>
<iframe id="qc-report" title="兩個合成樣本的 MultiQC 與 Seqera AI 摘要" loading="lazy"></iframe>
<noscript><p>請啟用 JavaScript 以載入內嵌報告；講義正文仍可閱讀。</p></noscript>
</section>`]});
  const compiled = cp.execFileSync('pandoc', ['-f','json','-t','html5','--standalone','--toc','--toc-depth=2',
    '--metadata','lang:zh-Hant','--metadata','title:Nextflow 生物資訊流程講義',
    '--template',path.join(root,'scripts/lesson08-handout.html')], {input:JSON.stringify(ast),encoding:'utf8',maxBuffer:32*1024*1024});
  const output = compiled.replace('<!--QC_DATA-->', `<script id="qc-data" type="application/octet-stream">${data}</script>`);
  fs.mkdirSync(path.dirname(out), {recursive:true});
  fs.writeFileSync(out, output);
  fs.writeFileSync(path.join(root,'output/slides/lesson-08-materials-build.json'), JSON.stringify({
    source:'lessons/lesson-08-materials.md',source_sha256:hash(markdown),report_source:path.relative(root,reportPath),
    report_sha256:reportHash,published_report_sha256:hash(report),summary_normalized:summaryNormalized,mermaid_version:'10.9.3',diagrams:diagramCount,
    source_note:'Built from the current working copy; existing local header-date edits are preserved, not staged by this build.',
    report_note:'Executed synthetic data; local paths replaced; online requests blocked; QC values unchanged; only final AI text is presented.'
  },null,2)+'\n');
  console.log(`Built ${out}; ${diagramCount} SVG diagram; embedded MultiQC snapshot`);
})().catch(e=>{console.error(e);process.exit(1);});
