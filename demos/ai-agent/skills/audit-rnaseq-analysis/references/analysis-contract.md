# Bulk RNA-seq analysis contract

## Required counts input

- CSV with `gene_id` in the first column.
- One sample per remaining column.
- Unique, nonempty gene and sample identifiers.
- Nonnegative integer values for raw-count workflows.

## Required metadata input

- One row per sample.
- Unique `sample_id`.
- `condition` and `batch`.
- Add subject ID for paired, repeated, or longitudinal data.
- Add site and relevant prespecified clinical covariates when applicable.

Counts and metadata must contain exactly the same samples before analysis.

## Plan output

Include:

- research unit;
- primary contrast and estimand;
- model formula or equivalent;
- candidate covariates and identifiability assessment;
- QC and input checks;
- planned figures/tables;
- sensitivity analyses;
- blockers;
- approval requests.

## Execution output

Create a new output directory containing:

- `analysis_plan.md`
- `environment.txt`
- saved executable code
- command and error logs
- input audit
- QC tables/figures
- model outputs
- exclusion/threshold decision log
- `report.md`

## Hard stops

Stop rather than continue when:

- sample IDs do not align;
- required metadata are missing;
- counts are incompatible with the planned method;
- condition is completely confounded with batch/site;
- data use is not approved;
- requested clinical interpretation exceeds the approved scope.

## Interpretation language

- **Evidence:** direct output supported by a named artifact.
- **Inference:** conclusion dependent on a stated model or database.
- **Speculation:** hypothesis requiring new data or experiment.
