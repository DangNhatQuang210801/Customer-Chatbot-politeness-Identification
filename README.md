STIMULI & TASKS
Prompts.csv + Replies.csv / Replies-masked.csv → Tasks-json.ipynb → Replies\_Tasks.csv  \[pair\_id, Prompt\_Id, Reply\_Id, condition(A/B), bot\_mask, reply\_text]
Tag Book v1.docx + Tags.txt → Rules\_book.ipynb → tagbook\_v1\_1.json / tagbook\_v1\_1.md  \[frozen rules]
Replies\_Tasks.csv + tagbook\_v1\_1.json → Rules\_book.ipynb → reply\_tags.csv / Logical Tags Prediction.json  \[deterministic tags; no ML]

SURVEY BUILD
Replies\_Tasks.csv (+ optional reply\_tags.csv) → survey\_form\_builder.ipynb → survey\_form\_text\_AB.txt / survey\_form\_text\_BA.txt  \[20 items/reply; AB/BA]
survey\_form\_text\_\* + Replies\_Tasks.csv → survey/make\_block\_map.ipynb → surveyblock\_map.csv  \[maps item → construct; marks reverse; attention\_flag + attention\_key]

SURVEY DATA → TIDY SCORES
Google Forms CSV “Chatbot Rating – Anwers bot masked.csv” + surveyblock\_map.csv → src/preprocess.py → answers\_long.csv / answers\_wide.csv  \[clean, reverse-code, PI/CSAT/HL/CMP means per person×reply]
answers\_long.csv + Replies\_Tasks.csv + reply\_tags.csv → src/preprocess.py → analysis\_merged.csv  \[scores + metadata + tags]
(legacy) processed\_scores.xlsx / predictions.csv → src/preprocess.py → analysis\_merged.csv  \[aligned or deprecated]

QUALITY & MANIPULATION CHECKS
analysis\_merged.csv → src/analysis.py → reliability\_report.md / qc\_tables.csv  \[Cronbach’s α; item stats; attention pass]
Replies\_Tasks.csv + reply\_tags.csv → src/analysis.py → mc\_checks.csv  \[A vs B tag-based Politeness Index per pair\_id/Prompt\_Id]
(alt) analysis\_merged.csv → src/analysis.py → mc\_checks.csv  \[same result via merged table]

MAIN ANALYSES
answers\_long.csv → src/analysis.py → ab\_welch\_per\_prompt.csv / ab\_summary\_overall.csv  \[paired tests by default; Cohen’s d; 95% CIs]
analysis\_merged.csv → src/analysis.py → lme\_results.txt / model\_table.csv  \[mixed-effects: outcome \~ condition + (1|participant\_id) + (1|Prompt\_Id) ± tag covariates]

FIGURES & REPORTING
ab\_summary\_overall.csv + mc\_checks.csv → src/analysis.py → figures/*.png  \[bars with CIs for PI/CSAT/HL/CMP; tag-effect plot]
analysis\_merged.csv → dashboard.py → Streamlit app  \[prompt → replies → tags/scores]
tagbook\_v1\_1.md + survey\_form\_text\_* + reliability\_report.md + ab\_summary\_overall.csv → docs → paper\_notes.md / appendix/

HOUSEKEEPING
Encoding: read/write CSV as UTF-8-SIG; if Windows-encoded, ingest via latin-1 then re-save UTF-8-SIG.
Masking: keep bot\_mask as A/B throughout; never reveal true brands.
Balance: enforce AB/BA quotas; track and correct in preprocessing.
Provenance: one script → one output; deterministic seeds; tagbook v1.1 frozen.
