# 金融資產避險能力實證分析

[English](./README.md) | [**繁體中文**](./README.zh-TW.md)

**Python · 金融資料分析 · 統計建模 · 實證研究**

本專案以 S&P 500 作為市場基準，研究黃金、美國公債 ETF、瑞士法郎與 Bitcoin 的報酬關係，並分析這些關係是否在 COVID-19 市場危機期間發生變化。

研究橫跨統計學上下學期，從初步的探索性資料分析，逐步發展為結合假設檢定與迴歸模型的金融實證研究。

## 我的實作內容

透過 Python 建立金融資料分析流程，包含：

- **金融資料取得與處理：** 使用 `yfinance` 蒐集歷史價格、整理不同資產的資料並計算日報酬率。
- **統計模型建構：** 實作相關係數分析、OLS 迴歸、假設檢定及 COVID 期間交互作用模型。
- **資料視覺化：** 產生資產價格比較、迴歸散佈圖與危機期間相關係數圖表。
- **實證結果解讀：** 分析不同資產與股票市場的關係，討論其分散風險與避險特性。

## 研究方法

以 S&P 500 日報酬率作為市場基準，分析黃金、美國 7–10 年期公債 ETF（IEF）、CHF/USD 及 Bitcoin。

**1. 單一線性迴歸**

\[
R_{asset,t}=\beta_0+\beta_1R_{SP500,t}+\epsilon_t
\]

**2. COVID 期間交互作用模型**

\[
R_{asset,t}=\beta_0+\beta_1R_{SP500,t}+\beta_2D_t+\beta_3(R_{SP500,t}\times D_t)+\epsilon_t
\]

透過交互作用項，檢驗 COVID 期間資產與股市的估計報酬關係是否發生統計上顯著的變化。
## Selected Visualizations

### Asset Correlations Across Market Conditions

![Correlation Comparison](./outputs/correlation_bar_chart.png)

### Return Relationships During COVID-19

![Crisis-Period Regression](./outputs/covid_slope_comparison.png)
## 主要研究發現

| 資產 | 實證結果 |
|---|---|
| **美國公債 ETF** | COVID 期間與 S&P 500 呈較強負相關（−0.5137）。 |
| **黃金** | COVID 期間的市場報酬關係出現顯著變化（交互作用項 p = 0.00007）。 |
| **Bitcoin** | 與股市呈正相關，在研究樣本中較缺乏穩定的防禦性特徵。 |
| **瑞士法郎** | 與股市的相關係數接近零，線性共同波動較弱。 |

**核心發現：** 資產間的歷史報酬關係可能隨市場環境變化，因此評估避險能力時，需要結合統計檢定與金融情境，而不能僅依賴單一相關係數。

## 技術與實作流程

**技術工具：** Python、pandas、yfinance、statsmodels、Matplotlib、Seaborn。

```text
金融市場資料蒐集
        ↓
資料清理與報酬率計算
        ↓
相關分析與迴歸建模
        ↓
危機期間比較
        ↓
資料視覺化與結果解讀
```

### 執行方式

```bash
pip install -r requirements.txt

python src/downloadSP.py
python src/downloadFin.py
python src/main.py
```

*資料下載及分析程式須使用一致的本機路徑。重新下載的資料版本與有效期間不同時，結果可能有所差異。*

## 研究限制

本專案為學術實證分析，研究結果反映歷史樣本中的線性關係，不能直接推論因果關係，也不代表已建立可實際運用的投資避險策略。

原始書面報告與目前程式在部分研究期間設定上存在差異。若要完整重現原始結果，仍需統一資料版本與樣本設定。

## 專案資訊

**蔡承佑 Patrick Tsai（TSAI CHENGYU）**  
統計學上下學期團隊研究專案

**個人貢獻：** Python 金融資料取得、統計分析程式實作、資料整理與視覺化。

研究結論為團隊共同成果，本作品集主要展示個人的程式實作及分析能力。

*本專案僅供學術研究與作品集展示，不構成投資建議。*
