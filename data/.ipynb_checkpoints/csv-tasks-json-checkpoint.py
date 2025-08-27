import pandas as pd
import json
from pathlib import Path

csv_path = Path("Replies_Label_Studio.csv")  # change if needed
json_out = Path("tasks_clean_fixed.json")    # output file

df = pd.read_csv(csv_path)

text_col_candidates = ["reply_text", "reply", "text"]
text_col = next((c for c in text_col_candidates if c in df.columns), None)
if text_col is None:
    raise ValueError(f"None of {text_col_candidates} found in CSV columns: {list(df.columns)}")

bot_col_candidates = ["bot", "brand", "source", "system"]
bot_col = next((c for c in bot_col_candidates if c in df.columns), None)

# Brand masking: map each bot name to Chatbot A/B
bot_map = {}
if bot_col:
    bots = list(df[bot_col].dropna().unique())
    for i, b in enumerate(bots):
        bot_map[b] = f"Chatbot {'AB'[i % 2]}"
    df["bot_mask"] = df[bot_col].map(bot_map)
else:
    df["bot_mask"] = None
    bot_map = {}

tasks = []
for i, row in df.iterrows():
    task = {
        "id": int(i + 1),
        "data": {
            "reply_text": str(row[text_col]).strip(),
            "bot_mask": row["bot_mask"] if pd.notna(row["bot_mask"]) else ""
        }
    }
    tasks.append(task)

# Save JSON
with open(json_out, "w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"✅ Wrote {len(tasks)} tasks to {json_out}")
print(f"Brand masking: {bot_map}")
