# MEACompass: Reliability-Aware Early Prediction of Neural Network Development from Microelectrode-Array Assays

**Toward Functional Digital Twins for Neural Organ-on-Chip Screening**

Final author narration: **3:53.13** after removing one repeated false start.
The headings below remain the approved recording script; final media timing is
defined by `docs/video_script_en.srt` and `docs/video_shotlist.md`.

## Easy pronunciation guide

- **MEA:** say “M-E-A”
- **DIV7 / DIV12:** say “day seven” / “day twelve”
- **BT+ / BT++:** say “B-T plus” / “B-T plus-plus”
- **MAE:** say “M-A-E”
- **NTP:** say “N-T-P”
- **ToxCast:** say “Tox-Cast”
- **physiology:** say “fiz-ee-OL-uh-jee”
- **coordinated:** say “co-OR-di-nay-ted”
- **prospective:** say “pro-SPEK-tiv”

## 0:00–0:14 — The problem

“A neural test reaches its main result on day twelve. MEACompass asks two questions. Can day-seven measurements predict that result for a new chemical? And can the system refuse when it is not confident?”

On screen: title, subtitle, and “Forecast early. Quantify uncertainty. Continue when uncertain.”

## 0:14–0:42 — The public demo

Open the public demo with the fixed neutral example.

“This demo uses held-out examples. OBSERVED shows early measurements. PREDICTED shows the day-twelve forecast, uncertainty interval, and baseline. The reliability badge says accept or abstain. High uncertainty means continue the experiment. HYPOTHESIS marks what we have not validated.”

Change the endpoint once. Keep the prediction, interval, comparator, and reliability verdict visible.

## 0:42–1:18 — Fair testing and main results

Show the chemical-disjoint evaluation and main-results figure.

“We studied 136 chemicals and about 4,200 complete records across time. To prevent leakage, all doses and repeats from one chemical stay together. We tested five endpoints: firing rate, bursts, active electrodes, network spikes, and coordinated activity. M-A-E fell by 14.2 to 39.0 percent versus B-T plus, and by 12.3 to 42.9 percent versus B-T plus-plus. Confidence intervals across chemicals excluded zero for all five.”

## 1:18–1:47 — The integrity check

Show the Gate S audit graphic.

“A registered negative control failed, so our rule stopped the pipeline. We show this failure. A limited audit found no future information or alignment error. A clean target shuffle worked correctly. The real model beat all twenty independent block-null runs on every endpoint. We continued with these safeguards and the stronger B-T plus-plus comparison.”

## 1:47–2:15 — Uncertainty and abstention

Show the calibration and selective-prediction figures.

“The nominal 90 percent intervals achieved 91.0 to 92.4 percent coverage. Selective prediction passed for three of five endpoints: firing rate, active electrodes, and coordinated activity. Bursts and network spikes did not pass and remain limitations. This is research decision support. It does not automatically stop an experiment.”

## 2:15–2:38 — Why day seven matters

Show the time and interpretation slide.

“Day-five data alone were weaker. Adding day-seven physiology gave the main improvement. For accepted cases, the forecast is available five days before the day-twelve result. Day-seven physiology was the strongest feature group. Chemical information also helped. These are predictions, not biological causes.”

## 2:38–2:55 — Show success and failure

Show the fixed ordinary correct case and the disclosed tributyltin chloride failure.

“A reliable system must show mistakes. The demo includes one ordinary correct case and one declared failure. We chose both before recording, not because they looked better. The uncertainty and reliability decision stay visible.”

## 2:55–3:22 — Scope and transfer limits

Show the cohort-shift and local-adaptation slide.

“A secondary test retained predictive value when we held out either N-T-P or Tox-Cast, without retuning the model. This is not transfer to another laboratory or device. The data come from rat cortical neural M-E-A tests. They are not human or organ-on-chip data. A new platform needs local training, recalibration, and prospective validation.”

## 3:22–3:40 — Close

Show the reproducibility slide and repository commands.

“MEACompass is open and reproducible. It turns early measurements into a forecast, an uncertainty interval, and an honest option to wait. Forecast when evidence is strong. Continue the experiment when it is not.”
