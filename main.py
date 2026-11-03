"""Statistics final project analysis pipeline.

This script uses local Yahoo Finance CSV files to build the tables and figures
needed for a written report on hedge assets and the S&P 500.
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

DATA_MAP = {
    "SP500": ("sp500_30y.csv", "USD_Price"),
    "Gold": ("gold_gc_f_30y.csv", "USD_Price"),
    "CHF": ("chf_usd_30y.csv", "USD_Price"),
    "US10Y": ("us10y_price_30y.csv", "USD_Price"),
    "BTC": ("btc_usd_30y.csv", "USD_Price"),
}

ASSETS = ["Gold", "CHF", "US10Y", "BTC"]
COVID_START = "2020-02-01"
COVID_END = "2020-12-31"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)


def load_price_data() -> pd.DataFrame:
    """Load all local CSV files and merge them into one price DataFrame."""
    frames = []

    for asset, (filename, value_column) in DATA_MAP.items():
        path = BASE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing data file: {path}")

        frame = pd.read_csv(path, parse_dates=["Date"])
        if value_column not in frame.columns:
            raise KeyError(f"{filename} is missing column {value_column}")

        cleaned = (
            frame[["Date", value_column]]
            .rename(columns={value_column: asset})
            .dropna()
            .sort_values("Date")
        )
        frames.append(cleaned)

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="Date", how="outer")

    merged = merged.sort_values("Date").set_index("Date")
    return merged


def build_return_data(price_data: pd.DataFrame) -> pd.DataFrame:
    """Convert prices to daily returns and add the COVID dummy."""
    return_series = []
    for column in price_data.columns:
        series = price_data[column].dropna().pct_change()
        return_series.append(series.rename(f"R_{column}"))

    returns = pd.concat(return_series, axis=1, join="outer")
    returns["COVID_Dummy"] = (
        (returns.index >= pd.Timestamp(COVID_START))
        & (returns.index <= pd.Timestamp(COVID_END))
    ).astype(int)
    returns = returns.dropna(subset=["R_SP500"])
    return returns


def create_sample_summary(price_data: pd.DataFrame, return_data: pd.DataFrame) -> pd.DataFrame:
    """Summarize each asset's available sample window and observations."""
    rows = []
    for asset in DATA_MAP:
        price_series = price_data[asset].dropna()
        return_series = return_data[f"R_{asset}"].dropna()
        rows.append(
            {
                "Asset": asset,
                "Price Start": price_series.index.min().date().isoformat(),
                "Price End": price_series.index.max().date().isoformat(),
                "Price Obs": int(price_series.shape[0]),
                "Return Start": return_series.index.min().date().isoformat(),
                "Return End": return_series.index.max().date().isoformat(),
                "Return Obs": int(return_series.shape[0]),
            }
        )
    return pd.DataFrame(rows)


def create_descriptive_stats(return_data: pd.DataFrame) -> pd.DataFrame:
    """Generate descriptive statistics for all return series."""
    columns = [f"R_{asset}" for asset in DATA_MAP]
    stats = return_data[columns].agg(["mean", "std", "min", "median", "max"]).T
    stats["count"] = return_data[columns].count()
    stats = stats.rename(
        columns={
            "mean": "Mean",
            "std": "Std",
            "min": "Min",
            "median": "Median",
            "max": "Max",
            "count": "Count",
        }
    )
    stats.index.name = "Series"
    return stats.reset_index()


def create_correlation_table(return_data: pd.DataFrame) -> pd.DataFrame:
    """Compute full-period and COVID-period correlations with the S&P 500."""
    rows = []
    covid_mask = return_data["COVID_Dummy"] == 1

    for asset in ASSETS:
        asset_col = f"R_{asset}"
        full_sample = return_data[["R_SP500", asset_col]].dropna()
        covid_sample = return_data.loc[covid_mask, ["R_SP500", asset_col]].dropna()
        non_covid_sample = return_data.loc[~covid_mask, ["R_SP500", asset_col]].dropna()

        rows.append(
            {
                "Asset": asset,
                "Full Period Corr": full_sample["R_SP500"].corr(full_sample[asset_col]),
                "COVID Period Corr": covid_sample["R_SP500"].corr(covid_sample[asset_col]),
                "Non-COVID Corr": non_covid_sample["R_SP500"].corr(non_covid_sample[asset_col]),
                "Full Sample Obs": int(full_sample.shape[0]),
                "COVID Sample Obs": int(covid_sample.shape[0]),
            }
        )

    return pd.DataFrame(rows)


