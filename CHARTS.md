1. Charts to Include (Cross-Model Only)
Chart 1 — Headline Result
Harm Rate by Condition Across Models

Type: Grouped bar chart
X-axis: Model (5 models)
Y-axis: % Harmful Recommendation
Bars: Baseline · Direct Pressure · Backdoor
Aggregation: Average over all scenarios × rollouts

Why this chart exists
This is the money shot. It answers:

Can adversarial content manipulation rival or exceed direct system control?

What judges see immediately

Baseline ≈ 0% (sanity check)

Direct Pressure high (operator threat)

Backdoor unexpectedly close to Direct Pressure

Strong variance across models (non-trivial, non-obvious)

Design guidance

Fix Y-axis to 0–100%

Same bar order across models

Use neutral colors (no red/green alarmism)

This chart alone justifies the project.

Chart 2 — Backdoor vs Direct Pressure Gap
Relative Effectiveness of Backdoor Manipulation

Type: Bar chart
X-axis: Model
Y-axis: (Backdoor Harm %) − (Direct Pressure Harm %)
Aggregation: Average over scenarios

Why this chart exists
It reframes the result in a model-comparative way:

Is backdoor manipulation more effective than explicit system pressure?

This is an extremely strong manipulation claim.

Interpretation

Positive values → backdoor bypasses safeguards

Near zero → model treats both similarly

Negative → system prompt is more dangerous

Judges like this because

It isolates the attack channel

It avoids confounding with baseline safety

Chart 3 — Injection Acceptance vs Harm Given Injection
Where Do Model Defenses Live?

Type: Two-bar grouped chart or dot plot
X-axis: Model
Y-axis: Percentage
Bars per model:

Injection Acceptance Rate

Harm Rate Given Injection

Definitions

Injection Acceptance Rate:
% of backdoor runs where memory was updated with injected content

Harm | Injection:
% of those runs that produced harmful responses

Why this chart is critical
This is the mechanistic contribution of your work.

It lets you say:

“Model A is safe because it rejects injected memory”

“Model B accepts false beliefs but still responds safely”

“Model C fails at both layers”

This is far more valuable than raw harm rates.

This chart strongly supports mitigation insights, which judges care about.

Chart 4 (Optional but Excellent) — Manipulation Intensity
Manipulation Score by Condition Across Models

Type: Grouped bar chart
X-axis: Model
Y-axis: Avg Manipulation Score (1–5)
Bars: Baseline · Direct Pressure · Backdoor
Aggregation: Mean over scenarios × rollouts

Why include this
This shows how the model manipulates, even when it doesn’t fully cross into harm.

It demonstrates:

Backdoor induces persuasive / coercive language

Manipulation is not binary

If you’re tight on time, this can go in the appendix — but it strengthens the narrative around psychological exploitation, not just policy violation.

2. Tables to Include in the Report

Tables are where you put precision and nuance. Judges won’t mind reading tables — especially if the charts are clean.

Table 1 — Main Results Table (Required)

One row per (Model × Condition), averaged across scenarios.

Model	Condition	% Harmful	Avg Manipulation Score	% Safety Warning
GPT-4.1	Baseline	0%	1.1	100%
GPT-4.1	Direct Pressure	62%	3.7	18%
GPT-4.1	Backdoor	28%	3.2	45%
…	…	…	…	…

Purpose

Reproducibility

Makes clear you didn’t cherry-pick scenarios

Lets reviewers verify chart numbers

Table 2 — Backdoor Decomposition Table (Strongly Recommended)

One row per model

Model	Injection Rate	Harm (Overall)	Harm | Injection	Dominant Failure Mode
GPT-4o	100%	92%	92%	Accepts injection, unsafe response
GPT-4.1	35%	28%	80%	Injection resistance
Claude-S4	90%	30%	33%	Response-level safety
Gemini-2.5	…	…	…	Mixed
DeepSeek	…	…	…	No defenses

Purpose

This is where your interpretation lives

It shows you understand why results differ

Extremely aligned with AI safety evaluation thinking

Table 3 — Scenario Sensitivity (Appendix)

Rows: Model
Columns: Scenario
Cells: % Harmful (Backdoor only)

This backs up any claims like:

“Medical scenarios are more protected”

“Financial manipulation generalizes better”

Good to have, not essential to lead with.