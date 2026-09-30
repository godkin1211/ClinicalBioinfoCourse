#!/usr/bin/env python3
"""Deterministic input checks for the synthetic RNA-seq agent lesson."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_METADATA_COLUMNS = {"sample_id", "condition", "batch", "reported_sex"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit sample alignment, batch balance, library sizes, and marker consistency."
    )
    parser.add_argument("--counts", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    return parser.parse_args()


def read_counts(path: Path) -> tuple[list[str], dict[str, dict[str, int]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header or header[0] != "gene_id":
            raise ValueError("counts must start with a gene_id column")

        sample_ids = header[1:]
        if not sample_ids or len(sample_ids) != len(set(sample_ids)):
            raise ValueError("counts sample IDs must be present and unique")

        genes: dict[str, dict[str, int]] = {}
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(f"counts line {line_number} has {len(row)} fields; expected {len(header)}")
            gene_id = row[0]
            if not gene_id or gene_id in genes:
                raise ValueError(f"counts gene IDs must be non-empty and unique: {gene_id!r}")

            values: dict[str, int] = {}
            for sample_id, raw_value in zip(sample_ids, row[1:]):
                value = int(raw_value)
                if value < 0:
                    raise ValueError(f"negative count for {gene_id}/{sample_id}")
                values[sample_id] = value
            genes[gene_id] = values

    return sample_ids, genes


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("metadata has no header")
        missing = REQUIRED_METADATA_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"metadata is missing required columns: {sorted(missing)}")

        rows: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            sample_id = row["sample_id"].strip()
            if not sample_id or sample_id in rows:
                raise ValueError(f"metadata sample IDs must be non-empty and unique at line {line_number}")
            rows[sample_id] = {key: (value or "").strip() for key, value in row.items()}
    return rows


def marker_pattern(genes: dict[str, dict[str, int]], sample_id: str) -> str:
    required = {"XIST", "RPS4Y1"}
    if not required.issubset(genes):
        return "not_assessed"

    xist = genes["XIST"][sample_id]
    rps4y1 = genes["RPS4Y1"][sample_id]
    if xist >= 100 and rps4y1 <= 20:
        return "F-like"
    if xist <= 20 and rps4y1 >= 100:
        return "M-like"
    return "ambiguous"


def main() -> int:
    args = parse_args()
    sample_ids, genes = read_counts(args.counts)
    metadata = read_metadata(args.metadata)

    count_samples = set(sample_ids)
    metadata_samples = set(metadata)
    only_counts = sorted(count_samples - metadata_samples)
    only_metadata = sorted(metadata_samples - count_samples)

    print("RNA-seq teaching-data preflight")
    print(f"counts: {len(genes)} genes x {len(sample_ids)} samples")
    print(f"metadata: {len(metadata)} samples")
    print(f"sample IDs aligned: {not only_counts and not only_metadata}")
    if only_counts:
        print(f"  only in counts: {', '.join(only_counts)}")
    if only_metadata:
        print(f"  only in metadata: {', '.join(only_metadata)}")
    if only_counts or only_metadata:
        return 2

    table: dict[str, Counter[str]] = defaultdict(Counter)
    for sample_id in sample_ids:
        row = metadata[sample_id]
        table[row["condition"]][row["batch"]] += 1

    batches = sorted({row["batch"] for row in metadata.values()})
    print("\ncondition x batch")
    print("condition\t" + "\t".join(batches))
    imbalance_detected = False
    for condition in sorted(table):
        counts = [table[condition][batch] for batch in batches]
        total = sum(counts)
        dominant_fraction = max(counts) / total if total else 0
        imbalance_detected = imbalance_detected or dominant_fraction >= 0.75
        print(condition + "\t" + "\t".join(str(value) for value in counts))
    print(f"condition-batch imbalance flag: {imbalance_detected}")

    library_sizes = {
        sample_id: sum(gene_counts[sample_id] for gene_counts in genes.values())
        for sample_id in sample_ids
    }
    median_size = statistics.median(library_sizes.values())
    print("\nlibrary sizes")
    for sample_id in sample_ids:
        ratio = library_sizes[sample_id] / median_size
        print(f"{sample_id}\t{library_sizes[sample_id]}\t{ratio:.2f}x median")

    print("\nreported sex vs expression-marker pattern")
    mismatches: list[str] = []
    for sample_id in sample_ids:
        reported = metadata[sample_id]["reported_sex"]
        pattern = marker_pattern(genes, sample_id)
        consistent = pattern in {"not_assessed", "ambiguous"} or pattern.startswith(reported)
        status = "consistent" if consistent else "REVIEW"
        if not consistent:
            mismatches.append(sample_id)
        print(f"{sample_id}\treported={reported}\tpattern={pattern}\t{status}")

    print("\nsummary")
    print(f"metadata/expression anomalies requiring human review: {len(mismatches)}")
    if mismatches:
        print(f"  samples: {', '.join(mismatches)}")
    print("no input values were modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
