# Financial Asset Hedging Analysis

[**English**](./README.md) | [繁體中文](./README.zh-TW.md)

**Python · Financial Data Analysis · Econometrics · Statistical Modeling**

An empirical analysis of how gold, U.S. Treasury ETFs, the Swiss franc, and Bitcoin behave relative to the S&P 500, with a focus on whether their relationships change during market crises.

This project was developed across two semesters of university statistics coursework, progressing from exploratory data analysis to hypothesis-driven statistical modeling.

## What I Built

Developed a Python-based financial analysis workflow covering:

- **Data Collection & Processing:** Retrieved historical market data using `yfinance`, aligned asset prices, and calculated daily returns.
- **Statistical Modeling:** Implemented correlation analysis, OLS regression, hypothesis testing, and COVID-period interaction models.
- **Data Visualization:** Generated asset comparisons, regression plots, and crisis-period correlation charts.
- **Financial Interpretation:** Evaluated how statistical relationships differ across assets and market conditions.

## Methodology

The analysis uses the S&P 500 as the market benchmark and examines four assets: gold, the U.S. 7–10 Year Treasury Bond ETF (IEF), CHF/USD, and Bitcoin.

Two regression specifications were implemented.

**1. Market Return Relationship**

\[
R_{asset,t}=\beta_0+\beta_1R_{SP500,t}+\epsilon_t
\]

**2. Crisis-Period Interaction Model**

\[
R_{asset,t}=\beta_0+\beta_1R_{SP500,t}+\beta_2D_t+\beta_3(R_{SP500,t}\times D_t)+\epsilon_t
\]

The interaction term tests whether an asset's estimated sensitivity to S&P 500 returns changed during the defined COVID-19 period.
## Selected Visualizations

### Asset Correlations Across Market Conditions

![Correlation Comparison](./outputs/correlation_bar_chart.png)

### Return Relationships During COVID-19

![Crisis-Period Regression](./outputs/covid_slope_comparison.png)
## Key Findings

| Asset | Empirical Finding |
|---|---|
| **U.S. Treasury ETF** | Showed the strongest negative correlation with the S&P 500 (−0.5137 during COVID). |
| **Gold** | Exhibited a statistically significant change in its market-return relationship during COVID (interaction p = 0.00007). |
| **Bitcoin** | Displayed positive equity-market correlation, suggesting limited defensive characteristics in the studied sample. |
| **Swiss Franc** | Maintained near-zero correlations with the S&P 500. |

**Main takeaway:** Historical diversification relationships are not necessarily stable across market conditions. Statistical significance and market context both matter when evaluating potential hedging assets.

## Technology & Implementation

**Tech Stack:** Python, pandas, yfinance, statsmodels, Matplotlib, Seaborn.

**Workflow**

```text
Market Data Collection
        ↓
Data Cleaning & Return Calculation
        ↓
Correlation & Regression Analysis
        ↓
Crisis-Period Comparison
        ↓
Visualization & Interpretation
```

### Getting Started

```bash
pip install -r requirements.txt

python src/downloadSP.py
python src/downloadFin.py
python src/main.py
```

*The download and analysis scripts require consistent local data paths. Historical results may vary with data versions and effective sample periods.*

## Limitations

This is an academic empirical analysis, not a validated investment strategy. The results reflect historical linear relationships and do not establish causality or guaranteed hedging performance.

The original reports and current code use partly different sample-window definitions. Reproducing the published results requires the corresponding historical data and analysis settings.

## Project Information

**Patrick Tsai (TSAI CHENGYU)**  
Academic Team Project — Statistics I & II

**My Contributions:** Python data collection, statistical analysis implementation, data processing, and visualization.

The research conclusions were developed collaboratively. This repository highlights my technical and analytical contributions.

*For academic and portfolio purposes only. Not investment advice.*
