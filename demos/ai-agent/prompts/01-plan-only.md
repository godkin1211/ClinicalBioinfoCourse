# Plan-only prompt

You are assisting with a synthetic bulk RNA-seq teaching dataset.

Inputs:

- `data/counts.csv`: raw integer gene counts, genes in rows and samples in columns.
- `data/metadata.csv`: sample-level metadata.

For this turn, produce an analysis plan only.

Do not:

- execute code or tools;
- create, modify, rename, or delete files;
- exclude samples;
- correct metadata;
- choose thresholds to maximize statistical significance.

Your plan must state:

1. The research unit, primary contrast, candidate covariates, and intended estimand.
2. Required input checks, including sample-ID alignment, library sizes, condition × batch balance, and expression/metadata consistency.
3. Whether the requested condition effect is identifiable from this design.
4. The proposed QC, exploratory plots, model design, outputs, and sensitivity analyses.
5. Every decision requiring human approval.
6. A list of blockers that would stop execution.

Separate:

- observed facts available directly from the two input schemas;
- checks that still need to be run;
- assumptions;
- proposed analyses.

End with a concise approval request. Do not proceed beyond the plan.
