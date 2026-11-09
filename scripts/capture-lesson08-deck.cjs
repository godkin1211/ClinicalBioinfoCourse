// Capture existing, sanitized handout evidence. Does not call external AI APIs.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const out=path.join(root,'assets/lesson-08');
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:2});
    await page.route(/^https?:/,route=>route.abort());
    await page.goto(pathToFileURL(path.join(root,'output/slides/lesson-08-materials.html')).href);
    await page.locator('.workflow-diagram svg').screenshot({path:path.join(out,'qc-workflow.png')});
    const frame=page.frameLocator('#qc-report');
    await frame.locator('.js-plotly-plot').first().waitFor();
    const table=frame.locator('#general_stats_table_table');
    await table.screenshot({path:path.join(out,'multiqc-general-stats.png')});
    console.log('Saved existing workflow and actual synthetic-data MultiQC table screenshots');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
