import pandas as pd, numpy as np
import matplotlib.pyplot as plt

RISK_FREE = 0.065          # assumed risk-free rate (approx. 91-day T-bill yield)
BENCH = "Nifty50 Index (UTI)"

navs = pd.read_csv("../data/navs.csv", index_col="date", parse_dates=True)
daily = navs.pct_change().dropna()
years = (navs.index[-1] - navs.index[0]).days / 365.25

# ---- 1. Four numbers per fund ----
cagr = (navs.iloc[-1] / navs.iloc[0]) ** (1 / years) - 1
vol = daily.std() * np.sqrt(252)
sharpe = (cagr - RISK_FREE) / vol
max_dd = (navs / navs.cummax() - 1).min()

# ---- 2. Beat rate: % of 3-year windows where the fund beat the index ----
roll3 = (navs / navs.shift(252 * 3)) ** (1 / 3) - 1          # rolling 3-yr CAGR
roll3 = roll3.dropna()
beat_rate = (roll3.gt(roll3[BENCH], axis=0)).mean()
beat_rate[BENCH] = np.nan

summary = pd.DataFrame({
    "CAGR": cagr, "Volatility": vol, "Sharpe": sharpe,
    "Max Drawdown": max_dd, "Beat rate (3y windows)": beat_rate,
}).sort_values("CAGR", ascending=False)
summary["Beat index overall?"] = np.where(summary["CAGR"] > cagr[BENCH], "Yes", "No")
summary.loc[BENCH, "Beat index overall?"] = "Benchmark"

print(f"Period: {navs.index[0].date()} to {navs.index[-1].date()} ({years:.1f} years)\n")
print(summary.round(3).to_string())
summary.to_excel("../output/summary.xlsx")

# ---- 3. Charts ----
growth = navs / navs.iloc[0] * 10000
ax = growth.drop(columns=BENCH).plot(figsize=(10, 6), linewidth=1, alpha=0.7)
growth[BENCH].plot(ax=ax, color="black", linewidth=2.5, label=BENCH)
ax.set_title("Growth of Rs 10,000 invested in Oct 2020")
ax.set_ylabel("Value (Rs)"); ax.set_xlabel(""); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("../output/1_growth.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 6))
for name, row in summary.iterrows():
    color = "black" if name == BENCH else "tab:blue"
    ax.scatter(row["Volatility"] * 100, row["CAGR"] * 100, color=color, s=60)
    left = name == "ICICI Pru Large Cap"          # label on the left to avoid overlap
    ax.annotate(name, (row["Volatility"] * 100, row["CAGR"] * 100), fontsize=8,
                xytext=(-5 if left else 5, 3), textcoords="offset points",
                ha="right" if left else "left")
ax.set_xlim(10, 18); ax.set_ylim(10, 21)    # same width on both axes, so risk gaps are not exaggerated
ax.set_xlabel("Volatility (% per year)"); ax.set_ylabel("CAGR (%)")
ax.set_title("Risk vs return: similar risk, different returns")
plt.tight_layout(); plt.savefig("../output/2_risk_return.png", dpi=150); plt.close()

br = summary["Beat rate (3y windows)"].dropna().sort_values() * 100
ax = br.plot.barh(figsize=(9, 5), color=["tab:green" if v > 50 else "tab:red" for v in br])
ax.axvline(50, color="grey", linestyle="--")
ax.set_xlabel("% of 3-year windows where the fund beat the Nifty 50 index fund")
ax.set_title("How often did each fund beat the index?")
plt.tight_layout(); plt.savefig("../output/3_beat_rate.png", dpi=150); plt.close()

print("\nSaved: output/summary.xlsx and 3 charts")
