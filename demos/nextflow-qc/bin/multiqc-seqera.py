#!/usr/bin/env python3
"""MultiQC 1.30 compatibility entrypoint for Seqera's report-summary API.

Only Seqera requests are routed; no installed package is modified. Request and
response payloads remain MultiQC's. See README for upstream evidence and limits.
"""
import sys
import multiqc
from multiqc import report
from multiqc.core.ai import SeqeraClient
from multiqc.__main__ import run_multiqc

if multiqc.__version__ != '1.30':
    sys.exit('This compatibility entrypoint is restricted to MultiQC 1.30')

original_request = SeqeraClient._request_with_error_handling_and_retries


def report_summary_request(self, url, headers, body, retries=None):
    if not url.endswith('/internal-ai/query'):
        raise ValueError('Unexpected Seqera API route; review compatibility adapter')
    return original_request(
        self,
        'https://ai-api.seqera.io/v1/web/internal-ai/report-summary',
        headers, body, retries=retries,
    )


SeqeraClient._request_with_error_handling_and_retries = report_summary_request
try:
    run_multiqc()
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise
if not report.ai_global_summary or not report.ai_global_summary.strip():
    sys.exit('Seqera AI summary missing; refusing to report AI success')
