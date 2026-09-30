# Result-audit prompt

Audit the completed `outputs/` as if it were produced by another analyst.

Do not modify the outputs during the first audit pass.

Check:

1. Every sample and gene in the analysis can be traced to the original inputs.
2. Counts remained raw integers until the documented transformation step.
3. The condition × batch relationship is reported and reflected in the model discussion.
4. Any metadata/expression mismatch is flagged but not silently corrected.
5. PCA axes, transformations, color mappings, and sample labels match the code.
6. Statistical unit and sample size are stated correctly.
7. No sample was excluded without a recorded human decision.
8. Numeric claims in `report.md` can be recalculated from saved tables.
9. Evidence, model-dependent inference, and speculation are separated.
10. Software and package versions are recorded.

Return:

- `PASS`, `FAIL`, or `NEEDS HUMAN DECISION` for each item;
- the exact supporting artifact or missing artifact;
- the smallest corrective action;
- a final recommendation on whether the analysis is ready for scientific interpretation.
