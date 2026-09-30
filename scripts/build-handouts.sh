#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
mkdir -p output/pdf tmp/pdfs
if [[ $# -eq 0 ]]; then
  set -- 01 02
fi
for lesson in "$@"; do
  pdf_author='OO醫院精準醫學核心實驗室組長邱XX'
  case "$lesson" in
    01) pdf_title='從 SNP Array 到 WES/WGS：基因體資料分析入門' ;;
    02) pdf_title='癌症體細胞基因體分析：從定序證據到可信的候選事件' ;;
    03)
      pdf_title='Bulk RNA-seq：從檢體、表現量到差異表現與可變剪接'
      pdf_author='奇美醫院精準醫學核心實驗室組長邱家軍'
      ;;
    *) echo "Unsupported lesson: $lesson" >&2; exit 1 ;;
  esac
  pandoc "lessons/lesson-${lesson}-materials.md" \
    --from=markdown --to=typst --standalone --syntax-highlighting=none --wrap=none \
    --template=scripts/handout.typst \
    --lua-filter=scripts/handout-paths.lua \
    --metadata="course-label:第 ${lesson} 堂" \
    --metadata="pdf-title:$pdf_title" \
    --metadata="pdf-author:$pdf_author" \
    --output="tmp/pdfs/lesson-${lesson}-materials.typ"
  typst compile --root "$project_dir" \
    "tmp/pdfs/lesson-${lesson}-materials.typ" "output/pdf/lesson-${lesson}-materials.pdf"
done
