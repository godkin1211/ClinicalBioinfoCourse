const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL,fileURLToPath} = require('node:url');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname,'..');
const output = path.join(root,'output/playwright/lesson-08');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});
  await page.goto(pathToFileURL(process.env.HANDOUT_HTML || path.join(root,'output/slides/lesson-08-materials.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  assert.ok(!(await page.locator('body').innerText()).includes('第八堂'));
  assert.ok(!(await page.title()).includes('第八堂'));
  assert.equal(await page.locator('main h1').count(),1);
  assert.equal(await page.locator('main h2').count(),10);
  assert.equal(await page.locator('main .workflow-diagram svg').count(),1);
  assert.equal(await page.locator('main .workflow-diagram .node').count(),7);
  assert.match(await page.locator('main').innerText(),/登錄到 Nextflow secrets/);
  assert.match(await page.locator('main').innerText(),/Gmail 通知流程完成或失敗/);
  const frame=page.frameLocator('#qc-report');
  await frame.locator('#global_ai_summary_response').waitFor();
  assert.ok((await frame.locator('#global_ai_summary_response').innerText()).trim().length>100);
  assert.ok(!(await frame.locator('#global_ai_summary_response').innerText()).includes("'signature':"));
  await frame.locator('.js-plotly-plot').first().waitFor();
  for(const sample of ['sampleA_R1','sampleA_R2','sampleB_R1','sampleB_R2']) {
   assert.ok((await frame.locator('body').innerText()).includes(sample));
  }
  for(const link of await page.locator('main a[href]').evaluateAll(es=>es.map(e=>e.href))) {
   if(link.startsWith('file:'))assert.ok(fs.existsSync(fileURLToPath(new URL(link))),link);
  }
  await page.screenshot({path:path.join(output,'desktop-intro.png')});
  await page.locator('#embedded-qc').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'desktop-report.png')});
  await page.locator('#expand-report').click();
  assert.ok(await page.locator('#embedded-qc').evaluate(e=>e.classList.contains('expanded')));
  await page.screenshot({path:path.join(output,'expanded-report.png')});
  await page.locator('#expand-report').click();
  const popupPromise=page.waitForEvent('popup');
  await page.locator('#open-report').click();
  const popup=await popupPromise;
  await popup.locator('#global_ai_summary_response').waitFor();
  assert.ok((await popup.locator('#global_ai_summary_response').innerText()).length>100);
  await popup.close();
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile document overflow');
  await page.locator('main h1').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'mobile-intro.png')});
  assert.deepEqual(errors,[]);
  assert.deepEqual(network,[]);
  console.log('PASS: complete handout, SVG, embedded AI summary, interactive plots, open/expand, links, mobile layout, zero external requests');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
