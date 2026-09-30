"""Verify this exercise's outputs, not the validity of a clinical pipeline."""
import argparse
import csv
import math
from pathlib import Path
from models import expected_vaf


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence(path):
    with path.open() as handle:
        return {int(r["POS"]): r for r in csv.DictReader(handle, delimiter="\t")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    root = parser.parse_args().directory
    tumor = evidence(root / "tumor.evidence.tsv")
    normal = evidence(root / "normal.evidence.tsv")
    require(set(tumor) == set(normal) == {500, 1500, 2500}, "Unexpected positions")
    expected = {500: (400,20,10,10,0), 1500: (400,20,20,0,20), 2500: (400,200,100,100,0)}
    columns = ["DEPTH", "ALT", "ALT_FORWARD", "ALT_REVERSE", "ALT_END5"]
    for pos, counts in expected.items():
        require(tuple(int(tumor[pos][c]) for c in columns) == counts, f"Tumor {pos}")
        require(math.isclose(float(tumor[pos]["VAF"]), counts[1]/counts[0]), f"VAF {pos}")
        require(int(normal[pos]["DEPTH"]) == 200, f"Normal depth {pos}")
        require(int(normal[pos]["ALT"]) == (100 if pos == 2500 else 0), f"Normal ALT {pos}")
    rows = [r.split("\t") for r in (root / "candidates.tsv").read_text().splitlines()]
    require([r[3] for r in rows] == ["PASS", "ReviewBias", "NormalEvidence"], "VCF flags")
    require(rows[0][4:] == ["TUMOR:380,20:400:0.05", "NORMAL:200,0:200:0"], "VCF samples/counts")
    with (root / "copy_number.seg").open() as handle:
        segments = list(csv.DictReader(handle, delimiter="\t"))
    require(len(segments) == 3, "CN segment count")
    require(math.isclose(float(segments[1]["seg.mean"]), math.log2(1.4), abs_tol=1e-6), "CN model")
    require(math.isclose(expected_vaf(.1,1,1,2), .05), "Low-purity model")
    require(math.isclose(expected_vaf(.2,1,1,6), 1/14), "CN/VAF model")
    for name in ["tumor.bam", "normal.bam", "tumor.bam.bai", "normal.bam.bai",
                 "reference.fa.fai", "candidates.vcf.gz", "candidates.vcf.gz.tbi"]:
        require((root/name).stat().st_size > 0, f"Missing/empty {name}")
    print("PASS: BAM-derived counts, bias patterns, VCF samples/flags, CN/VAF models, indexed artifacts")


if __name__ == "__main__":
    main()
