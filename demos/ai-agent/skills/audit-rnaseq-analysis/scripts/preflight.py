#!/usr/bin/env python3
"""Dependency-free structural preflight for bulk RNA-seq counts and metadata."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    return parser.parse_args()


def load_counts(path: Path) -> tuple[list[str], int]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header or header[0] != "gene_id":
            raise ValueError("counts first column must be gene_id")
        samples = header[1:]
        if not samples or len(samples) != len(set(samples)):
            raise ValueError("counts sample IDs must be nonempty and unique")

        genes: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(f"counts line {line_number}: wrong field count")
            gene = row[0]
            if not gene or gene in genes:
                raise ValueError(f"counts line {line_number}: duplicate/empty gene_id")
            genes.add(gene)
            for value in row[1:]:
                if int(value) < 0:
                    raise ValueError(f"counts line {line_number}: negative count")
    return samples, len(genes)


def load_metadata(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"sample_id", "condition", "batch"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"metadata missing columns: {sorted(missing)}")
        records: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            sample = (row["sample_id"] or "").strip()
            if not sample or sample in records:
                raise ValueError(f"metadata line {line_number}: duplicate/empty sample_id")
            records[sample] = {key: (value or "").strip() for key, value in row.items()}
    return records


def main() -> int:
    args = arguments()
    samples, gene_count = load_counts(args.counts)
    metadata = load_metadata(args.metadata)

    count_set = set(samples)
    metadata_set = set(metadata)
    only_counts = sorted(count_set - metadata_set)
    only_metadata = sorted(metadata_set - count_set)

    print(f"counts: {gene_count} genes x {len(samples)} samples")
    print(f"metadata: {len(metadata)} samples")
    if only_counts or only_metadata:
        print(f"BLOCKER only_in_counts={only_counts}")
        print(f"BLOCKER only_in_metadata={only_metadata}")
        return 2

    table: dict[str, Counter[str]] = defaultdict(Counter)
    for sample in samples:
        record = metadata[sample]
        table[record["condition"]][record["batch"]] += 1

    batches = sorted({record["batch"] for record in metadata.values()})
    print("condition x batch:")
    print("condition\t" + "\t".join(batches))
    for condition in sorted(table):
        values = [table[condition][batch] for batch in batches]
        print(condition + "\t" + "\t".join(str(value) for value in values))

    condition_to_batches = {
        condition: {
            record["batch"]
            for record in metadata.values()
            if record["condition"] == condition
        }
        for condition in table
    }
    if len(condition_to_batches) > 1 and all(
        len(batches_for_condition) == 1
        for batches_for_condition in condition_to_batches.values()
    ):
        sole_batches = {
            next(iter(batches_for_condition))
            for batches_for_condition in condition_to_batches.values()
        }
        if len(sole_batches) == len(condition_to_batches):
            print("BLOCKER condition appears completely confounded with batch")
            return 3

    print("PASS structural preflight; human review is still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
