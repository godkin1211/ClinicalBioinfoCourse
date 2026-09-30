#!/usr/bin/env bash
set -euo pipefail
# Input SAM is synthetic and already aligned; this does not test alignment.
samtools faidx reference.fa
samtools view -b aligned.sam | samtools sort -o sample.bam
samtools index sample.bam
samtools flagstat sample.bam > flagstat.txt
samtools depth -aa sample.bam > depth.tsv
bcftools mpileup -Ou -f reference.fa -a FORMAT/DP,FORMAT/AD sample.bam |
  bcftools call -mv -Oz -o calls.vcf.gz
bcftools index calls.vcf.gz
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT[\t%GT\t%DP\t%AD]\n' calls.vcf.gz > calls.tsv
bcftools query -f '%POS\t%FILTER[\t%GT\t%AD\t%DP\t%GQ]\n' review.vcf > review.tsv