def run_simple_regression(return_data: pd.DataFrame, asset: str) -> dict:
    """Run a simple regression for one asset."""
    asset_col = f"R_{asset}"
    sample = return_data[["R_SP500", asset_col]].dropna()
    y = sample[asset_col]
    x = sm.add_constant(sample["R_SP500"])
    model = sm.OLS(y, x).fit()

    return {
        "Asset": asset,
        "Observations": int(sample.shape[0]),
        "Intercept": model.params["const"],
        "Beta_SP500": model.params["R_SP500"],
        "Intercept t": model.tvalues["const"],
        "Beta_SP500 t": model.tvalues["R_SP500"],
        "Intercept p": model.pvalues["const"],
        "Beta_SP500 p": model.pvalues["R_SP500"],
        "R_squared": model.rsquared,
        "Adj_R_squared": model.rsquared_adj,
    }


def run_covid_regression(return_data: pd.DataFrame, asset: str) -> dict:
    """Run a multiple regression with a COVID dummy and interaction term."""
    asset_col = f"R_{asset}"
    sample = return_data[["R_SP500", "COVID_Dummy", asset_col]].dropna().copy()
    sample["SP500_x_COVID"] = sample["R_SP500"] * sample["COVID_Dummy"]

    y = sample[asset_col]
    x = sm.add_constant(sample[["R_SP500", "COVID_Dummy", "SP500_x_COVID"]])
    model = sm.OLS(y, x).fit()

    return {
        "Asset": asset,
        "Observations": int(sample.shape[0]),
        "Intercept": model.params["const"],
        "Beta_SP500": model.params["R_SP500"],
        "Beta_COVID_Dummy": model.params["COVID_Dummy"],
        "Beta_Interaction": model.params["SP500_x_COVID"],
        "Intercept p": model.pvalues["const"],
        "Beta_SP500 p": model.pvalues["R_SP500"],
        "Beta_COVID_Dummy p": model.pvalues["COVID_Dummy"],
        "Beta_Interaction p": model.pvalues["SP500_x_COVID"],
        "R_squared": model.rsquared,
        "Adj_R_squared": model.rsquared_adj,
        "F_statistic": model.fvalue,
        "F_pvalue": model.f_pvalue,
    }


