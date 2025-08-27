import pandas as pd
import json
from pathlib import Path

# Config

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SURVEY_FILE = DATA_DIR / "Chatbot Rating - Anwers bot masked.csv"
BLOCKMAP_FILE = DATA_DIR / "surveyblock_map.csv"
TASKS_FILE = DATA_DIR / "tasks_data.json"
OUTPUT_FILE = DATA_DIR / "processed_scores.csv"

# 1. Load data
print("Loading survey data...")
survey_df = pd.read_csv(SURVEY_FILE)

print("Loading block map...")
blockmap = pd.read_csv(BLOCKMAP_FILE)

print("Loading tasks metadata...")
with open(TASKS_FILE, "r", encoding="utf-8") as f:
    tasks = json.load(f)
tasks_df = pd.DataFrame([{
    "prompt_id": t["data"].get("prompt_id"),
    "reply_id": t["id"],
    "bot_mask": t["data"].get("bot_mask")
} for t in tasks])

# 2. Melt survey data to long format
long_df = survey_df.melt(id_vars=["Email Address", "Timestamp"], 
                         var_name="column", value_name="score")

# Ensure numeric
long_df["score"] = pd.to_numeric(long_df["score"], errors="coerce")

# 3. Merge with block map
df = long_df.merge(blockmap, on="column", how="left")


# 4. Apply reverse coding
def reverse_score(x):
    if pd.isna(x): 
        return x
    return 6 - x

df.loc[df["reverse"] == 1, "score"] = df.loc[df["reverse"] == 1, "score"].apply(reverse_score)

# 5. Drop fillers
df = df[df["construct"] != "FILLER"]

# 6. Attention check
# Mark participants who fail attention check
att_check = df[df["construct"] == "ATT_CHECK"]
bad_participants = att_check.loc[att_check["score"] != 5, "Email Address"].unique()
print(f"Excluding {len(bad_participants)} participants who failed attention check.")

df = df[~df["Email Address"].isin(bad_participants)]
df = df[df["construct"].isin(["CSAT","PI","HL","CMP"])]

# 7. Compute scores per participant × prompt × condition
scored = df.groupby(["Email Address","prompt_id","condition","construct"])["score"].mean().reset_index()

# Pivot constructs into columns
scored = scored.pivot(index=["Email Address","prompt_id","condition"], 
                      columns="construct", values="score").reset_index()

# 8. Merge with tasks metadata
scored = scored.merge(tasks_df, on="prompt_id", how="left")

# 9. Save processed file

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
scored.to_csv(OUTPUT_FILE, index=False)
print(f"Saved processed scores → {OUTPUT_FILE}")
