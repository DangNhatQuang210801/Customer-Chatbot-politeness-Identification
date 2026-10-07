"""Build docs/index.html, a static dashboard of the chatbot politeness survey.

Reads survey/answers_long.csv (one row per participant and rating item) and the
first-language column of survey/Answers Masked.csv. Only aggregates are written
to the page; no participant-level rows leave this script.

Run from anywhere:  python dashboard/build_dashboard.py
"""
import html
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "index.html"
REPO = "https://github.com/DangNhatQuang210801/Customer-Chatbot-politeness-Identification"
PLOTLY_JS = "https://cdn.plot.ly/plotly-basic-4.1.1.min.js"

CONSTRUCTS = {
    "PI": "Politeness (PI)",
    "CSAT": "Satisfaction (CSAT)",
    "HL": "Clarity (HL)",
    "CMP": "Compliance (CMP)",
}
BOTS = {"A": "Chatbot A", "B": "Chatbot B"}

# Light-mode colours. The page swaps each one for its dark-mode partner in DARK.
COL = {"A": "#2a78d6", "B": "#eb6834"}
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
LIKERT = ["#c4383a", "#ee8c84", "#e6e5df", "#86b6ef", "#256abf"]
DARK = {
    "#2a78d6": "#3987e5", "#eb6834": "#d95926", "#0b0b0b": "#ffffff", "#52514e": "#c3c2b7",
    "#e1e0d9": "#2c2c2a", "#c3c2b7": "#383835", "#fcfcfb": "#1a1a19", "#e6e5df": "#6b6a65",
}
pio.templates.default = "none"


def ci(series):
    """Mean and 95% t-interval half-width."""
    s = series.dropna()
    return s.mean(), stats.t.ppf(0.975, len(s) - 1) * s.sem()


def fmt_p(p):
    return "&lt; .001" if p < 0.001 else f"{p:.3f}".replace("0.", ".", 1)


def base_layout(fig, height, xtitle):
    fig.update_layout(
        height=height, margin=dict(l=8, r=12, t=36, b=48),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=INK),
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", font=dict(color=INK2)),
        hoverlabel=dict(font=dict(family="system-ui, sans-serif")),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zerolinecolor=AXIS, tickfont=dict(color=MUTED),
                     title=dict(text=xtitle, font=dict(color=INK2, size=12)))
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, tickfont=dict(color=INK2), automargin=True)
    return fig


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


# ---------------------------------------------------------------- data
df = pd.read_csv(ROOT / "survey" / "answers_long.csv", encoding="utf-8-sig")
df["scenario"] = df["scenario"].str.split(" – ", n=1).str[1] + " (" + df["Prompt_Id"] + ")"
raw = pd.read_csv(ROOT / "survey" / "Answers Masked.csv", encoding="utf-8-sig")
lang = raw.iloc[:, -1].str.strip()  # "Is your first language English ?"

n_part = df["participant_id"].nunique()
n_ratings = len(df)
n_items = df["question_text"].nunique()
n_scen = df["Prompt_Id"].nunique()
n_native = int((lang == "Yes").sum())
n_raw_items = raw.shape[1] - 1

# participant x construct x chatbot means (every participant answered every item)
pc = df.groupby(["construct", "participant_id", "condition"])["score"].mean().unstack("condition")
# participant x scenario x construct x chatbot means (same values as construct_scores_long.csv)
ps = df.groupby(["construct", "scenario", "participant_id", "condition"])["score"].mean().unstack("condition")

means, part_tests, prompt_tests, scen = [], [], [], []
for c, label in CONSTRUCTS.items():
    g = pc.loc[c]
    (ma, ha), (mb, hb) = ci(g["A"]), ci(g["B"])
    means.append((c, label, ma, ha, mb, hb))

    # participant-level paired t-test: each person's B mean vs A mean
    r = stats.ttest_rel(g["B"], g["A"])
    d = g["B"] - g["A"]
    lo, hi = r.confidence_interval()
    part_tests.append((label, len(d), d.mean(), r.statistic, int(r.df), r.pvalue, lo, hi, d.mean() / d.std()))

    # prompt-level paired t-test, as in the report: B - A per scenario, one-sample t across scenarios
    sc = ps.loc[c].groupby("scenario")[["A", "B"]].mean()
    k = sc["B"] - sc["A"]
    r = stats.ttest_1samp(k, 0)
    lo, hi = r.confidence_interval()
    prompt_tests.append((label, len(k), k.mean(), r.statistic, int(r.df), r.pvalue, lo, hi, k.mean() / k.std()))

    # per scenario: mean difference with a paired 95% CI across participants
    for s, gs in ps.loc[c].groupby("scenario"):
        m, h = ci(gs["B"] - gs["A"])
        scen.append((c, label, s, gs["A"].mean(), gs["B"].mean(), m, h))

