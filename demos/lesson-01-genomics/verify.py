"""Check the concrete expected results of this synthetic teaching exercise."""
import argparse
import math
from pathlib import Path


def table(path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    return [dict(zip(header, line.split())) for line in lines[1:] if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    root = parser.parse_args().directory
    for name, size in [("raw.fam", 40), ("raw.bim", 6000),
                       ("clean.fam", 39), ("clean.bim", 5999)]:
        assert len((root / name).read_text().splitlines()) == size, name
    samples = {r["IID"]: r for r in table(root / "qc.imiss")}
    assert math.isclose(float(samples["S40"]["F_MISS"]), 1/3, abs_tol=0.0001)
    variants = {r["SNP"]: r for r in table(root / "qc.lmiss")}
    assert math.isclose(float(variants["v1"]["F_MISS"]), .275)
    pairs = table(root / "related.genome")
    duplicate = next(r for r in pairs if {r["IID1"], r["IID2"]} == {"S01", "S02"})
    assert float(duplicate["PI_HAT"]) > .99
    pcs = [line.split() for line in (root / "structure.eigenvec").read_text().splitlines()]
    assert len(pcs) == 39 and all(len(row) == 6 for row in pcs)
    assert all(math.isfinite(float(x)) for row in pcs for x in row[2:])
    rohs = table(root / "roh.hom")
    assert any(r["IID"] == "S03" and r["CHR"] == "1" for r in rohs)
    assert (root / "calls.tsv").read_text().strip() == "chrToy\t1000\tA\tC\t0/1\t40\t20,20"
    review = [line.split("\t") for line in (root / "review.tsv").read_text().splitlines()]
    assert [r[1] for r in review] == ["PASS", "LowDP", "PASS", "LowMQ"]
    assert review[2][3] == "38,2" and review[1][4] == "3"
    print("PASS: sizes, missingness, duplicate, PCA, ROH, called SNV and review cases")


if __name__ == "__main__":
    main()
