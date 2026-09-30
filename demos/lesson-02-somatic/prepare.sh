#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# Run inside a generated practice directory. Reruns replace same-named outputs.
samtools faidx reference.fa
for sample in tumor normal; do
  samtools view -b "$sample.sam" | samtools sort -o "$sample.bam"
  samtools index "$sample.bam"
  samtools quickcheck -v "$sample.bam"
  samtools flagstat "$sample.bam" > "$sample.flagstat.txt"
done
bcftools view -Oz -o candidates.vcf.gz candidates.vcf
bcftools index -t candidates.vcf.gz
bcftools query -f '%CHROM\t%POS\t%ID\t%FILTER[\t%SAMPLE:%AD:%DP:%AF]\n' candidates.vcf.gz > candidates.tsv
samtools view tumor.bam | python3 "$script_dir/audit_reads.py" > tumor.evidence.tsv
samtools view normal.bam | python3 "$script_dir/audit_reads.py" > normal.evidence.tsv
