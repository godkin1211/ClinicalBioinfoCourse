// Reusable Artifact Session callbacks. Import the supplied PPTX before prepare().
// This file edits the imported master/layout structure, not a newly styled deck.
import {slides, sourceLinks} from './lesson08-deck-content.mjs';
const GREEN='#0DC09D', WHITE='#FFFFFF', MUTED='#D8D2E2';
const text=(slide,name,value,x,y,w,h,size=22,color=WHITE,bold=false,font='Inter')=>{
  const sh=slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=value;
  sh.text.style={fontSize:size,typeface:font,color,bold,insets:0,wrap:'square',autoFit:'none',verticalAlignment:'top'};
  return sh;
};
const block=(slide,name,heading,body,x,y,w,h=100,size=22)=>{
  text(slide,`${name}-heading`,heading,x,y,w,32,24,GREEN,true);
  text(slide,`${name}-body`,body,x,y+36,w,h-36,size);
};

export async function prepare({presentation}) {
  if(presentation.slides.items.length!==17) throw Error('Start from the original 17-slide template');
  const originals=[...presentation.slides.items];
  const cover=(await presentation.inspect({select:'$.slides[0].elements[*]',include:['id','kind','position']})).records;
  for(const element of cover.filter(e=>e.kind==='textbox')){
    const sh=presentation.resolve(element.id), isTitle=element.position.top<300;
    sh.text=isTitle?'Nextflow\n生物資訊\n工作流程入門':'高雄長庚臨床生物資訊系列課程\n奇美醫院精準醫學核心實驗室組長邱家軍\n2026-11-10';
    sh.position=isTitle?{left:356.51,top:210,width:544.47,height:205}:{left:330,top:425,width:571,height:92};
    sh.text.style={fontSize:isTitle?50:18.67,typeface:'Inter',bold:true,color:isTitle?GREEN:WHITE,alignment:'right',insets:0,autoFit:'none'};
  }
  const targets=[originals[0]];
  for(const spec of slides.slice(1)){
    const index=spec.kind==='triple'?1:spec.kind==='concept'?4:6;
    targets.push(originals[index].duplicate());
  }
  const all=(await presentation.inspect({select:'$.slides[*]',include:['id']})).records;
  const ids=targets.map(t=>all[presentation.slides.items.findIndex(s=>s.id===t.id)].id);
  presentation.slides.keep(ids);
  presentation.slides.reorder(ids);
  return {ids,count:ids.length};
}

async function clearBody(presentation,slide,kind){
  const current=await presentation.inspect({select:'$.slides[*]',include:['id','elements.id','elements.kind','elements.position','elements.text','elements.name']});
  const record=current.records.find(r=>presentation.resolve(r.id).id===slide.id);
  const remove=record.elements.filter(e=>{
    if(e.position?.top<110 && e.kind==='textbox') return false;
    if(kind==='triple' && e.kind==='image') return false;
    if(kind==='concept') return false;
    return true;
  }).map(e=>e.id);
  if(remove.length)presentation.delete(remove);
  return record;
}

function header(presentation,slide,record,spec,index){
  for(const e of record.elements.filter(e=>e.kind==='textbox' && e.position?.top<110)){
    const sh=presentation.resolve(e.id);
    if(e.position.top<75){
      sh.text=spec.title;
      sh.position={left:48,top:39,width:864,height:39};
      sh.text.style={fontSize:26.59,typeface:'Inter',color:WHITE,bold:true,insets:0,autoFit:'none'};
    }else{
      sh.text=spec.subtitle;
      sh.position={left:48,top:84,width:864,height:30};
      sh.text.style={fontSize:18.67,typeface:'Inter Light',color:WHITE,bold:false,insets:0,autoFit:'none'};
    }
  }
  text(slide,'page-number',String(index+1).padStart(2,'0'),864,505,35,20,13,MUTED);
}

