🌱 What I built
This project is a full pipeline to test whether polite chatbot replies make people feel more satisfied and more willing to follow instructions.

Step 1 – Stimuli
We start with real customer prompts and two chatbot replies (Chatbot A vs Chatbot B). Brands are hidden. Replies are paired so each prompt has a “less polite” and a “more polite” version.

Step 2 – Tags
Each reply is coded with politeness strategies (apology, empathy, hedges, refusal, next-step, etc.) using a frozen rulebook. This turns messy text into clean, machine-readable labels.

Step 3 – Survey
We build survey blocks where participants see the A/B replies and rate them on politeness (PI), satisfaction (CSAT), clarity (HL), and compliance (CMP). Neutral filler items and attention checks keep responses honest.

Step 4 – Data
Survey responses are cleaned and merged with metadata and tag labels. This produces tidy tables where each row is one participant’s score for one reply.

Step 5 – Checks
We run quality checks: reliability of survey items (Cronbach’s α), attention-pass rates, and manipulation checks (whether B really scores higher on politeness tags than A).

Step 6 – Analysis
We test A vs B differences with paired t-tests and mixed-effects models. This shows if polite replies truly improve satisfaction, helpfulness, or compliance across all prompts.

Step 7 – Results & Reporting
We generate figures (bar charts with CIs, tag-effect plots), a minimal dashboard, and assemble notes into the final paper/report and presentation.

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
