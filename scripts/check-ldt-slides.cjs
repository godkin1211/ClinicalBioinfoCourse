// Local rendering/interaction checks and PDF export. Does not run clinical analyses.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL, fileURLToPath} = require('node:url');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'output/playwright/ldt-20261024');
fs.mkdirSync(out, {recursive:true});

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page = await browser.newPage();
    const issues=[], errors=[], network=[];
    page.on('pageerror', e=>errors.push(e.message));
    page.on('request', r=>{if(/^https?:/.test(r.url()))network.push(r.url());});
    const url=pathToFileURL(path.join(root,'output/slides/ldt-20261024-bioinformatics.html')).href;
    await page.goto(url);
    const count=await page.locator('.slide').count();
    assert.equal(count,32);
    const titles=await page.locator('.slide').evaluateAll(es=>es.map(e=>e.dataset.title));
    assert.ok(!titles.includes('兩份報告都寫 5%：你會一樣相信嗎？'));
    assert.ok(!titles.includes('實驗室認證、施行計畫與流程驗證，不是同一件事'));
    assert.equal(titles[1],'從「測得到」到「有幫助」，中間有三道問題');
    assert.equal(titles[2],'選軟體之前，先定義「我們承諾測到什麼」');
    assert.equal(await page.locator('.appendix').count(),4);
    assert.equal(await page.locator('.content img').count(),9);
    assert.ok(await page.locator('.content img').evaluateAll(es=>es.every(e=>e.src.startsWith('data:image/')&&e.alt.length>5)));
    assert.match(await page.locator('.speaker').textContent(),/奇美醫院精準醫學核心實驗室組長邱家軍/);
    for(const viewport of [{width:1440,height:900},{width:1366,height:768}]) {
      await page.setViewportSize(viewport);
      await page.evaluate(()=>document.fonts.ready);
      for(let i=0;i<count;i++) {
        await page.evaluate(i=>go(i),i);
        await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        const bad=await page.locator('.active').evaluate(s=>{
          const bounds=s.getBoundingClientRect(), footer=s.querySelector('footer').getBoundingClientRect();
          return [...s.querySelectorAll('h2,.content *')].filter(e=>e.getClientRects().length).flatMap(e=>{
            const r=e.getBoundingClientRect();
            return r.bottom>footer.top-3||r.right>bounds.right-15||r.left<bounds.left||e.clientWidth>0&&e.scrollWidth>e.clientWidth+2
              ? [{tag:e.tagName,text:e.textContent.slice(0,70),bottom:r.bottom,footer:footer.top}]:[];
          });
        });
        if(bad.length)issues.push({slide:i+1,viewport:viewport.width,bad});
        assert.ok(await page.locator('.active img').evaluateAll(es=>es.every(e=>e.complete&&e.naturalWidth>0)));
        await page.screenshot({path:path.join(out,`${viewport.width}-${String(i+1).padStart(2,'0')}.png`)});
      }
    }
    for(let i=0;i<count;i++) {
      await page.evaluate(i=>go(i),i);
      await page.locator('#explanation').click();
      assert.ok((await page.locator('#explain-body').textContent()).length>200);
      assert.ok(await page.locator('#explain').evaluate(e=>e.scrollWidth<=e.clientWidth+1));
      await page.keyboard.press('ArrowRight');
      assert.equal(await page.locator('#status').textContent(),`${i+1} / ${count}`);
      await page.keyboard.press('Escape');
    }
    await page.keyboard.press('Home');
    await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#status').textContent(),'2 / 32');
    await page.locator('#next').click();assert.equal(await page.locator('#status').textContent(),'3 / 32');
    await page.locator('#overview').click();await page.locator('#toc button').nth(27).click();assert.equal(await page.locator('#status').textContent(),'28 / 32');
    await page.keyboard.press('e');assert.ok(await page.locator('#explain').evaluate(e=>e.open));
    await page.locator('#explain-close').click();
    await page.locator('#fullscreen').click();assert.ok(await page.evaluate(()=>document.fullscreenElement));
    await page.evaluate(()=>document.exitFullscreen());
    await page.goto(url+'#slide-20');assert.equal(await page.locator('#status').textContent(),'20 / 32');
    assert.equal(await page.locator('.active img').count(),1);
    for(const link of await page.locator('a').evaluateAll(es=>es.map(e=>e.href).filter(h=>h.startsWith('file:')))) {
      assert.ok(fs.existsSync(fileURLToPath(new URL(link))),link);
    }
    await page.emulateMedia({media:'print'});assert.equal(await page.locator('.slide:visible').count(),count);
    await page.pdf({path:path.join(root,'output/pdf/ldt-20261024-bioinformatics.pdf'),printBackground:true,preferCSSPageSize:true});
    const nojs=await browser.newContext({javaScriptEnabled:false});
    const fallback=await nojs.newPage();await fallback.goto(url);assert.equal(await fallback.locator('.slide:visible').count(),count);await nojs.close();
    const reading=await browser.newPage({viewport:{width:1366,height:768}});
    await reading.goto(pathToFileURL(path.join(root,'output/slides/ldt-20261024-explanations.html')).href);
    assert.equal(await reading.locator('article').count(),count);
    assert.deepEqual(await reading.locator('article h2').allTextContents(),titles.map((title,i)=>`${String(i+1).padStart(2,'0')} · ${title}`));
    const ids=await reading.locator('[id]').evaluateAll(es=>es.map(e=>e.id));assert.equal(new Set(ids).size,ids.length);
    await reading.close();
    const review=await browser.newPage({viewport:{width:1600,height:1220}});
    for(let start=0;start<count;start+=12) {
      const items=[];
      for(let i=start;i<Math.min(start+12,count);i++) {
        const png=fs.readFileSync(path.join(out,`1366-${String(i+1).padStart(2,'0')}.png`)).toString('base64');
        items.push(`<div><b>${i+1}</b><img src="data:image/png;base64,${png}"></div>`);
      }
      await review.setContent(`<style>body{margin:8px;background:#dce5df;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font:16px sans-serif}img{display:block;width:100%}b{display:block;padding:3px}</style>${items.join('')}`);
      await review.screenshot({path:path.join(out,`contact-${start/12+1}.png`),fullPage:true});
    }
    const report={count,issues,errors,network,checks:'both viewports; all notes and images; local links; keyboard/button navigation; TOC; fullscreen; hash; print/PDF; no-JS; reading anchors'};
    fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
    if(issues.length||errors.length||network.length)process.exitCode=1;
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
