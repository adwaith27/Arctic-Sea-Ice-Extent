import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX


ROOT = Path(__file__).resolve().parents[1]
SEA_ICE_FILE = ROOT / "Sea_Ice_Index_Monthly_Data_with_Statistics_G02135_v3.0.xlsx"
GHG_FILE = ROOT / "CO2_CH4_conc(1983).xlsx"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURE_DIR = ROOT / "outputs" / "figures"

START_DATE = "1983-07-01"
FORECAST_STEPS = 12
TEST_STEPS = 24

SEA_ICE_COLUMNS = [
    "year",
    "month",
    "extent",
    "area",
    "extent-anomaly",
    "trend-through-year-km^2-per-year",
]

ANALYSIS_COLUMNS = [
    "extent",
    "area",
    "extent-anomaly",
    "trend-through-year-km^2-per-year",
    "avg_CO2_ppm",
    "avg_CH4_ppb",
]


def ensure_output_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def add_date_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(
        {
            "year": df["year"].astype(int),
            "month": df["month"].astype(int),
            "day": 1,
        }
    )
    return df


def load_sea_ice() -> pd.DataFrame:
    xls = pd.ExcelFile(SEA_ICE_FILE)
    frames = []

    for sheet in xls.sheet_names:
        if sheet == "Documentation":
            continue
        frame = pd.read_excel(
            SEA_ICE_FILE,
            sheet_name=sheet,
            header=9,
            usecols=SEA_ICE_COLUMNS,
        )
        frames.append(frame)

    sea_ice = pd.concat(frames, ignore_index=True)
    sea_ice = sea_ice.dropna(subset=["year", "month", "extent"])
    sea_ice = add_date_column(sea_ice)
    return sea_ice.sort_values("date")


def load_greenhouse_gases() -> pd.DataFrame:
    co2 = pd.read_excel(GHG_FILE, sheet_name="CO2")
    ch4 = pd.read_excel(GHG_FILE, sheet_name="CH4")

    co2 = co2.rename(
        columns={"Year": "year", "Month": "month", "average NH": "avg_CO2_ppm"}
    )
    ch4 = ch4.rename(
        columns={"Year": "year", "Month": "month", "average NH": "avg_CH4_ppb"}
    )

    ghg = pd.merge(
        co2[["year", "month", "avg_CO2_ppm"]],
        ch4[["year", "month", "avg_CH4_ppb"]],
        on=["year", "month"],
        how="inner",
    )
    return add_date_column(ghg)


def build_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    sea_ice = load_sea_ice()
    ghg = load_greenhouse_gases()

    sea_ice = sea_ice.loc[sea_ice["date"] >= START_DATE].copy()
    merged = pd.merge(
        sea_ice,
        ghg.drop(columns=["date"]),
        on=["year", "month"],
        how="inner",
    )
    merged = add_date_column(merged).sort_values("date").set_index("date")

    monthly = merged.asfreq("MS")
    monthly[ANALYSIS_COLUMNS] = monthly[ANALYSIS_COLUMNS].interpolate(method="time")
    monthly = monthly.dropna(subset=["extent", "avg_CO2_ppm", "avg_CH4_ppb"])

    melt_season = monthly.loc[monthly.index.month >= 7].copy()
    return monthly, melt_season


def save_datasets(monthly: pd.DataFrame, melt_season: pd.DataFrame) -> None:
    monthly.to_excel(PROCESSED_DIR / "sea_ice_ghg_monthly_from_1983_07.xlsx")
    melt_season.to_excel(PROCESSED_DIR / "sea_ice_ghg_melt_season_jul_dec.xlsx")

    monthly.reset_index().to_excel(ROOT / "SeaIce_CO2_CH4_Merged.xlsx", index=False)
    monthly.to_excel(ROOT / "Transformed Data.xlsx")
    melt_season.to_excel(ROOT / "Transformed Data - Melt Season.xlsx")


def save_figure(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIGURE_DIR / f"{name}.jpg", dpi=220, bbox_inches="tight")
    plt.close(fig)


def format_time_axis(ax: plt.Axes) -> None:
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.25)