export async function buildBatch({presentation,input}){
  const {start,end,assetsRoot}=input;
  for(let i=start;i<Math.min(end,slides.length);i++){
    const spec=slides[i],slide=presentation.slides.getItem(i);
    slide.speakerNotes.text=`教材對應：lessons/lesson-08-materials.md，第 ${spec.section||'1'} 節。\n${spec.code?'程式片段供閱讀，請以 demos/nextflow-qc/ 的完整程式執行。\n':''}來源：\n${Object.values(sourceLinks).join('\n')}\n範本：使用者提供的 Nextflow Intro 2026.pptx。\n示範為人工合成資料，並非臨床驗證流程。`;
    if(i===0) continue;
    const record=await clearBody(presentation,slide,spec.kind);
    header(presentation,slide,record,spec,i);
    if(spec.kind==='triple'){
      // Retain the three original mint icons and original column rhythm.
      spec.columns.forEach(([a,b],j)=>block(slide,`column-${j}`,a,b,134+j*240,232,230,190,20));
      text(slide,'takeaway',spec.bottom,48,449,840,48,20,MUTED);
    }else if(spec.kind==='concept'){
      // Reuse the template's native process/channel/workflow illustration.
      for(const e of record.elements.filter(e=>e.position?.top>=110)){
        const o=presentation.resolve(e.id),p=e.position;
        o.position={left:560+(p.left-285)*.76,top:140+(p.top-125)*.76,width:p.width*.76,height:p.height*.76};
        if(e.text){
          o.text={Processes:'Process',Channels:'Channel',Workflow:'Workflow'}[e.text]||e.text;
          o.position={...o.position,width:130,height:40};
          o.text.style={fontSize:19,typeface:'Inter',color:WHITE,alignment:'left',insets:0,wrap:'none'};
        }
      }
      spec.left.forEach(([a,b],j)=>block(slide,`definition-${j}`,a,b,48,138+j*113,430,105,22));
    }else if(spec.kind==='overview'){
      slide.images.add({path:`${assetsRoot}/qc-workflow.png`,alt:'2 個樣本分別做 FastQC，收齊四個 ZIP 後執行 MultiQC',fit:'contain',position:{left:48,top:129,width:864,height:188}});
      spec.lines.forEach(([a,b],j)=>block(slide,`flow-${j}`,a,b,48+j*294,336,272,115,21));
      text(slide,'takeaway',spec.bottom,48,458,840,40,21,GREEN,true);
    }else if(spec.kind==='compare'){
      spec.columns.forEach(([a,b],j)=>block(slide,`compare-${j}`,a,b,48+j*450,143,414,300,24));
      if(spec.bottom)text(slide,'takeaway',spec.bottom,48,455,840,45,21,MUTED);
    }else if(spec.kind==='code'){
      // Match the reference's dark code surface; all code text remains editable.
      const x=48,y=135,w=spec.wide?864:500;
      const lines=spec.code.split('\n').length;
      const size=spec.wide?(spec.small?17:18):(spec.small?17:19);
      const h=spec.wide?Math.min(260,Math.max(145,lines*(size*1.15)+20)):340;
      const bg=slide.shapes.add({geometry:'rect',name:'code-surface',position:{left:x,top:y,width:w,height:h},fill:'#292B35',line:{fill:'none',width:0}});
      text(slide,'code',spec.code,x+14,y+12,w-28,h-20,size,'#EDF3DF',false,'Menlo');
      if(spec.wide){
        const yy=y+h+18,col=(864-(spec.points.length-1)*22)/spec.points.length;
        spec.points.forEach(([a,b],j)=>block(slide,`annotation-${j}`,a,b,48+j*(col+22),yy,col,493-yy,19));
      }else{
        spec.points.forEach(([a,b],j)=>block(slide,`annotation-${j}`,a,b,570,139+j*118,342,112,20));
      }
    }else if(spec.kind==='table'){
      const rows=spec.rows.length,cols=spec.rows[0].length;
      const table=slide.tables.add({rows,columns:cols,left:48,top:140,width:864,height:spec.bottom?300:330,values:spec.rows,columnWidths:cols===2?[274,590]:[205,320,339]});
      table.borders.assign({fill:'#665E76',width:.6,style:'solid'});
      for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
        const cell=table.getCell(r,c);
        cell.fill=r===0?'#2C243B':'#160F26';
        cell.text.style={fontSize:20,typeface:'Inter',color:r===0?GREEN:WHITE,bold:r===0,insets:10,verticalAlignment:'middle'};
      }
      if(spec.bottom)text(slide,'takeaway',spec.bottom,48,458,840,40,20,MUTED);
    }else if(spec.kind==='report'){
      slide.images.add({path:`${assetsRoot}/multiqc-general-stats.png`,alt:'已執行之合成資料 MultiQC General Statistics，四個 read 檔',fit:'contain',position:{left:48,top:135,width:864,height:213}});
      spec.points.forEach(([a,b],j)=>block(slide,`interpretation-${j}`,a,b,48+j*294,365,272,123,21));
    }else if(spec.kind==='links'){
      spec.links.forEach(([a,b],j)=>{
        const sh=text(slide,`resource-${j}`,a,48,136+j*65,850,40,24,GREEN,true);
        sh.text.get(a).link={uri:b,isExternal:true};
      });
    }else if(spec.kind==='appendix'){
      text(slide,'appendix-heading','課後實作',48,156,840,75,52,GREEN,true);
      text(slide,'appendix-body',spec.body,48,257,800,185,27,WHITE);
    }
  }
  return {built:[start,end-1],total:slides.length};
}

export {slides};
