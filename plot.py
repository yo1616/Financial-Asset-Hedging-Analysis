import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 你計算出的危機相關係數
data = {
    "Gold":   {"2008": -0.0469, "2020": 0.1863, "2022": 0.1213},
    "CHF":    {"2008": -0.0014, "2020": -0.0017, "2022": -0.0665},
    "US10Y":  {"2008": -0.4480, "2020": -0.5137, "2022": 0.1996},
    "BTC":    {"2008": float('nan'), "2020": 0.4460, "2022": 0.5562}
}

df = pd.DataFrame(data)
df.index.name = "Crisis Period"

plt.figure(figsize=(8, 5))
sns.heatmap(df, annot=True, cmap="RdBu_r", center=0, fmt=".3f")

plt.title("Correlation with S&P500 During Crisis Periods")
plt.ylabel("Crisis Period")
plt.tight_layout()
plt.show()