dist = (df.groupby(["construct", "condition"])["score"].value_counts(normalize=True)
          .unstack().reindex(columns=range(1, 6), fill_value=0) * 100)

# ---------------------------------------------------------------- charts
fig_means = go.Figure()
for b in "AB":
    i = 2 if b == "A" else 4
    fig_means.add_scatter(
        x=[round(m[i], 3) for m in means], y=[m[1] for m in means], name=BOTS[b], mode="markers",
        offsetgroup=b, error_x=dict(type="data", array=[round(m[i + 1], 3) for m in means], color=COL[b], thickness=2, width=4),
        marker=dict(size=12, color=COL[b], line=dict(color=SURFACE, width=2)),
        customdata=[[round(m[i] - m[i + 1], 2), round(m[i] + m[i + 1], 2)] for m in means],
        hovertemplate=f"{BOTS[b]}<br>%{{y}}: %{{x:.2f}}<br>95% CI %{{customdata[0]}} to %{{customdata[1]}}<extra></extra>",
    )
base_layout(fig_means, 320, "Mean rating (1–5)")
fig_means.update_layout(scattermode="group", scattergap=0.5)
fig_means.update_yaxes(autorange="reversed", showgrid=False)

rows_h = [5 if c == "PI" else 3 for c in CONSTRUCTS]
fig_scen = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.07, row_heights=rows_h,
                         subplot_titles=list(CONSTRUCTS.values()))
shown = set()
for row, c in enumerate(CONSTRUCTS, start=1):
    pts = [s for s in scen if s[0] == c]
    for b, keep in (("A", lambda v: v < 0), ("B", lambda v: v >= 0)):
        sel = [s for s in pts if keep(s[5])]
        fig_scen.add_scatter(
            x=[round(s[5], 3) for s in sel], y=[s[2].rsplit(" (", 1)[0].replace(" / ", " /<br>") for s in sel], mode="markers", row=row, col=1,
            name=f"{BOTS[b]} rated higher", legendgroup=b, showlegend=b not in shown and bool(sel),
            error_x=dict(type="data", array=[round(s[6], 3) for s in sel], color=COL[b], thickness=2, width=4),
            marker=dict(size=11, color=COL[b], line=dict(color=SURFACE, width=2)),
            customdata=[[round(s[3], 2), round(s[4], 2)] for s in sel],
            hovertemplate="%{y}<br>B − A: %{x:+.2f}<br>A %{customdata[0]}, B %{customdata[1]}<extra></extra>",
        )
        shown |= {b} if sel else set()
base_layout(fig_scen, 600, "Chatbot B − Chatbot A (rating points)")
fig_scen.update_xaxes(zeroline=True, zerolinewidth=1)
for r in (1, 2, 3):
    fig_scen.update_xaxes(title_text="", row=r, col=1)
fig_scen.update_yaxes(autorange="reversed", showgrid=False)
fig_scen.update_annotations(font=dict(size=13, color=INK), x=0, xanchor="left")
fig_scen.update_layout(margin=dict(t=64), legend=dict(y=1.06))

fig_dist = go.Figure()
labels = [f"{CONSTRUCTS[c].split(' (')[0]} · {b}" for c in CONSTRUCTS for b in "AB"]
score_names = ["1 completely disagree", "2", "3", "4", "5 completely agree"]
for s in range(1, 6):
    fig_dist.add_bar(
        x=[round(dist.loc[(c, b), s], 2) for c in CONSTRUCTS for b in "AB"], y=labels, orientation="h",
        name=score_names[s - 1], marker=dict(color=LIKERT[s - 1], line=dict(color=SURFACE, width=1)),
        hovertemplate=f"%{{y}}<br>Score {s}: %{{x:.1f}}% of ratings<extra></extra>",
    )
base_layout(fig_dist, 420, "Share of ratings (%)")
fig_dist.update_layout(barmode="stack", bargap=0.45, legend=dict(traceorder="normal"))
fig_dist.update_xaxes(range=[0, 100], ticksuffix="%")
fig_dist.update_yaxes(autorange="reversed", showgrid=False)

