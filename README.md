Stimuli & tasks
Prompts.csv + Replies.csv/Replies-masked.csv → Tasks-json.ipynb → assemble A/B reply pairs per prompt, assign stable pair_id (or reuse Prompt_Id), mask brands, emit Label Studio tasks → Replies_Tasks.csv (pair_id, Prompt_Id, Reply_Id, condition A/B, bot_mask, reply_text).
Tag Book v1.docx + Tags.txt → Rules_book.ipynb → freeze tag definitions and export machine-readable rules → tagbook_v1_1.json / tagbook_v1_1.md.
Replies_Tasks.csv + tagbook_v1_1.json → Rules_book.ipynb → apply deterministic rules to each reply (no ML), generate tag binaries/notes → reply_tags.csv and/or Logical Tags Prediction.json.

Survey build
Replies_Tasks.csv (+ optional reply_tags.csv only for balancing/stratification) → survey/survey_form_builder.ipynb → construct 20-item blocks per reply (PI, CSAT, HL, CMP + neutral fillers + 1 attention check), AB/BA counterbalance → survey_form_text_AB.txt, survey_form_text_BA.txt.
survey_form_text_* + Replies_Tasks.csv → survey/make_block_map.ipynb → map Google Form item IDs → constructs → stimuli (pair_id/Reply_Id/Prompt_Id/condition); mark reverse-coded and attention items, include attention_flag and attention_key → surveyblock_map.csv.

Survey data → tidy scores
Google Forms export (Chatbot Rating - Anwers bot masked.csv) + surveyblock_map.csv → src/preprocess.py (or notebooks/preprocess.ipynb) → clean, normalize participant_id and item_id, reverse-code, compute per-construct means (PI, CSAT, HL, CMP) per respondent × reply, compute attention pass using attention_key; enforce UTF-8-SIG → answers_long.csv (tidy) + answers_wide.csv.
answers_long.csv + Replies_Tasks.csv + reply_tags.csv → src/preprocess.py → merge perceptions with tags and metadata → analysis_merged.csv.
(Optional legacy) processed_scores.xlsx / predictions.csv → src/preprocess.py → align or deprecate into the same schema → analysis_merged.csv updated.

Quality & manipulation checks
analysis_merged.csv → src/analysis.py (or notebooks/analysis.ipynb) → reliability (Cronbach’s α), item stats, attention-pass report → reliability_report.md, qc_tables.csv.
Preferred minimal path for manipulation checks (reply-level, no respondent data needed): Replies_Tasks.csv + reply_tags.csv → src/analysis.py → A vs B differences in tag-based Politeness Index per pair_id/Prompt_Id → mc_checks.csv.
(Alternatively, compute the same from analysis_merged.csv for convenience.)

Main analyses
answers_long.csv → src/analysis.py → paired t-tests within prompt/respondent (default), Cohen’s d, 95% CIs; use Welch only for any independent-sample comparisons → ab_welch_per_prompt.csv, ab_summary_overall.csv.
analysis_merged.csv → src/analysis.py → mixed-effects: outcome ~ condition + (1|participant_id) + (1|Prompt_Id) [+ optional tag covariates: apology/hedge/refusal±/next-step] → lme_results.txt, model_table.csv.

Figures & reporting
ab_summary_overall.csv + mc_checks.csv → src/analysis.py → bar charts with CIs for PI, CSAT, HL, CMP; tag-by-effect exploratory plot → figures/.png.
analysis_merged.csv → dashboard.py (Streamlit) → minimal drill-down (prompt → replies → scores/tags) → app script.
tagbook_v1_1.md + survey_form_text_ + reliability_report.md + ab_summary_overall.csv → docs assembly → paper_notes.md, appendix/.

Housekeeping & notes
Encoding: assume UTF-8-SIG for CSV I/O; for Windows-encoded sources (Replies.csv/Replies-masked.csv), load with fallback (latin-1) then re-save UTF-8-SIG.
Masking: keep bot_mask as A/B end-to-end; never expose true brand strings in survey or outputs.
Balance: enforce AB/BA quotas in survey; track in preprocess (drop or weight if imbalanced).
Provenance: each output path is written by a single script/notebook; prefer deterministic seeds and frozen tagbook v1.1.