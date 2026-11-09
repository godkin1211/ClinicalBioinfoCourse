// Move only slide-number shapes; preserve all other ZIP member bytes.
// Run with the bundled Node runtime. JSZip is supplied by that runtime.
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const {createRequire}=require('node:module');
const {createHash}=require('node:crypto');
const runtime=process.env.RUNTIME_NODE_MODULES || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const JSZip=createRequire(path.join(runtime,'package.json'))('jszip');
const root=path.resolve(__dirname,'..');
const source=path.resolve(process.argv[2] || path.join(root,'output/slides/lesson-08-nextflow.pptx'));
const output=path.resolve(process.argv[3] || path.join(root,'output/slides/lesson-08-nextflow-numbered.pptx'));
const sha=b=>createHash('sha256').update(b).digest('hex');
const attrs=s=>Object.fromEntries([...s.matchAll(/([\w:]+)="([^"]*)"/g)].map(m=>[m[1],m[2]]));
const shapes=s=>[...s.matchAll(/<p:sp(?=[\s>])[\s\S]*?<\/p:sp>/g)].map(m=>m[0]);
const isNumber=s=>/<p:ph\b[^>]*\btype="sldNum"/.test(s)||/<p:cNvPr\b[^>]*\bname="page-number"/.test(s);
const withoutNumbers=s=>s.replace(/<p:sp(?=[\s>])[\s\S]*?<\/p:sp>/g,m=>isNumber(m)?'':m);
const emu=n=>Math.round(n*9525);
(async()=>{
  assert.notEqual(source,output,'Keep the manually edited source unchanged');
  await assert.rejects(fs.access(output),{code:'ENOENT'},'Choose a new output path');
  const original=await fs.readFile(source),zip=await JSZip.loadAsync(original);
  const manifest=await zip.file('ppt/presentation.xml').async('string');
  const rels=await zip.file('ppt/_rels/presentation.xml.rels').async('string');
  const targets=new Map([...rels.matchAll(/<Relationship\b[^>]*\/?>/g)].map(m=>{const a=attrs(m[0]);return [a.Id,a.Target];}));
  const slidePaths=[...manifest.matchAll(/<p:sldId\b[^>]*\/?>/g)].map(m=>path.posix.normalize('ppt/'+targets.get(attrs(m[0])['r:id'])));
  assert.ok(slidePaths.length>1);
  const changed=[];
  for(const [index,name] of slidePaths.entries()){
    const xml=await zip.file(name).async('string');
    const nums=shapes(xml).filter(isNumber);
    if(index===0){assert.equal(nums.length,0,'Cover must have no slide number');continue;}
    assert.equal(nums.length,1,`Expected one slide number on page ${index+1}`);
    const old=nums[0];
    const spPr=`<p:spPr><a:xfrm><a:off x="${emu(864)}" y="${emu(14)}"/><a:ext cx="${emu(48)}" cy="${emu(24)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>`;
    let replacement=old.replace(/<p:spPr\b[^>]*\/>|<p:spPr\b[^>]*>[\s\S]*?<\/p:spPr>/,spPr);
    replacement=replacement.replace(/<a:bodyPr\b[^>]*\/>|<a:bodyPr\b[^>]*>[\s\S]*?<\/a:bodyPr>/,'<a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/>');
    replacement=replacement.replace(/<a:rPr\b[^>]*\/>|<a:rPr\b[^>]*>[\s\S]*?<\/a:rPr>/g,'<a:rPr lang="en-US" sz="1200" b="0"><a:solidFill><a:srgbClr val="D8D2E2"/></a:solidFill><a:latin typeface="Inter"/></a:rPr>');
    const updated=xml.replace(old,replacement);
    assert.equal(withoutNumbers(updated),withoutNumbers(xml),`Non-number content changed on page ${index+1}`);
    zip.file(name,updated);changed.push(name);
  }
  const bytes=await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'});
  const check=await JSZip.loadAsync(bytes),before=await JSZip.loadAsync(original);
  for(const [name,entry] of Object.entries(before.files)){
    if(!entry.dir&&!changed.includes(name))assert.deepEqual(await check.file(name).async('nodebuffer'),await entry.async('nodebuffer'),name);
  }
  assert.deepEqual(await fs.readFile(source),original,'Source changed during processing');
  await fs.writeFile(output,bytes,{flag:'wx'});
  await fs.writeFile(output.replace(/\.pptx$/, '-build.json'),JSON.stringify({
    source:path.relative(root,source),source_sha256:sha(original),final_sha256:sha(bytes),
    slide_count:slidePaths.length,numbered_slide_count:changed.length,
    page_number:{position:'top-right',x_px:864,y_px:14,width_px:48,height_px:24,font_size_pt:12,cover:false},
    preservation:'All non-number shapes and non-slide ZIP members are byte-identical to the current source; original file unchanged.',
  },null,2)+'\n');
  console.log(`PASS: ${changed.length}/${slidePaths.length} pages numbered at top-right; cover and all unrelated content unchanged.\n${output}`);
})().catch(e=>{console.error(e);process.exit(1);});
