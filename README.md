# Customer chatbot politeness study

Do polite chatbot replies make customers more satisfied and more willing to
follow instructions? This repository holds the data, notebooks and documents
of an individual research project by Dang Nhat Quang (Research Project 1,
Linguistic Data Science Lab, Ruhr University Bochum; instructor
Prof. Dr. Ralf Klabunde; May to December 2025).

Two customer-service chatbots answered the same 60 customer prompts. Each
reply was tagged with rule-based politeness tags, and 350 survey participants
rated both chatbots' replies to five of the prompts. The chatbots appear as
Chatbot A and Chatbot B in the survey and in the analysis files.

**Dashboard:** https://dangnhatquang210801.github.io/Customer-Chatbot-politeness-Identification/

## Results in brief

The project report compares the chatbots with a scenario-level paired t-test:
for each scenario, the mean rating of Chatbot B minus the mean rating of
Chatbot A, tested against zero across scenarios
(`survey/ab_summary_overall.csv`).

| Construct | Scenarios | Mean difference (B − A) | t | p |
|---|---|---|---|---|
| Politeness (PI) | 5 | −0.192 | −3.728 | .020 |
| Satisfaction (CSAT) | 3 | −0.092 | −0.907 | .460 |
| Clarity / helpfulness (HL) | 3 | 0.095 | 0.483 | .677 |
| Compliance intention (CMP) | 3 | −0.411 | −1.141 | .372 |

Chatbot B was rated less polite than Chatbot A. The other differences are not
significant at the scenario level, which rests on only three scenarios each.
The dashboard also shows a participant-level paired t-test (350 participants)
and the results per scenario.

## Pipeline

### 1. Prompts and replies (`data/`)

- `Prompts.csv`: 60 customer prompts with domain and goal.
- `Replies.csv`: both chatbots' reply to each prompt.
- `Replies-masked.csv`: the same replies labelled Chatbot A and Chatbot B.
- `Replies_Tasks.csv`: the 120 replies in long format
  (`Prompt_Id`, `Reply_Id`, `condition`, `reply_text`).
- `Tasks-json.ipynb`: turns `Replies_Tasks.csv` into `tasks_data.json`
  (120 Label Studio tasks).

### 2. Politeness tagging

`data/Rules_book.ipynb` applies fixed regular-expression rules for six tags
(T01 empathy/gratitude, T02 apology, T03 positive flexibility, T04
mitigation/hedging, T05 refusal, T06 general answer), with a negation check
for apologies and a fixed tag order. It writes `data/predictions.csv` (top
tag and all tags per reply). Running the notebook again reproduces
`predictions.csv` exactly.

- `reports/Tag Book v1.docx`: tag definitions.
- `reports/Tags.txt`: Label Studio labelling configuration for the six tags.
- `reports/Logical Tags Prediction.json`: tags for the 120 replies in Label
  Studio import format.

### 3. Survey (`survey/`)

Five scenarios (prompts P03, P04, P07, P08 and P23) each showed Chatbot A's and
Chatbot B's reply. Every reply had four statements rated from 1 (completely
disagree) to 5 (completely agree): 40 rating items, plus a question on whether
English is the participant's first language.

- `surveyblock_map.csv`: maps each item to its construct: politeness (PI),
  satisfaction (CSAT), clarity/helpfulness (HL) or compliance intention (CMP).
  The two reverse-worded items ("The reply feels curt or blaming") are coded
  `RC`.
- `Answers Masked.csv`: the raw responses of 350 participants. It holds no
  names, e-mail addresses or timestamps.
- `results/`: questionnaire text, the reply pairs shown, the survey rule book,
  an explanation of the analysis files and references.

### 4. Cleaning and scoring

The first cell of `survey/preprocess.ipynb` reads the export and the block
map, reshapes the answers to one row per participant and item, maps items to
constructs, checks that every prompt has an A and a B reply, and writes:

- `answers_long.csv`: 13,300 ratings (350 participants × 38 items).
- `processed_scores.csv` and `processed_scores.xlsx`: mean per prompt,
  chatbot and construct.

The notebook also contains reverse-scoring and attention-check steps. They do
not change this data set: the two reverse-worded items are coded `RC` and left
out of the four constructs, and the export has no attention-check item.

`construct_scores_long.csv` holds the mean per participant, scenario, chatbot
and construct (9,800 rows). The code that wrote it is not in the repository;
`dashboard/build_dashboard.py` computes the same values from
`answers_long.csv`.

### 5. Analysis

- The second cell of `survey/preprocess.ipynb` runs a Welch t-test for each
  prompt and construct (`ab_welch_per_prompt.csv`) and the scenario-level
  paired test with 95% confidence intervals and Cohen's d<sub>z</sub>
  (`ab_summary_overall.csv`).
- `survey/analysis.ipynb` repeats the summary from `processed_scores.csv`
  (`analysis_summary.csv`, `analysis_per_prompt.csv`) and plots B − A by
  construct.
- `reports/tag_effects.csv` lists the mean B − A difference where only one of
  the two replies carries a tag (column guide in `reports/tag_effects.txt`).
  The code that produced it is not in the repository.

### 6. Dashboard

`dashboard/build_dashboard.py` reads `survey/answers_long.csv` and writes
`docs/index.html`, a single static page served by GitHub Pages. It shows
aggregates only: sample size, mean ratings per construct, the paired t-tests,
differences per scenario and rating distributions.

```
python -m venv .venv
.venv\Scripts\activate          # Windows; use "source .venv/bin/activate" elsewhere
pip install -r dashboard/requirements.txt
python dashboard/build_dashboard.py
```

The notebooks use relative paths, so run them from their own folder. They need
pandas, NumPy and SciPy; `analysis.ipynb` also needs matplotlib, and writing
`processed_scores.xlsx` needs openpyxl.

## Limitations

- The scenario-level tests rest on three to five scenarios.
- Item reliability (Cronbach's alpha) was not calculated.
- No mixed-effects models were fitted.
- Tag effects are associations based on a few prompts, not causal effects.

## Documents

- `Reseach 1.docx`: the project report.
- `NhatQuang-Research1.pptx`: the project presentation.
- `reports/Presentation plan.txt` and `src/Workflow check list.txt`: early
  planning notes. They name files that were planned but never created (for
  example `src/preprocess.py`, `analysis_merged.csv`, mixed-effects outputs
  and a Streamlit dashboard), and the percentages in the checklist are not a
  current status.
