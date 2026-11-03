#!/usr/bin/env python3
"""Verify the supplied synthetic QC exercise, not arbitrary clinical data."""
import argparse
import csv
import math
import re
from pathlib import Path
import zipfile


def verify(root, samples, cached=False, ai=False):
    expected = {f'{sample}_R{read}' for sample in samples for read in (1, 2)}
    for name in sorted(expected):
        html = root / 'fastqc' / f'{name}_fastqc.html'
        assert html.stat().st_size > 1000, f'Missing/empty HTML: {html}'
        with zipfile.ZipFile(root / 'fastqc' / f'{name}_fastqc.zip') as archive:
            assert archive.testzip() is None, f'Corrupt ZIP: {name}'
            data = archive.read(f'{name}_fastqc/fastqc_data.txt').decode()
        assert 'Total Sequences\t4\n' in data, f'Read count: {name}'
        assert 'Sequence length\t40\n' in data, f'Read length: {name}'
        assert 'Encoding\tSanger / Illumina 1.9\n' in data, f'Encoding: {name}'
        quality = data.split('>>Per base sequence quality\t', 1)[1].splitlines()
        assert float(quality[2].split('\t')[1]) == 30, f'Cycle 1: {name}'
    assert (root / 'multiqc' / 'multiqc_report.html').stat().st_size > 1000
    with (root / 'multiqc/multiqc_data/multiqc_general_stats.txt').open() as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    assert {row['Sample'] for row in rows} == expected, 'MultiQC sample set mismatch'
    for row in rows:
        # MultiQC 1.30 exports total_sequences in millions in general stats.
        assert math.isclose(float(row['fastqc-total_sequences']), 4e-6)
        assert float(row['fastqc-avg_sequence_length']) == 40
    with (root / 'pipeline_info/execution_trace.txt').open() as handle:
        trace = list(csv.DictReader(handle, delimiter='\t'))
    assert len(trace) == len(samples) + 1, 'Task count mismatch'
    assert all(row['status'] in ('COMPLETED', 'CACHED') for row in trace)
    assert all(row['exit'] == '0' for row in trace)
    if cached:
        assert all(row['status'] == 'CACHED' for row in trace), 'Expected all cached'
    for name in ('execution_report.html', 'execution_timeline.html', 'pipeline_dag.html'):
        assert (root / 'pipeline_info' / name).stat().st_size > 100
    if ai:
        report = (root / 'multiqc/multiqc_report.html').read_text()
        summary = re.search(r'<div id="global_ai_summary_response"[^>]*>(.*?)</div>', report, re.S)
        assert summary and re.sub(r'<[^>]+>', '', summary[1]).strip(), 'AI summary missing (MultiQC SUCCESS alone is insufficient)'
        print('PASS: AI summary text is embedded in the report (not a scientific accuracy check)')
    print(f'PASS: {len(samples)} samples, {len(expected)} FASTQ reports, '
          f'{len(trace)} successful tasks; FastQC content and MultiQC verified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outdir', type=Path)
    parser.add_argument('--samples', nargs='+', required=True)
    parser.add_argument('--cached', action='store_true')
    parser.add_argument('--ai', action='store_true', help='Require embedded AI summary text in MultiQC 1.30 HTML')
    args = parser.parse_args()
    verify(args.outdir, args.samples, args.cached, args.ai)
