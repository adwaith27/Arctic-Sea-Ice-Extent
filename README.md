# Arctic Sea Ice Extent and Greenhouse Gas Modelling

This repository contains an Economic and Climate Modelling project that studies how Northern Hemisphere sea ice extent has changed alongside atmospheric greenhouse gas concentrations. The analysis combines monthly sea ice data with carbon dioxide (CO2) and methane (CH4) concentration data, creates a consistent modelling dataset, visualises the main climate patterns, and builds a SARIMAX time-series forecast for sea ice extent.

The project is designed to be reproducible: the notebook is kept readable, while the main analysis pipeline lives in a Python script that regenerates the cleaned datasets, figures, validation metrics, and forecast output.

## Research Aim

The main question is:

> How has Northern Hemisphere sea ice extent changed over time, and how can CO2 and CH4 concentration trends help explain and forecast those changes?

The project focuses on:

- long-term changes in sea ice extent;
- the relationship between sea ice, CO2, and CH4;
- seasonal ice behaviour, especially the July-December melt season;
- short-term forecasting using SARIMAX with greenhouse gas variables as exogenous regressors.

## Why the Dataset Starts in July 1983

The source datasets do not all begin at the same date. The methane dataset starts in July 1983, while the sea ice and CO2 datasets have earlier observations. To merge the three datasets cleanly, the common modelling window begins at:

```text
1983-07-01
```

The main dataset keeps every monthly observation from July 1983 onward. A separate melt-season subset is also created for July-December analysis. This distinction matters because filtering only for months July-December across all years would remove January-June observations and distort a full monthly time-series model.

## Repository Structure

```text
.
├── artic_ice.ipynb
├── src/
│   └── arctic_sea_ice_analysis.py
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   └── figures/
├── README.md
├── pyproject.toml
└── uv.lock
```

Important files:

- `artic_ice.ipynb`: notebook entry point for readable execution and displaying generated JPEG figures.
- `src/arctic_sea_ice_analysis.py`: main reproducible analysis pipeline.
- `data/raw/`: original or prepared source datasets used by the project.
- `data/raw/Sea_Ice_Index_Monthly_Data_with_Statistics_G02135_v3.0.xlsx`: NSIDC sea ice workbook.
- `data/raw/CO2_CH4_conc_1983.xlsx`: prepared CO2 and CH4 workbook used by the analysis.
- `data/processed/Transformed Data.xlsx`: full monthly merged dataset from July 1983 onward.
- `data/processed/Transformed Data - Melt Season.xlsx`: July-December subset for melt-season interpretation.
- `data/processed/SeaIce_CO2_CH4_Merged.xlsx`: merged sea ice, CO2, and CH4 dataset.
- `outputs/figures/`: static JPEG charts for reports and presentations.
- `ECO Project first draft.pptx`: project presentation draft.

## Data Sources

The project uses three climate datasets:

- NSIDC Sea Ice Index monthly Northern Hemisphere sea ice data.
- NOAA Global Monitoring Laboratory monthly CO2 data.
- NOAA Global Monitoring Laboratory monthly CH4 data.

The raw and prepared input files are kept in `data/raw/` so the analysis can be rerun without manually downloading data again. Generated Excel outputs are kept in `data/processed/`; root-level duplicate Excel files have been removed to avoid confusion.

## Methods

The pipeline performs the following steps:

1. Loads monthly sea ice data from the NSIDC workbook.
2. Loads CO2 and CH4 concentration data from the greenhouse gas workbook.
3. Aligns all datasets by `year` and `month`.
4. Keeps the common monthly period from July 1983 onward.
5. Creates a separate July-December melt-season subset.
6. Exports cleaned Excel datasets.
7. Generates static JPEG figures for presentation and interpretation.
8. Builds a SARIMAX model using CO2 and CH4 as exogenous variables.
9. Validates the model on the final 24 months of available data.
10. Produces a 12-month sea ice extent forecast.

## Generated Figures

The analysis produces the following JPEG figures in `outputs/figures/`:

- `extent_time_series.jpg`
- `avg_CO2_ppm_time_series.jpg`
- `avg_CH4_ppb_time_series.jpg`
- `correlation_matrix.jpg`
- `monthly_extent_distribution.jpg`
- `melt_season_extent.jpg`
- `seasonal_decomposition.jpg`
- `sarimax_12_month_forecast.jpg`

JPEG outputs are used instead of HTML charts so the results are easier to view directly in GitHub, reports, and PowerPoint slides.

## Model Validation

The SARIMAX model is validated using the final 24 months as a holdout period. In the latest run, the validation metrics were:

```text
MAE:  0.227
RMSE: 0.258
MAPE: 2.57%
```

These values are measured against sea ice extent in million square kilometres. They indicate that the short-term forecast performs reasonably well for this coursework-level modelling setup, though the results should be interpreted as an exploratory forecast rather than a full physical climate model.

## How to Reproduce

This project uses `uv` for Python dependency management.

Install dependencies:

```bash
uv sync
```

If dependencies need to be added from scratch, use:

```bash
uv add pandas numpy openpyxl matplotlib seaborn statsmodels scipy scikit-learn jupyterlab ipykernel python-pptx
```

Run the full analysis pipeline:

```bash
uv run python src/arctic_sea_ice_analysis.py
```

Or open the notebook:

```bash
uv run jupyter lab
```

Then run `artic_ice.ipynb`.

## Outputs

Running the pipeline regenerates:

- `data/processed/SeaIce_CO2_CH4_Merged.xlsx`
- `data/processed/Transformed Data.xlsx`
- `data/processed/Transformed Data - Melt Season.xlsx`
- JPEG figures in `outputs/figures/`
- model validation metrics in `data/processed/model_validation_metrics.csv`
- 12-month forecast output in `data/processed/sea_ice_extent_12_month_forecast.xlsx`

All Excel files are stored under `data/` rather than the repository root. This keeps raw inputs, processed modelling datasets, and presentation outputs separated.

## Notes and Limitations

- CO2 and CH4 are used as explanatory time-series variables, but correlation does not prove direct causality.
- SARIMAX is useful for short-term statistical forecasting, but it is not a substitute for a physical climate model.
- The future exogenous greenhouse gas values are projected using recent average monthly changes, so the forecast represents a simple continuation scenario.
- The melt-season subset is intended for interpretation of July-December patterns, while the full monthly dataset is used for modelling.