def create_regression_tables(return_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create result tables for simple and COVID regressions."""
    simple_results = pd.DataFrame([run_simple_regression(return_data, asset) for asset in ASSETS])
    covid_results = pd.DataFrame([run_covid_regression(return_data, asset) for asset in ASSETS])
    return simple_results, covid_results


def plot_indexed_prices(price_data: pd.DataFrame) -> None:
    """Plot indexed price levels on the common sample used by all assets."""
    common_sample = price_data[list(DATA_MAP)].dropna()
    indexed = common_sample / common_sample.iloc[0] * 100

    plt.figure(figsize=(12, 6))
    for column in indexed.columns:
        plt.plot(indexed.index, indexed[column], label=column)

    plt.yscale("log")
    plt.title("Indexed Prices of S&P 500 and Hedge Assets")
    plt.ylabel("Index (first common day = 100)")
    plt.xlabel("Date")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "indexed_prices_all_assets.png", dpi=300)
    plt.close()


def plot_correlation_bar(correlation_table: pd.DataFrame) -> None:
    """Plot full-period and COVID-period correlations side by side."""
    melted = correlation_table.melt(
        id_vars="Asset",
        value_vars=["Full Period Corr", "COVID Period Corr", "Non-COVID Corr"],
        var_name="Period",
        value_name="Correlation",
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(data=melted, x="Asset", y="Correlation", hue="Period")
    plt.axhline(0, color="black", linewidth=1)
    plt.title("Correlation with S&P 500 by Period")
    plt.ylabel("Correlation")
    plt.xlabel("Asset")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "correlation_bar_chart.png", dpi=300)
    plt.close()


def plot_scatter_with_regression(return_data: pd.DataFrame) -> None:
    """Create one scatter plot per asset with a fitted regression line."""
    for asset in ASSETS:
        asset_col = f"R_{asset}"
        sample = return_data[["R_SP500", asset_col, "COVID_Dummy"]].dropna()

        plt.figure(figsize=(8, 6))
        sns.regplot(
            data=sample,
            x="R_SP500",
            y=asset_col,
            scatter_kws={"alpha": 0.35, "s": 18},
            line_kws={"color": "red"},
        )
        plt.title(f"{asset} Return vs S&P 500 Return")
        plt.xlabel("S&P 500 daily return")
        plt.ylabel(f"{asset} daily return")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"scatter_regression_{asset.lower()}.png", dpi=300)
        plt.close()


def plot_scatter_with_regression_combined(return_data: pd.DataFrame) -> None:
    """Create a 2x2 panel of all asset scatter plots with fitted regression lines."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, asset in zip(axes, ASSETS):
        asset_col = f"R_{asset}"
        sample = return_data[["R_SP500", asset_col]].dropna()

        sns.regplot(
            data=sample,
            x="R_SP500",
            y=asset_col,
            ax=ax,
            scatter_kws={"alpha": 0.35, "s": 18},
            line_kws={"color": "red"},
        )
        ax.set_title(asset)
        ax.set_xlabel("S&P 500 daily return")
        ax.set_ylabel(f"{asset} daily return")
        ax.grid(True, alpha=0.3)

    fig.suptitle("Scatter Plots and Regression Lines for Four Assets", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUTPUT_DIR / "scatter_regression_combined.png", dpi=300)
    plt.close(fig)


def plot_covid_slope_comparison(return_data: pd.DataFrame) -> None:
    """Compare non-COVID and COVID observations in scatter plots."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    palette = {0: "#4c72b0", 1: "#dd8452"}
    labels = {0: "Non-COVID", 1: "COVID"}

    for ax, asset in zip(axes, ASSETS):
        asset_col = f"R_{asset}"
        sample = return_data[["R_SP500", asset_col, "COVID_Dummy"]].dropna()

        for dummy_value in [0, 1]:
            subset = sample[sample["COVID_Dummy"] == dummy_value]
            if subset.empty:
                continue
            sns.regplot(
                data=subset,
                x="R_SP500",
                y=asset_col,
                ax=ax,
                ci=None,
                scatter_kws={"alpha": 0.25, "s": 14},
                line_kws={"linewidth": 2},
                color=palette[dummy_value],
                label=labels[dummy_value],
            )

        ax.set_title(asset)
        ax.set_xlabel("S&P 500 daily return")
        ax.set_ylabel(f"{asset} daily return")
        ax.legend()
        ax.grid(True, alpha=0.3)

    fig.suptitle("Return Relationship Before and During COVID", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUTPUT_DIR / "covid_slope_comparison.png", dpi=300)
    plt.close(fig)


def save_tables(
    sample_summary: pd.DataFrame,
    descriptive_stats: pd.DataFrame,
    correlation_table: pd.DataFrame,
    simple_results: pd.DataFrame,
    covid_results: pd.DataFrame,
    return_data: pd.DataFrame,
) -> None:
    """Write all report tables to disk."""
    sample_summary.to_csv(OUTPUT_DIR / "sample_summary.csv", index=False)
    descriptive_stats.to_csv(OUTPUT_DIR / "descriptive_stats.csv", index=False)
    correlation_table.to_csv(OUTPUT_DIR / "correlation_table.csv", index=False)
    simple_results.to_csv(OUTPUT_DIR / "simple_regression_results.csv", index=False)
    covid_results.to_csv(OUTPUT_DIR / "covid_regression_results.csv", index=False)
    return_data.to_csv(OUTPUT_DIR / "merged_returns_with_dummy.csv")


def print_report_guidance() -> None:
    """Show the user which tables and charts map to the report sections."""
    print("\n=== 這份報告需要的資料與圖表 ===")
    print("1. sample_summary.csv：各資產資料起訖日與樣本數")
    print("2. descriptive_stats.csv：各報酬率的平均數、標準差、中位數、最大最小值")
    print("3. correlation_table.csv：全期間、COVID 期間、非 COVID 期間與 S&P 500 的相關係數")
    print("4. simple_regression_results.csv：單一迴歸結果，對應研究問題一")
    print("5. covid_regression_results.csv：含 dummy 與交乘項的多元迴歸結果，對應研究問題二")
    print("6. indexed_prices_all_assets.png：五種資產價格趨勢總覽")
    print("7. correlation_bar_chart.png：各期間相關係數比較")
    print("8. scatter_regression_combined.png：四種資產單一迴歸散佈圖合併版")
    print("9. scatter_regression_*.png：各資產單一迴歸散佈圖")
    print("10. covid_slope_comparison.png：COVID 前後斜率差異比較圖")


def main() -> None:
    ensure_output_dir()
    price_data = load_price_data()
    return_data = build_return_data(price_data)

    sample_summary = create_sample_summary(price_data, return_data)
    descriptive_stats = create_descriptive_stats(return_data)
    correlation_table = create_correlation_table(return_data)
    simple_results, covid_results = create_regression_tables(return_data)

    save_tables(
        sample_summary,
        descriptive_stats,
        correlation_table,
        simple_results,
        covid_results,
        return_data,
    )

    plot_indexed_prices(price_data)
    plot_correlation_bar(correlation_table)
    plot_scatter_with_regression(return_data)
    plot_scatter_with_regression_combined(return_data)
    plot_covid_slope_comparison(return_data)
    print_report_guidance()


if __name__ == "__main__":
    main()
