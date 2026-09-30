# AI-assisted analysis human review checklist

## A. Data boundary

- [ ] Data are public, synthetic, or approved for the selected environment.
- [ ] No directly identifying patient information is present.
- [ ] The agent can only access the intended input and output locations.
- [ ] External connectors and uploads are disabled unless explicitly approved.

## B. Question and design

- [ ] Research unit is stated correctly.
- [ ] Primary contrast and estimand are explicit.
- [ ] Paired/repeated/nested design is represented.
- [ ] Batch, site, sex and relevant clinical covariates were assessed.
- [ ] The design can distinguish the effect being requested.

## C. Input integrity

- [ ] Sample IDs match across all files.
- [ ] Duplicate sample and feature IDs are checked.
- [ ] Counts are nonnegative integers where raw counts are expected.
- [ ] Metadata levels and missing values are summarized.
- [ ] Condition × batch/site tables were inspected.
- [ ] Plausibility anomalies are flagged, not automatically corrected.

## D. Execution approval

- [ ] Planned tools and versions are listed.
- [ ] Writes are limited to a new output directory.
- [ ] Sample exclusion requires a separate approval.
- [ ] Threshold changes require rationale and are logged.
- [ ] Destructive or external actions require explicit approval.

## E. Result verification

- [ ] Code actually ran; results are not only narrated.
- [ ] Standard output/error and exit status are preserved.
- [ ] Figures correspond to saved code and data.
- [ ] Key numeric claims were independently recalculated.
- [ ] Multiple testing and effect sizes are reported.
- [ ] Sensitivity analysis addresses major design risks.
- [ ] Null or inconclusive results are retained.

## F. Interpretation

- [ ] Observed evidence is separated from model-dependent inference.
- [ ] Causal language is avoided unless design supports it.
- [ ] Database and literature claims link to primary sources.
- [ ] Limitations include sample size, confounding and assay scope.
- [ ] Clinical interpretation remains with qualified personnel.

## G. Provenance package

- [ ] Original input manifests/checksums
- [ ] Prompt and approval history
- [ ] Analysis plan
- [ ] Code and command log
- [ ] Environment/package versions
- [ ] QC and exclusion/threshold log
- [ ] Tables and figures
- [ ] Final evidence/inference/limitations report
