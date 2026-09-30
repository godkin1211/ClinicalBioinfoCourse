"""Count fixture evidence from SAM stdin. Only supports the supplied 150M records.

Not a general pileup engine: no indels, paired-read overlap, UMI or likelihood model.
"""
import sys

sites = {pos: dict(depth=0, alt=0, forward=0, reverse=0, end=0) for pos in (500, 1500, 2500)}
for line in sys.stdin:
    if line.startswith("@") or not line.strip():
        continue
    fields = line.rstrip().split("\t")
    flag, start = int(fields[1]), int(fields[3])
    if flag & (4 | 256 | 512 | 1024 | 2048):
        continue
    if fields[2] != "chrToy":
        continue
    if fields[5] != "150M" or len(fields[9]) != 150:
        raise ValueError("Only this exercise's 150M records are supported")
    for pos, count in sites.items():
        offset = pos-start
        if not 0 <= offset < 150 or int(fields[4]) < 20 or ord(fields[10][offset])-33 < 20:
            continue
        count["depth"] += 1
        if fields[9][offset] == "T":
            count["alt"] += 1
            count["reverse" if flag & 16 else "forward"] += 1
            count["end"] += min(offset, 149-offset) < 5
print("POS\tDEPTH\tALT\tVAF\tALT_FORWARD\tALT_REVERSE\tALT_END5")
for pos, c in sites.items():
    vaf = f"{c['alt']/c['depth']:.4f}" if c['depth'] else "NA"
    print(f"{pos}\t{c['depth']}\t{c['alt']}\t{vaf}\t{c['forward']}\t{c['reverse']}\t{c['end']}")
