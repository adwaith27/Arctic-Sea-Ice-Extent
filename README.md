# Arctic Sea Ice Extent and Greenhouse Gas Modelling

This project analyses Northern Hemisphere sea ice extent together with CO2 and CH4 concentration data for an Economic and Climate Modelling subject project.

## Project Logic

The combined modelling dataset starts at July 1983 because the CH4 series begins in July 1983. The main dataset should keep every month from July 1983 onward, not only July-December for every year.

Two outputs are produced:

- Full monthly dataset from July 1983 onward for time-series modelling.
- Melt-season subset, July-December, for focused seasonal analysis.

## Data Sources

- NSIDC Sea Ice Index monthly Northern Hemisphere data.
- NOAA Global Monitoring Laboratory CO2 monthly data.
- NOAA Global Monitoring Laboratory CH4 monthly data.

## Reproduce

Install dependencies:

```bash
uv add pandas numpy openpyxl matplotlib seaborn statsmodels scipy scikit-learn jupyterlab ipykernel python-pptx
uv sync
```

Run the analysis:

```bash
uv run python src/arctic_sea_ice_analysis.py
```

Generated files are written to:

- `data/processed/`
- `outputs/figures/`

## Key Methods

- Monthly data alignment by `year` and `month`.
- Correlation analysis across sea ice and greenhouse gas variables.
- Seasonal distribution and melt-season comparison.
- SARIMAX forecasting using CO2 and CH4 as exogenous regressors.
- Train/test validation using the final 24 months as a holdout set.