FIGS = {"means": fig_means, "scen": fig_scen, "dist": fig_dist}
figs_json = "{" + ",".join(f'"{k}":{pio.to_json(f, remove_uids=True)}' for k, f in FIGS.items()) + "}"
figs_json = figs_json.replace("</", "<\\/")

# ---------------------------------------------------------------- tables
f2 = lambda v: f"{v:.2f}"
f3 = lambda v: f"{v:+.3f}"
means_tbl = table(["Construct", "Chatbot A mean [95% CI]", "Chatbot B mean [95% CI]"],
                  [(m[1], f"{m[2]:.2f} [{m[2]-m[3]:.2f}, {m[2]+m[3]:.2f}]", f"{m[4]:.2f} [{m[4]-m[5]:.2f}, {m[4]+m[5]:.2f}]") for m in means])
test_head = ["Construct", "n", "Mean diff (B − A)", "t", "df", "p", "95% CI", "d<sub>z</sub>"]
test_rows = lambda ts: [(t[0], t[1], f3(t[2]), f2(t[3]), t[4], fmt_p(t[5]), f"[{t[6]:.3f}, {t[7]:.3f}]", f2(t[8])) for t in ts]
prompt_tbl = table(["Construct", "Scenarios (k)"] + test_head[2:], test_rows(prompt_tests))
part_tbl = table(["Construct", "Participants"] + test_head[2:], test_rows(part_tests))
scen_tbl = table(["Construct", "Scenario", "Mean A", "Mean B", "B − A [95% CI]"],
                 [(s[1], html.escape(s[2]), f2(s[3]), f2(s[4]), f"{s[5]:+.2f} [{s[5]-s[6]:+.2f}, {s[5]+s[6]:+.2f}]") for s in scen])
dist_tbl = table(["Construct", "Chatbot"] + [f"{s}" for s in range(1, 6)],
                 [(CONSTRUCTS[c], b, *(f"{dist.loc[(c, b), s]:.1f}%" for s in range(1, 6))) for c in CONSTRUCTS for b in "AB"])

# ---------------------------------------------------------------- page
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chatbot Politeness Survey</title>
<meta name="description" content="Aggregate results of a survey in which {n_part} participants rated two customer-service chatbots on politeness, satisfaction, clarity and compliance.">
<style>
:root {{
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --muted: #898781;
  --line: #e1e0d9; --ring: rgba(11,11,11,0.10); --a: #2a78d6; --b: #eb6834;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #ffffff; --ink2: #c3c2b7; --muted: #898781;
    --line: #2c2c2a; --ring: rgba(255,255,255,0.10); --a: #3987e5; --b: #d95926;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--page); color: var(--ink);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 32px 16px 48px; }}
h1 {{ font-size: 1.6rem; line-height: 1.25; margin: 0 0 8px; }}
h2 {{ font-size: 1.15rem; margin: 0 0 4px; }}
p {{ margin: 0 0 12px; }}
a {{ color: var(--a); }}
.lead {{ color: var(--ink2); max-width: 68ch; }}
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 24px 0; }}
.tile, .card {{ background: var(--surface); border: 1px solid var(--ring); border-radius: 12px; }}
.tile {{ padding: 14px 16px; }}
.tile .v {{ font-size: 1.7rem; font-weight: 600; }}
.tile .l {{ color: var(--ink2); font-size: 0.9rem; }}
.card {{ padding: 20px 16px 12px; margin: 0 0 20px; }}
.card > p, .note {{ color: var(--ink2); font-size: 0.92rem; max-width: 72ch; }}
.chart {{ width: 100%; }}
details {{ margin: 8px 0 4px; }}
summary {{ cursor: pointer; color: var(--ink2); font-size: 0.9rem; }}
.scroll {{ overflow-x: auto; margin: 8px 0 12px; }}
table {{ border-collapse: collapse; font-size: 0.88rem; font-variant-numeric: tabular-nums; min-width: 100%; }}
th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
th {{ color: var(--ink2); font-weight: 600; }}
h3 {{ font-size: 0.98rem; margin: 16px 0 0; }}
ul {{ padding-left: 20px; margin: 0; }}
li {{ margin-bottom: 6px; }}
footer {{ color: var(--muted); font-size: 0.85rem; margin-top: 24px; }}
</style>
</head>
<body>
<main>
<h1>Customer chatbot politeness study</h1>
<p class="lead">Survey results for two customer-service chatbots, shown to participants as Chatbot A and Chatbot B.
Each participant rated both chatbots' replies to the same five customer scenarios on a 1–5 scale.
Research Project 1, Linguistic Data Science Lab, Ruhr University Bochum, by Dang Nhat Quang.
Code and data: <a href="{REPO}">GitHub repository</a>.</p>

