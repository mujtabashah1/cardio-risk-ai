# Official CDC definitions

- [2021 annual data and documentation](https://www.cdc.gov/brfss/annual_data/annual_2021.html)
- [2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf): target p.136; BMI p.149; candidate coding throughout. Page numbers refer to printed codebook pages.
- [2021 calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf): explicit target derivation and BMI construction/export scaling.
- [2021 dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html): _MICHD sources CVDINFR4 and CVDCRHD4.

Downloaded October 3, 2026. The calculated-variable narrative contains an `AKCDAY5` typo in DRNKANY5 description; its SAS code and codebook consistently refer to ALCDAY5. No substitution was made. BMI has human-scale values in the construction code but is multiplied by 100 for export; the codebook confirms two implied decimal places.
