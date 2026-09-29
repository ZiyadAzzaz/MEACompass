# MEACompass competition video shot list

Status: recording-ready draft. Total target runtime is 4:45. SRT timestamps remain provisional until the final voice track is recorded. The demo must appear within the first minute.

| Time | Screen | Action / click | Narration focus | On-screen caption | Subtitle cue |
|---|---|---|---|---|---|
| 0:00–0:18 | Deck slide 1 | Slow timeline reveal from DIV5 to DIV12 | State the early-forecast decision and the option to refuse | Forecast early · Quantify uncertainty · Continue when uncertain | EN/ZH cue 1–2 |
| 0:18–0:28 | Public demo landing view | Load the predetermined neutral example; no manual browsing through cases | Explain that the evidence is precomputed and held out | OBSERVED | EN/ZH cue 3 |
| 0:28–0:43 | Demo forecast panel | Point to the forecast, interval, and BT+ comparator | Separate forecast from observation | PREDICTED | EN/ZH cue 3 |
| 0:43–0:58 | Demo reliability panel | Change endpoint once; let all linked panels update | Explain accept versus abstain and the unvalidated transfer boundary | HYPOTHESIS · uncertainty means continue | EN/ZH cue 3 |
| 0:58–1:12 | Deck slide 4 | Highlight chemical-group split, then outer evaluation | Explain why random well splitting would leak chemical identity | Chemical-disjoint evaluation | EN/ZH cue 4 |
| 1:12–1:30 | Deck slide 5 | Reveal endpoint bars, then BT++ card | Report all five endpoints and the two locked gain ranges | All five endpoints improved; paired chemical CI excludes zero | EN/ZH cue 4 |
| 1:30–2:05 | Deck slide 6 | Trace registered stop → bounded audit → conditional continuation | Lead with the failed negative control and safeguards | The failure remains visible | EN/ZH cue 5 |
| 2:05–2:24 | Deck slide 7 | Point to nominal marker and empirical endpoint ticks | Explain chemical-held-out interval coverage | Nominal 90% intervals; calibrated on training chemicals only | EN/ZH cue 6 |
| 2:24–2:45 | Deck slide 8 | Point to the threshold, three passes, and two limitations | Explain selective prediction and why uncertainty is not a stop command | 3/5 pass · 2/5 limitations | EN/ZH cue 6 |
| 2:45–3:20 | Deck slide 9 | Build DIV5 → DIV7 → post-lock DIV9 → DIV12; point to contribution bands | Explain time causality, accepted-case lead time, and predictive—not causal—interpretation | DIV7 forecasts are available five days early for accepted cases | EN/ZH cue 7–8 |
| 3:20–3:35 | Demo correct-case view | Load the predeclared ordinary correct case | Show forecast, interval, and verdict without celebration styling | Representative held-out case | Final retimed cue |
| 3:35–3:50 | Demo failure-case view | Load tributyltin chloride using the predeclared recording checklist | Show the error and reliability display without hiding it | Disclosed failure case | Final retimed cue |
| 3:50–4:22 | Deck slide 11 | Point to both cohort-shift directions, then local adaptation steps | Use the approved narrow cohort-shift wording; deny lab/device transfer | Post-lock secondary · not external-device transfer | Final retimed cue |
| 4:22–4:45 | Deck slide 12 | Highlight `make test`, `make reproduce-lite`, and `make demo` | Close on auditability, calibration, and the option to wait | Forecast when evidence is strong; continue when it is not | EN/ZH cue 9–10 |

## Recording checklist

- Capture the real public demo in a logged-out browser before replacing deck slide 10.
- Fix the neutral, correct, and failure examples before recording; record the selection rule in `docs/decisions.md`.
- Do not search among cases during recording or choose visually favorable examples.
- Keep the mouse still while narrating; use one deliberate click per visual change.
- Keep the labels **OBSERVED**, **PREDICTED**, and **HYPOTHESIS** visible.
- Do not say that every assay finishes early. Use: “DIV7 forecasts are available five days before the DIV12 endpoint for accepted cases.”
- Do not claim external laboratory, device, human, or organ-on-chip transfer.
- Retake only for factual or delivery errors; never alter displayed evidence to improve appearance.

## Spoken-number budget

The narration intentionally concentrates quantitative speech into six evidence groups: 136 chemicals; about 4,200 trajectories; 14.2–39.0% versus BT+; 12.3–42.9% versus BT++; 91.0–92.4% interval coverage; and three of five abstention endpoints. Other detail stays visual.
