// Local visual QA with the bundled Playwright runtime; no external page requests.
const {chromium} = require('/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'output/playwright/lesson-02');
fs.mkdirSync(output, {recursive:true});

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const page = await browser.newPage({viewport:{width:1440,height:900}});
  const errors=[], network=[], issues=[];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {if (/^https?:/.test(request.url())) network.push(request.url());});
  const url = pathToFileURL(path.join(root,'output/slides/lesson-02-somatic.html')).href;
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  const count = await page.locator('.slide').count();
  assert.equal(count, 64);
  assert.match(await page.locator('.slide').nth(1).getAttribute('data-title'), /同一種癌症/);
  assert.match(await page.locator('.slide').nth(17).getAttribute('data-title'), /FastQC：先看圖形/);
  for (const [index, name] of [[39,'TMB：'],[40,'MSI：'],[41,'HRD：']]) {
    assert.ok((await page.locator('.slide').nth(index).getAttribute('data-title')).startsWith(name));
  }
  assert.match(await page.locator('.slide').nth(45).getAttribute('class'), /closing/);
  for (const viewport of [{width:1440,height:900}, {width:1366,height:768}]) {
    await page.setViewportSize(viewport);
    for (let i=0; i<count; i++) {
      await page.evaluate(i => go(i), i);
      for (const expanded of [false,true]) {
        await page.locator('.active details').evaluateAll((els,open) => els.forEach(e=>e.open=open),expanded);
        const bad = await page.locator('.active').evaluate(s => {
          const footer=s.querySelector('footer').getBoundingClientRect(), bounds=s.getBoundingClientRect();
          return [...s.querySelectorAll('.content *, h2')].filter(e=>e.getClientRects().length).flatMap(e=>{
            if (e.closest('details:not([open])') && !e.matches('details,summary')) return [];
            const r=e.getBoundingClientRect();
            return r.bottom>footer.top-3 || r.right>bounds.right-15 || r.left<bounds.left || e.scrollWidth>e.clientWidth+2 && e.clientWidth>0
              ? [{tag:e.tagName,text:e.textContent.slice(0,65),bottom:Math.round(r.bottom),footer:Math.round(footer.top)}] : [];
          });
        });
        if (bad.length) issues.push({slide:i+1,viewport:viewport.width,expanded,bad});
      }
      await page.screenshot({path:path.join(output,`${viewport.width===1440?'slide':'projector'}-${String(i+1).padStart(2,'0')}.png`)});
    }
  }
  await page.evaluate(()=>go(0));
  await page.keyboard.press('ArrowRight'); assert.equal(await page.locator('#status').textContent(),`2 / ${count}`);
  await page.keyboard.press('End'); assert.equal(await page.locator('#status').textContent(),`${count} / ${count}`);
  await page.keyboard.press('Home'); assert.equal(await page.locator('#status').textContent(),`1 / ${count}`);
  await page.locator('#next').click(); assert.equal(await page.locator('#status').textContent(),`2 / ${count}`);
  await page.locator('#overview').click(); await page.locator('#toc button').nth(18).click();
  assert.equal(await page.locator('#status').textContent(),`19 / ${count}`);
  await page.evaluate(()=>go(slides.findIndex(s=>s.querySelector('details'))));
  await page.locator('.active summary').click(); assert.equal(await page.locator('.active details').getAttribute('open'),null);
  await page.locator('.active summary').click(); assert.notEqual(await page.locator('.active details').getAttribute('open'),null);
  await page.locator('#fullscreen').click(); assert.equal(await page.evaluate(()=>!!document.fullscreenElement),true);
  await page.evaluate(()=>document.exitFullscreen());
  await page.goto(url+'#slide-23'); assert.equal(await page.locator('#status').textContent(),`23 / ${count}`);
  // The detailed learner explanations must match every slide and stay accessible.
  assert.equal(await page.locator('template').count(),count);
  assert.equal(await page.locator('.slide .walkthrough').count(),count-1);
  for (let i=0;i<count;i++) {
    await page.evaluate(i=>go(i),i);
    await page.locator('#explanation').click();
    assert.ok((await page.locator('#explain-title').textContent()).startsWith(`${i+1} / ${count}`));
    assert.equal(await page.locator('#explain-body h3').count(),3);
    assert.ok((await page.locator('#explain-body').textContent()).length>150);
    assert.ok(await page.locator('#explain').evaluate(e=>e.scrollWidth<=e.clientWidth+1));
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#status').textContent(),`${i+1} / ${count}`);
    if(i===17) await page.screenshot({path:path.join(output,'explanation-18.png')});
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#explain').evaluate(e=>e.open),false);
  }
  await page.keyboard.press('e'); assert.equal(await page.locator('#explain').evaluate(e=>e.open),true);
  await page.locator('#explain-close').click();
  const reading=await browser.newPage({viewport:{width:1366,height:768}});
  await reading.goto(pathToFileURL(path.join(root,'output/slides/lesson-02-explanations.html')).href+'#page-18');
  assert.equal(await reading.locator('article').count(),count);
  assert.equal(await reading.locator('article h3').count(),count*3);
  await reading.screenshot({path:path.join(output,'reading-18.png')});
  await reading.emulateMedia({media:'print'});
  assert.equal(await reading.locator('article:visible').count(),count);
  await reading.close();
  const links = await page.locator('a').evaluateAll(els=>els.map(e=>e.href).filter(h=>h.startsWith('file:')));
  for (const link of links) assert.ok(fs.existsSync(require('node:url').fileURLToPath(new URL(link))),link);
  await page.emulateMedia({media:'print'}); assert.equal(await page.locator('.slide:visible').count(),count);
  const nojs=await browser.newContext({javaScriptEnabled:false});
  const fallback=await nojs.newPage(); await fallback.goto(url);
  assert.equal(await fallback.locator('.slide:visible').count(),count); await nojs.close();
  // Contact sheets use the unaltered screenshots as HTML images for manual review.
  const review = await browser.newPage({viewport:{width:1600,height:1220}});
  for (let start=0; start<count; start+=12) {
    const items=[];
    for (let i=start; i<Math.min(start+12,count); i++) {
      const png=fs.readFileSync(path.join(output,`projector-${String(i+1).padStart(2,'0')}.png`)).toString('base64');
      items.push(`<div><b>${i+1}</b><img src="data:image/png;base64,${png}"></div>`);
    }
    await review.setContent(`<style>body{margin:8px;background:#dce5df;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font:16px sans-serif}img{display:block;width:100%}b{display:block;padding:3px}</style>${items.join('')}`);
    await review.screenshot({path:path.join(output,`contact-${start/12+1}.png`),fullPage:true});
  }
  const report={count,issues,errors,network,checks:`both viewports; FastQC insertion at slide 18; navigation; TOC; answer toggle; fullscreen; hash; local links; print visibility; no-JS fallback; all ${count} explanations; E/Escape/modal navigation isolation; reading edition and print`};
  fs.writeFileSync(path.join(output,'qa.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
  await browser.close();
  if (issues.length || errors.length || network.length) process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
