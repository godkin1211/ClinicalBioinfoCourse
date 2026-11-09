// Validate a session-exported PPTX and publish the final teaching deliverable.
// Usage: node scripts/finalize-lesson08-deck.mjs /absolute/path/to/draft.pptx
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {slides} from './lesson08-deck-content.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill=process.env.PRESENTATIONS_SKILL_DIR || '/Users/godkin/.codex/plugins/cache/openai-primary-runtime/presentations/26.1104.22356/skills/presentations';
const python=process.env.RUNTIME_PYTHON || '/Users/godkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
if(!process.argv[2])throw Error('Provide the session-exported draft PPTX path');
const staging=path.join(root,'tmp/lesson08-deck');
await fs.mkdir(staging,{recursive:true});
const candidate=path.join(staging,'candidate.pptx');
await fs.copyFile(process.argv[2],candidate);
const finalPath=path.join(root,'output/slides/lesson-08-nextflow.pptx');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const tables=slides.flatMap((s,i)=>s.kind==='table'?[i+1]:[]);
const result=await finalizePresentation({
  workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:python,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:slides.length,
  requiredNativeTableOwnerSlides:tables,
  requiredNativeChartOwnerSlides:[],
  layoutArgs:['--expected-slide-size-emu','9144000,5143500','--validate-bullet-geometry','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],
  // Inter and Inter Light retain the supplied design; Menlo is for editable code.
  fontPolicy:{basis:'design',families:['Inter','Inter Light','Menlo'],scriptFonts:{ea:'Heiti TC'}},
  verifyArtifactToolImport:true,
  receiptPath:path.join(staging,'validation.json'),
});
const source=await fs.readFile(path.join(root,'lessons/lesson-08-materials.md'));
const deck=await fs.readFile(finalPath);
await fs.writeFile(path.join(root,'output/slides/lesson-08-nextflow-build.json'),JSON.stringify({
  source:'lessons/lesson-08-materials.md',
  source_sha256:createHash('sha256').update(source).digest('hex'),
  template_name:'Nextflow Intro 2026.pptx',
  template_role:'User-supplied 16:9 theme, master, cover art, mint icons and process diagram',
  slide_count:slides.length,
  course_date:'2026-11-10',
  language:'zh-Hant',
  final_sha256:createHash('sha256').update(deck).digest('hex'),
  slides:slides.map((s,i)=>({number:i+1,title:s.title,source_section:s.section||'1',appendix:i>=40})),
  notes:['Source is the current working copy, including its existing course-date edit.','No scientific analysis, AI API request or email was executed to create this deck.','Original user-supplied template is not republished as an unmodified file.'],
},null,2)+'\n');
console.log(JSON.stringify({finalPath,slideCount:slides.length,validation:result.status||'complete'},null,2));
