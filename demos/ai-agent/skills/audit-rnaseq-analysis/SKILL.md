---
name: audit-rnaseq-analysis
description: Plan, preflight, execute, and audit human-verifiable bulk RNA-seq analyses from a raw count matrix and sample metadata. Use when an agent is asked to inspect RNA-seq counts, design differential-expression or QC work, detect sample/batch/metadata risks, create reproducible artifacts, or review another analyst's RNA-seq outputs. Require an explicit human gate before sample exclusion, metadata changes, writes outside a new output directory, or scientific interpretation.
---

# Audit RNA-seq Analysis

Use a gated workflow. Do not jump from a broad question directly to differential expression.

## 1. Establish the data boundary

Confirm:

- counts and metadata paths;
- whether data are synthetic, public, or approved for the current environment;
- allowed read/write locations;
- whether external tools, services, or uploads are approved.

Stop if sensitive data would leave an approved environment.

## 2. Read the analysis contract

Read [references/analysis-contract.md](references/analysis-contract.md). Treat missing required fields, unmatched sample IDs, duplicate identifiers, noninteger/negative raw counts, or an unidentifiable primary contrast as blockers.

Run:

```bash
python scripts/preflight.py --counts <counts.csv> --metadata <metadata.csv>
```

Do not change inputs in response to a warning.

## 3. Produce a plan before execution

State:

- research unit, contrast, estimand, covariates, paired/nested structure;
- input checks and QC;
- condition × batch/site balance and identifiability;
- proposed transformations, model, outputs, and sensitivity analyses;
- tools and versions;
- blockers and human decisions.

Separate observed facts, assumptions, proposed checks, and planned analyses.

Stop for human approval before executing code or writing analysis outputs.

## 4. Enforce review gates

Require explicit approval before:

- excluding a sample or gene;
- changing metadata or sample identity;
- changing a predeclared contrast/outcome;
- selecting or changing a threshold;
- writing outside a new output directory;
- using an external service;
- interpreting a result clinically.

Flag a suspected label mismatch as `needs human review`. Never silently repair it.

## 5. Execute reproducibly

After approval:

1. Write only to a new output directory.
2. Save the plan and environment versions.
3. Save executable code before running it.
4. Preserve commands, standard output/error, tables, and figures.
5. Log every exclusion and threshold with evidence and approver.
6. Stop on blockers rather than inventing missing metadata.

Use raw integer counts for count-based differential-expression tools. Do not substitute TPM or normalized values without explicit methodological justification.

## 6. Verify independently

Check:

- sample IDs and dimensions;
- condition × batch/site tables;
- library sizes and transformations;
- figure labels against code;
- reported numbers against saved tables;
- sample-level statistical unit;
- multiple testing and effect sizes;
- sensitivity to major design risks.

An agent's self-review is not independent validation. Use deterministic scripts or a second reproducible calculation for key claims.

## 7. Report bounded conclusions

Organize the final report into:

1. Observed evidence
2. Model-dependent inference
3. Unresolved issues
4. Limitations
5. Decisions still requiring a human

Do not convert association into causation or research output into a clinical recommendation.
