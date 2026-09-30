"""Generate synthetic somatic-review fixtures; no patient data, no caller simulation."""
import argparse
import math
from pathlib import Path
import random


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="New directory; existing paths are rejected")
    root = parser.parse_args().output
    root.mkdir(parents=True, exist_ok=False)
    rng = random.Random(20260914)
    sequence = [rng.choice("ACGT") for _ in range(5000)]
    for pos in (500, 1500, 2500):
        sequence[pos-1] = "C"
    reference = "".join(sequence)
    (root / "reference.fa").write_text(">chrToy\n" + reference + "\n")
    for sample, depth in [("TUMOR", 400), ("NORMAL", 200)]:
        with (root / f"{sample.lower()}.sam").open("w") as out:
            out.write(f"@HD\tVN:1.6\tSO:unsorted\n@SQ\tSN:chrToy\tLN:5000\n@RG\tID:{sample}\tSM:{sample}\tPL:ILLUMINA\n")
            for pos in (500, 1500, 2500):
                nalt = depth // 2 if pos == 2500 else (20 if sample == "TUMOR" else 0)
                for i in range(depth):
                    is_alt = i < nalt
                    artifact = pos == 1500 and is_alt
                    start = pos - (149 - i % 4 if artifact else 40 + i % 70)
                    flag = 0 if artifact else (16 if i % 2 else 0)
                    bases = list(reference[start-1:start+149])
                    if is_alt:
                        bases[pos-start] = "T"
                    # SAM stores reverse-strand sequence in reference-facing orientation.
                    out.write(f"{sample}_{pos}_{i}\t{flag}\tchrToy\t{start}\t60\t150M\t*\t0\t0\t{''.join(bases)}\t{'I'*150}\tRG:Z:{sample}\n")
    header = '''##fileformat=VCFv4.2
##source=synthetic_teaching_fixture_NOT_a_somatic_caller
##contig=<ID=chrToy,length=5000>
##FILTER=<ID=ReviewBias,Description="Artificial teaching flag: strand and read-end bias">
##FILTER=<ID=NormalEvidence,Description="Artificial teaching flag: evidence in normal">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Illustrative genotype; not inferred">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Synthetic allele counts">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Synthetic depth">
##FORMAT=<ID=AF,Number=A,Type=Float,Description="Synthetic observed alternate fraction">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tTUMOR\tNORMAL
'''
    (root / "candidates.vcf").write_text(header +
        "chrToy\t500\tA\tC\tT\t.\tPASS\t.\tGT:AD:DP:AF\t0/1:380,20:400:0.05\t0/0:200,0:200:0\n" +
        "chrToy\t1500\tB\tC\tT\t.\tReviewBias\t.\tGT:AD:DP:AF\t0/1:380,20:400:0.05\t0/0:200,0:200:0\n" +
        "chrToy\t2500\tD\tC\tT\t.\tNormalEvidence\t.\tGT:AD:DP:AF\t0/1:200,200:400:0.5\t0/1:100,100:200:0.5\n")
    # Independent analytical CN illustration: NOT computed from the SAM coverage.
    ratio = math.log2((.2 * 6 + .8 * 2) / 2)
    (root / "copy_number.seg").write_text(
        "ID\tchrom\tloc.start\tloc.end\tnum.mark\tseg.mean\n"
        f"CN_DEMO\tchrToy\t1\t2999\t30\t0\n"
        f"CN_DEMO\tchrToy\t3000\t4000\t10\t{ratio:.6f}\n"
        f"CN_DEMO\tchrToy\t4001\t5000\t10\t0\n")
    print(f"Created {root}; A/B: tumor 20/400, normal 0/200; D: 50% in both.")


if __name__ == "__main__":
    main()
