# Execute-after-approval prompt

The following actions are approved:

- Read only `data/counts.csv` and `data/metadata.csv`.
- Create a new `outputs/` directory.
- Validate sample IDs, integer/nonnegative counts, duplicate identifiers, library sizes, condition × batch balance, and sex-marker/metadata consistency.
- Generate code and execute it.
- Produce exploratory PCA and sample-level QC.
- Propose, but do not silently alter, the differential-expression design.

The following actions are not approved:

- Modify either input file.
- Exclude any sample.
- Change condition, batch, reported sex, or sample IDs.
- Select a QC threshold or model only because it yields more significant results.
- Upload data to another service.
- Present a clinical diagnosis or treatment recommendation.

Write all outputs under `outputs/` and preserve:

1. `analysis_plan.md`
2. `environment.txt`
3. executable analysis code
4. command log
5. input-audit tables
6. figures with the code used to create them
7. `decisions_pending.md`
8. `report.md` with separate evidence, inference, limitations, and unresolved issues

If a blocked condition appears, stop and document it rather than inventing a correction.
