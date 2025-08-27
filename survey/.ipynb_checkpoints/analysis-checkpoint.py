# ============================================================
# analysis.py
# ------------------------------------------------------------
# Purpose: Compare Chatbot A vs B scores with paired tests
# Inputs : data/processed_scores.csv
# Outputs: results/figures/*.png, results/stats/*.csv
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "processed_scores.csv"

print("Loading processed scores...")
df = pd.read_csv(DATA_FILE)

# -----------------------------
# 1. Pivot A vs B
# -----------------------------
pivoted = df.pivot(index=["Email Address","prompt_id"], columns="condition", values=["PI","CSAT","HL","CMP"])
pivoted.columns = ["_".join(col).strip() for col in pivoted.columns.values]
pivoted = pivoted.reset_index()

# -----------------------------
# 2. Compute Δ scores
# -----------------------------
for metric in ["PI","CSAT","HL","CMP"]:
    pivoted[f"Delta_{metric}"] = pivoted[f"{metric}_B"] - pivoted[f"{metric}_A"]

# -----------------------------
# 3. Paired t-tests
# -----------------------------
stats_out = []
for metric in ["PI","CSAT","HL","CMP"]:
    diffs = pivoted[f"Delta_{metric}"].dropna()
    t, p = stats.ttest_rel(pivoted[f"{metric}_B"], pivoted[f"{metric}_A"], nan_policy="omit")
    stats_out.append({"metric":metric, "mean_delta":diffs.mean(), "t":t, "p":p})

stats_df = pd.DataFrame(stats_out)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
stats_df.to_csv(RESULTS_DIR / "stats_results.csv", index=False)
print(stats_df)

# -----------------------------
# 4. Bar plot with 95% CI
# -----------------------------
for metric in ["PI","CSAT","HL","CMP"]:
    diffs = pivoted[f"Delta_{metric}"].dropna()
    mean = diffs.mean()
    ci = stats.t.interval(0.95, len(diffs)-1, loc=mean, scale=stats.sem(diffs))
    
    plt.figure(figsize=(4,6))
    plt.bar([metric], [mean], yerr=[[mean-ci[0]], [ci[1]-mean]], capsize=10)
    plt.axhline(0, color="black", linestyle="--")
    plt.ylabel("Delta (B − A)")
    plt.title(f"{metric} Difference (Chatbot B − A)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{metric}_delta.png")
    plt.close()

print(f"Saved figures and stats → {RESULTS_DIR}")
