# Reproducing the research training workflow

These are reproduction instructions, not actions performed during the website phase. The checked-in frozen v1.0.0 artifact must remain unchanged. Use a separate fresh working directory for training experiments, without the existing models or generated modeling reports.

## Official source and fingerprint

Download the combined 2021 BRFSS **SAS Transport Format** archive from [CDC's annual data page](https://www.cdc.gov/brfss/annual_data/annual_2021.html). Extract `LLCP2021.XPT` into `data/raw/LLCP2021.XPT` in the reproduction directory. Do not commit the archive, raw records, splits or respondent review tables.

Recorded input fingerprints for the completed run:

- Raw XPT SHA-256: `ae7fea17e09740fd2bd306b217c58df42d86060eab85baf0d6af67e977a1eca2`.
- Original ZIP SHA-256: `e8a6e290cdcb6bff82d8f37dff6c3f3e435d428191eb529a716cf9f5316aa621`.

The current CDC page describes a July 2023 update; compare the downloaded file fingerprint before claiming exact reproduction. A different release is a new research input and must not silently replace the completed run.

## Create an isolated source workspace

From the project root, create a new sibling directory using this explicit source-only copy. It refuses to overwrite an existing directory:

```powershell
python scripts/prepare_training_workspace.py --destination ../cardio-risk-reproduction
Set-Location ../cardio-risk-reproduction
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Place the official XPT at the raw path above before continuing. The helper copies source, tests, pinned requirements, dictionary and CDC documentation; it copies no model, respondent file, membership file or generated experiment report.

## Preparation, split and training commands

```powershell
.\.venv\Scripts\python.exe -m src.data.build_dataset
.\.venv\Scripts\python.exe -m src.data.verify_reproducibility
.\.venv\Scripts\python.exe -m src.models.preflight
.\.venv\Scripts\python.exe -m src.models.train_all --stage train --device auto
.\.venv\Scripts\python.exe -m src.models.train_all --stage select
.\.venv\Scripts\python.exe -m src.models.train_all --stage evaluate
.\.venv\Scripts\python.exe -m src.models.train_all --stage report
```

The cleaner verifies the target definition and variable-specific mappings, retains missing predictors, divides the released BMI by 100 once, and removes unusable targets. It produces 434,058 supervised records for the recorded source.

Seed **42** governs target-stratified allocation of complete identical labeled-record groups to approximately **70%/15%/15%** train/validation/test row quotas. Recorded split sizes are 303,841 / 65,109 / 65,108. Source-row IDs and equality groups are separate audit outputs, never inputs. Training is further partitioned into disjoint grouped model-fit and calibration-only portions (80%/20%). Learned preprocessing is fitted using training data only. Validation selects model, calibration and threshold; test evaluation happens only after freezing. The evaluation stage returns saved results if evaluation was already completed.

## Selection and expected evidence

Candidate families include dummy, logistic regression, random forest, histogram gradient boosting, XGBoost, LightGBM and native CatBoost. Selection prioritizes validation average precision, with Brier score, feature-set uncertainty, missingness, subgroup behavior and CPU inference also considered. CatBoost without education/income was selected: validation AP **0.33936**, ROC-AUC **0.84196**, Brier **0.06299**. Its uncalibrated scores outperformed its calibrated alternative on Brier score. See [model selection report](../reports/modeling/model_selection_report.md).

The selected baseline uses 220 iterations, depth 6, learning rate 0.08, no class reweighting and no calibration. The recorded GPU training run used seed 42; hardware/backend/library differences can affect exact binary reproduction. Validation/test ROC-AUC around 0.84–0.85 and AP around 0.34–0.35 describe the completed run, not guaranteed acceptance criteria or permission to optimize the held-out test set.

Default research threshold: **0.20943938491134126**. Independent-test recall **0.51548**, precision **0.31682**, ROC-AUC **0.84676**, AP **0.34479**. Higher-sensitivity policies trade fewer misses for more false positives. No operating point is a clinical cutoff.

Frozen artifact SHA-256:

`4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1`

The repository includes this 182,048-byte frozen artifact using ordinary Git. Reproduction generates a separate research artifact; do not replace v1.0.0, its policies or its golden fixtures. This project classifies patterns associated with existing self-reported CHD/MI; it does not predict future cardiovascular events.