def create_exploratory_figures(monthly: pd.DataFrame, melt_season: pd.DataFrame) -> None:
    labels = {
        "extent": "Sea Ice Extent (million sq km)",
        "avg_CO2_ppm": "CO2 Concentration (ppm)",
        "avg_CH4_ppb": "CH4 Concentration (ppb)",
    }

    for column, color in [
        ("extent", "#2563eb"),
        ("avg_CO2_ppm", "#15803d"),
        ("avg_CH4_ppb", "#c2410c"),
    ]:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(monthly.index, monthly[column], color=color, linewidth=2)
        ax.set_title(f"{labels[column]} Over Time", fontsize=15, pad=12)
        ax.set_xlabel("Date")
        ax.set_ylabel(labels[column])
        format_time_axis(ax)
        fig.autofmt_xdate()
        save_figure(fig, f"{column}_time_series")

    corr = monthly[ANALYSIS_COLUMNS].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        ax=ax,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Correlation"},
    )
    ax.set_title("Correlation Matrix", fontsize=15, pad=12)
    save_figure(fig, "correlation_matrix")

    monthly_distribution = monthly.assign(month=monthly.index.month)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=monthly_distribution, x="month", y="extent", ax=ax, color="#93c5fd")
    ax.set_title("Monthly Distribution of Sea Ice Extent", fontsize=15, pad=12)
    ax.set_xlabel("Month")
    ax.set_ylabel("Sea Ice Extent (million sq km)")
    ax.grid(True, axis="y", alpha=0.25)
    save_figure(fig, "monthly_extent_distribution")

    fig, ax = plt.subplots(figsize=(12, 6))
    for month, frame in melt_season.groupby(melt_season.index.month):
        ax.plot(frame.index.year, frame["extent"], marker="o", linewidth=1.6, label=str(month))
    ax.set_title("Melt-Season Sea Ice Extent (July-December)", fontsize=15, pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Sea Ice Extent (million sq km)")
    ax.grid(True, alpha=0.25)
    ax.legend(title="Month", ncols=3)
    save_figure(fig, "melt_season_extent")

    extent = monthly["extent"].asfreq("MS").interpolate(method="time")
    decomposition = seasonal_decompose(extent, model="additive", period=12)
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    fig.suptitle("Seasonal Decomposition of Sea Ice Extent", fontsize=16)
    for ax, component in zip(axes, ["observed", "trend", "seasonal", "resid"]):
        series = getattr(decomposition, component)
        ax.plot(series.index, series.values, linewidth=1.6)
        ax.set_ylabel(component.title())
        format_time_axis(ax)
    axes[-1].set_xlabel("Date")
    fig.autofmt_xdate()
    save_figure(fig, "seasonal_decomposition")


def fit_sarimax(endog: pd.Series, exog: pd.DataFrame):
    model = SARIMAX(
        endog,
        exog=exog,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False,
        concentrate_scale=True,
    )
    return model.fit(disp=False, maxiter=100)


def run_forecast(monthly: pd.DataFrame) -> pd.DataFrame:
    model_df = monthly[["extent", "avg_CO2_ppm", "avg_CH4_ppb"]].dropna()

    train = model_df.iloc[:-TEST_STEPS]
    test = model_df.iloc[-TEST_STEPS:]

    validation_result = fit_sarimax(
        train["extent"], train[["avg_CO2_ppm", "avg_CH4_ppb"]]
    )
    validation_forecast = validation_result.get_forecast(
        steps=len(test), exog=test[["avg_CO2_ppm", "avg_CH4_ppb"]]
    ).summary_frame()

    mae = mean_absolute_error(test["extent"], validation_forecast["mean"])
    rmse = np.sqrt(mean_squared_error(test["extent"], validation_forecast["mean"]))
    mape = (
        np.abs((test["extent"] - validation_forecast["mean"]) / test["extent"]).mean()
        * 100
    )

    metrics = pd.DataFrame(
        [{"test_months": len(test), "mae": mae, "rmse": rmse, "mape_percent": mape}]
    )
    metrics.to_csv(PROCESSED_DIR / "model_validation_metrics.csv", index=False)

    full_result = fit_sarimax(
        model_df["extent"], model_df[["avg_CO2_ppm", "avg_CH4_ppb"]]
    )
    future_index = pd.date_range(
        model_df.index[-1] + pd.offsets.MonthBegin(1),
        periods=FORECAST_STEPS,
        freq="MS",
    )

    recent_ghg_change = model_df[["avg_CO2_ppm", "avg_CH4_ppb"]].diff(12).tail(12).mean() / 12
    last_ghg = model_df[["avg_CO2_ppm", "avg_CH4_ppb"]].iloc[-1]
    future_exog = pd.DataFrame(
        [last_ghg + recent_ghg_change * step for step in range(1, FORECAST_STEPS + 1)],
        index=future_index,
    )

    forecast = full_result.get_forecast(steps=FORECAST_STEPS, exog=future_exog)
    forecast_frame = forecast.summary_frame()
    forecast_frame.index = future_index
    forecast_frame.to_excel(PROCESSED_DIR / "sea_ice_extent_12_month_forecast.xlsx")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(model_df.index, model_df["extent"], label="Observed", linewidth=1.8)
    ax.plot(
        forecast_frame.index,
        forecast_frame["mean"],
        label="Forecast",
        color="#c2410c",
        linewidth=2.2,
    )
    ax.fill_between(
        forecast_frame.index,
        forecast_frame["mean_ci_lower"].to_numpy(),
        forecast_frame["mean_ci_upper"].to_numpy(),
        color="#94a3b8",
        alpha=0.25,
        label="95% confidence interval",
    )
    ax.set_title("12-Month Forecast of Northern Hemisphere Sea Ice Extent", fontsize=15, pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Extent (million sq km)")
    ax.legend()
    format_time_axis(ax)
    fig.autofmt_xdate()
    save_figure(fig, "sarimax_12_month_forecast")

    return metrics


def main() -> None:
    ensure_output_dirs()
    monthly, melt_season = build_datasets()
    save_datasets(monthly, melt_season)
    create_exploratory_figures(monthly, melt_season)
    metrics = run_forecast(monthly)

    print("Monthly dataset:", monthly.index.min().date(), "to", monthly.index.max().date())
    print("Rows:", len(monthly))
    print("Melt-season rows:", len(melt_season))
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
