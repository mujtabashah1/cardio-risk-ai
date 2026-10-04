# Subgroup deployment notes

The shared threshold is unchanged for every subgroup. There are no sex- or age-specific operating rules. Differences are descriptive, affected by prevalence, self-report and selection, and are not a fairness certification.

| Dataset | Sex code | Rows | Positive cases | Recall | Specificity | Precision |
| --- | --- | --- | --- | --- | --- | --- |
| validation | 1 | 30786 | 3035 | 0.5986820428336079 | 0.8647976649490109 | 0.3262704255701203 |
| validation | 2 | 34323 | 2264 | 0.3975265017667844 | 0.9328737639976292 | 0.2948885976408912 |
| test | 1 | 30694 | 3097 | 0.5979980626412658 | 0.8621589303185129 | 0.3274398868458274 |
| test | 2 | 34414 | 2201 | 0.3993639254884144 | 0.935274578586285 | 0.2965587044534413 |

CDC respondent sex codes: 1 Male, 2 Female. Validation recall was about 59.87% versus 39.75%; therefore equal subgroup performance must not be claimed. See the original `reports/modeling/subgroup_metrics.csv` for all age groups and both datasets. Age groups with fewer than 30 positives or fewer than 200 rows were flagged unstable; low-prevalence younger groups have particularly limited precision/recall estimates. No new subgroup optimization was performed.

Other deployment limits: cross-sectional existing self-report, no prospective endpoint, U.S./territory BRFSS 2021 context, unweighted respondent modeling, predictor missingness shifts in the fixed split, screening/access effects, repeated validation-selection bias, and need for external validation.

## Saved age-group results

| Dataset | Age group | Rows | Positive cases | Recall | Specificity | Precision | Unstable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validation | 18-24 | 3727 | 19 | 0.1579 | 0.9992 | 0.5000 | True |
| validation | 25-29 | 3060 | 32 | 0.1562 | 0.9977 | 0.4167 | False |
| validation | 30-34 | 3769 | 43 | 0.1628 | 0.9957 | 0.3043 | False |
| validation | 35-39 | 4068 | 52 | 0.0962 | 0.9943 | 0.1786 | False |
| validation | 40-44 | 4251 | 99 | 0.2121 | 0.9901 | 0.3387 | False |
| validation | 45-49 | 4121 | 156 | 0.2179 | 0.9861 | 0.3820 | False |
| validation | 50-54 | 5114 | 250 | 0.2760 | 0.9626 | 0.2749 | False |
| validation | 55-59 | 5756 | 377 | 0.3714 | 0.9308 | 0.2734 | False |
| validation | 60-64 | 6635 | 596 | 0.4446 | 0.8993 | 0.3036 | False |
| validation | 65-69 | 6906 | 796 | 0.4698 | 0.8543 | 0.2959 | False |
| validation | 70-74 | 6664 | 951 | 0.5825 | 0.8015 | 0.3282 | False |
| validation | 75-79 | 4611 | 792 | 0.6389 | 0.7340 | 0.3325 | False |
| validation | 80 or older | 5194 | 1059 | 0.6742 | 0.6346 | 0.3209 | False |
| validation | Missing age | 1233 | 77 | 0.2597 | 0.9602 | 0.3030 | False |
| test | 18-24 | 3796 | 13 | 0.0769 | 0.9997 | 0.5000 | True |
| test | 25-29 | 3146 | 23 | 0.0000 | 0.9987 | 0.0000 | True |
| test | 30-34 | 3719 | 45 | 0.0667 | 0.9970 | 0.2143 | False |
| test | 35-39 | 4250 | 68 | 0.1029 | 0.9964 | 0.3182 | False |
| test | 40-44 | 4340 | 108 | 0.1667 | 0.9917 | 0.3396 | False |
| test | 45-49 | 4237 | 121 | 0.1901 | 0.9876 | 0.3108 | False |
| test | 50-54 | 5005 | 247 | 0.3117 | 0.9620 | 0.2984 | False |
| test | 55-59 | 5543 | 409 | 0.4156 | 0.9256 | 0.3080 | False |
| test | 60-64 | 6671 | 646 | 0.4334 | 0.8996 | 0.3164 | False |
| test | 65-69 | 6888 | 779 | 0.5225 | 0.8604 | 0.3230 | False |
| test | 70-74 | 6555 | 913 | 0.5728 | 0.7939 | 0.3102 | False |
| test | 75-79 | 4503 | 775 | 0.6116 | 0.7358 | 0.3249 | False |
| test | 80 or older | 5310 | 1068 | 0.6704 | 0.6322 | 0.3146 | False |
| test | Missing age | 1145 | 83 | 0.3855 | 0.9595 | 0.4267 | False |