<div class="tiles">
  <div class="tile"><div class="v">{n_part}</div><div class="l">participants</div></div>
  <div class="tile"><div class="v">{n_ratings:,}</div><div class="l">ratings analysed</div></div>
  <div class="tile"><div class="v">{n_scen}</div><div class="l">customer scenarios</div></div>
  <div class="tile"><div class="v">{n_items}</div><div class="l">rating items ({n_items // 2} per chatbot)</div></div>
</div>

<section class="card">
  <h2>Mean rating by construct</h2>
  <p>Each dot is the mean over all {n_part} participants; bars show the 95% confidence interval. The axis is zoomed in: all means lie between {min(min(m[2], m[4]) for m in means):.2f} and {max(max(m[2], m[4]) for m in means):.2f} on the 1–5 scale.</p>
  <div id="means" class="chart"></div>
  <details><summary>Table view</summary>{means_tbl}</details>
</section>

<section class="card">
  <h2>Paired t-tests, Chatbot B against Chatbot A</h2>
  <p>Negative differences mean Chatbot B was rated lower than Chatbot A.</p>
  <h3>Scenario level (the test used in the project report)</h3>
  <p class="note">For each scenario, the mean rating of B minus the mean rating of A. The test uses one difference per scenario ({min(t[1] for t in prompt_tests)} to {max(t[1] for t in prompt_tests)} per construct), so df is the number of scenarios minus one and the test has little power. Significant at p &lt; .05: {", ".join(t[0] for t in prompt_tests if t[5] < 0.05) or "none"}.</p>
  {prompt_tbl}
  <h3>Participant level (added for this page)</h3>
  <p class="note">For each participant, their mean rating of B minus their mean rating of A on the same items. This shows how these {n_part} participants rated these particular replies; unlike the scenario-level test, it says nothing about other scenarios.</p>
  {part_tbl}
</section>

<section class="card">
  <h2>Difference by scenario</h2>
  <p>Mean of B − A for each scenario. Not every scenario had items for every construct (scenarios per construct: {", ".join(f"{t[0]} {t[1]}" for t in prompt_tests)}). Bars show a paired 95% confidence interval across participants.</p>
  <div id="scen" class="chart"></div>
  <details><summary>Table view</summary>{scen_tbl}</details>
</section>

<section class="card">
  <h2>How the ratings are distributed</h2>
  <p>Share of all ratings at each point of the scale, by construct and chatbot.</p>
  <div id="dist" class="chart"></div>
  <details><summary>Table view</summary>{dist_tbl}</details>
</section>

<section class="card">
  <h2>About the data</h2>
  <ul class="note">
    <li>Source: <code>survey/answers_long.csv</code>, the cleaned long-format export of the survey ({n_part} participants × {n_items} items = {n_ratings:,} ratings).</li>
    <li>The questionnaire had {n_raw_items} rating items. The two reverse-worded items ("The reply feels curt or blaming") were mapped to a separate check construct and are not part of the four scores.</li>
    <li>{n_native} of {n_part} participants answered that English is their first language.</li>
    <li>Item reliability (Cronbach's alpha) was not calculated, and no mixed-effects models were fitted.</li>
    <li>This page shows aggregates only. It was generated by <code>dashboard/build_dashboard.py</code>.</li>
  </ul>
</section>
<footer>Ratings: 1 = completely disagree, 5 = completely agree.</footer>
</main>
<script src="{PLOTLY_JS}" charset="utf-8"></script>
<script>
const FIGS = {figs_json};
const DARK = {json.dumps(DARK)};
const mq = matchMedia("(prefers-color-scheme: dark)");
function draw() {{
  for (const [id, fig] of Object.entries(FIGS)) {{
    let s = JSON.stringify(fig);
    if (mq.matches) s = s.replace(/#[0-9a-f]{{6}}/gi, m => DARK[m.toLowerCase()] || m);
    const f = JSON.parse(s);
    Plotly.react(id, f.data, f.layout, {{responsive: true, displayModeBar: false}});
  }}
}}
draw();
mq.addEventListener("change", draw);
</script>
</body>
</html>
"""
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.1f} KB): "
      f"{n_part} participants, {n_ratings} ratings, {n_items} items, {n_scen} scenarios")
