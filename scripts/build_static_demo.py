from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DISPLAY_ENDPOINTS = ["meanfiringrate", "nAE", "r"]
REQUIRED = {
    "sample_id", "casrn", "trt", "cohort", "dose", "endpoint",
    "observed_div5", "observed_div7", "observed_div9", "target12",
    "prediction", "uncertainty_lower", "uncertainty_upper",
    "bt_plus_plus_prediction", "day9_prediction", "day9_lower", "day9_upper",
    "verdict",
}


def select_rows(frame: pd.DataFrame, per_cohort: int = 50) -> pd.DataFrame:
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Demo source is missing columns: {sorted(missing)}")
    display = frame.loc[frame["endpoint"].isin(DISPLAY_ENDPOINTS)].copy()
    complete = display.groupby("sample_id")["endpoint"].nunique()
    display = display.loc[display["sample_id"].isin(complete[complete.eq(3)].index)]
    chosen: list[str] = []
    for cohort in sorted(display["cohort"].dropna().unique()):
        ids = sorted(display.loc[display["cohort"].eq(cohort), "sample_id"].unique())
        chosen.extend(ids[:per_cohort])
    selected = display.loc[display["sample_id"].isin(chosen), sorted(REQUIRED)].copy()
    selected = selected.sort_values(["cohort", "sample_id", "endpoint"])
    if selected.empty:
        raise ValueError("No complete three-endpoint samples are available")
    return selected


HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MEACompass · Static Demo</title>
  <style>
    :root{--ink:#12202a;--paper:#f4efe6;--white:#fffdf8;--blue:#2d6cdf;--mint:#4cb7a5;--amber:#d8a13a;--coral:#e46f61;--soft:#65737b;--rule:#d8d0c4}
    *{box-sizing:border-box} body{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,sans-serif;line-height:1.45}
    header{background:var(--ink);color:var(--white);padding:34px max(24px,calc((100vw - 1180px)/2)) 30px;border-bottom:6px solid var(--mint)}
    header h1{font-family:Georgia,serif;font-size:clamp(34px,5vw,60px);margin:0 0 6px} header h2{font:700 clamp(17px,2.2vw,26px) Georgia,serif;max-width:980px;margin:0}
    header p{color:#b9d7d1;margin:12px 0 0;font-weight:700}.shell{max-width:1180px;margin:28px auto;padding:0 22px 42px}
    .notice{border-left:5px solid var(--blue);background:var(--white);padding:14px 18px;margin-bottom:22px;font-weight:700}
    .controls{display:grid;grid-template-columns:2fr 1fr 1.4fr;gap:16px;padding:20px;background:var(--white);border:1px solid var(--rule)}
    label{display:block;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--soft);margin-bottom:6px}
    select{width:100%;padding:11px;border:1px solid #aeb8ba;background:white;color:var(--ink);font-weight:700}.toggles{display:flex;gap:20px;margin:18px 0;flex-wrap:wrap}.toggles label{letter-spacing:0;text-transform:none;font-size:14px;color:var(--ink)}
    .context{margin:18px 0;padding:12px 16px;background:#dfe9f7;border-left:5px solid var(--blue);font-weight:700}
    .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.panel{background:var(--white);border-top:6px solid var(--blue);padding:18px;min-height:330px}.panel:nth-child(2){border-color:var(--mint)}.panel:nth-child(3){border-color:var(--amber)}
    h3{font-family:Georgia,serif;font-size:22px;margin:0 0 14px} table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:right;padding:9px 7px;border-bottom:1px solid var(--rule)}th:first-child,td:first-child{text-align:left}th{color:var(--soft);font-size:11px;text-transform:uppercase}
    .badge{display:inline-block;margin-top:18px;padding:10px 14px;font-weight:900;background:var(--mint)}.badge.wait{background:#f3c96e}.caption{font-size:12px;color:var(--soft);margin-top:13px}.reveal{background:var(--white);padding:18px;margin-top:18px;border-left:5px solid var(--coral)}
    footer{margin-top:22px;padding:18px;background:var(--ink);color:var(--white)}footer strong{color:var(--mint)}
    @media(max-width:850px){.controls,.grid{grid-template-columns:1fr}.panel{min-height:auto}}
  </style>
</head>
<body>
<header>
  <h1>MEACompass</h1>
  <h2>Reliability-Aware Early Prediction of Neural Network Development from Microelectrode-Array Assays</h2>
  <p>Toward Functional Digital Twins for Neural Organ-on-Chip Screening</p>
</header>
<main class="shell">
  <div class="notice">Static, privacy-safe demonstration. Every value is a precomputed outer-test prediction; this page performs no model training and makes no network request.</div>
  <section class="controls">
    <div><label for="chemical">Chemical</label><select id="chemical"></select></div>
    <div><label for="dose">Dose</label><select id="dose"></select></div>
    <div><label for="well">Held-out well</label><select id="well"></select></div>
  </section>
  <div class="toggles">
    <label><input id="div9" type="checkbox"> What if we wait until DIV9?</label>
    <label><input id="reveal" type="checkbox"> Reveal observed DIV12</label>
  </div>
  <div id="context" class="context"></div>
  <section class="grid">
    <article class="panel"><h3>OBSERVED</h3><div id="observed"></div><p class="caption">Measurements available by the selected decision day.</p></article>
    <article class="panel"><h3>PREDICTED</h3><div id="predicted"></div><div id="badge" class="badge"></div></article>
    <article class="panel"><h3>HYPOTHESIS</h3><div id="hypothesis"></div><p id="hypothesis-note" class="caption"></p></article>
  </section>
  <section id="reveal-panel" class="reveal" hidden><h3>OBSERVED · DIV12 REVEAL</h3><div id="revealed"></div></section>
  <footer><strong>Research decision support only.</strong> Not an autonomous assay-termination system. Prospective validation is required before laboratory deployment. Training data are rat cortical MEA assays, not organ-on-chip experiments.<br><span id="count"></span></footer>
</main>
<script>
const rows=__DATA__;
const endpointOrder=["meanfiringrate","nAE","r"];
const labels={meanfiringrate:"Mean firing rate",nAE:"Active electrodes",r:"Coordinated activity (r)"};
const byId=id=>document.getElementById(id); const fmt=x=>Number.isFinite(Number(x))?Number(x).toFixed(2):"—";
function unique(values){return [...new Set(values)]}
function setOptions(el,values,label=v=>v){el.innerHTML="";values.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=label(v);el.appendChild(o)})}
function table(headers,body){return `<table><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${body.map(r=>`<tr>${r.map(v=>`<td>${v}</td>`).join("")}</tr>`).join("")}</tbody></table>`}
const chemicals=unique(rows.map(r=>`${r.casrn}|${r.trt}`)).sort((a,b)=>a.split("|")[1].localeCompare(b.split("|")[1]));
setOptions(byId("chemical"),chemicals,v=>`${v.split("|")[1]} · ${v.split("|")[0]}`);
function chemicalRows(){return rows.filter(r=>r.casrn===byId("chemical").value.split("|")[0])}
function updateDose(){setOptions(byId("dose"),unique(chemicalRows().map(r=>r.dose)).sort((a,b)=>a-b));updateWell()}
function updateWell(){const dose=Number(byId("dose").value);setOptions(byId("well"),unique(chemicalRows().filter(r=>Number(r.dose)===dose).map(r=>r.sample_id)).sort());render()}
function render(){
  const selected=rows.filter(r=>r.sample_id===byId("well").value).sort((a,b)=>endpointOrder.indexOf(a.endpoint)-endpointOrder.indexOf(b.endpoint)); if(!selected.length)return;
  const d9=byId("div9").checked; byId("context").textContent=`Unseen during training · ${selected[0].cohort} cohort · dose ${selected[0].dose} · deterministic non-cherry-picked subset`;
  const oh=["Endpoint","DIV5","DIV7"].concat(d9?["DIV9"]:[]); const ob=selected.map(r=>[labels[r.endpoint],fmt(r.observed_div5),fmt(r.observed_div7)].concat(d9?[fmt(r.observed_div9)]:[]));byId("observed").innerHTML=table(oh,ob);
  const pb=selected.map(r=>[labels[r.endpoint],fmt(d9?r.day9_prediction:r.prediction),fmt(d9?r.day9_lower:r.uncertainty_lower),fmt(d9?r.day9_upper:r.uncertainty_upper)]);byId("predicted").innerHTML=table(["Endpoint","DIV12 forecast","90% low","90% high"],pb);
  const verdict=d9?"DIV9 RETROSPECTIVE FORECAST":(selected.every(r=>r.verdict==="EARLY DECISION POSSIBLE")?"EARLY DECISION POSSIBLE":"CONTINUE TO DIV12");byId("badge").textContent=verdict;byId("badge").className="badge"+(verdict.includes("CONTINUE")?" wait":"");
  if(d9){const hb=selected.map(r=>[labels[r.endpoint],fmt(r.uncertainty_upper-r.uncertainty_lower),fmt(r.day9_upper-r.day9_lower)]);byId("hypothesis").innerHTML=table(["Endpoint","DIV7 width","DIV9 width"],hb);byId("hypothesis-note").textContent="Retrospective scenario: added DIV9 evidence, not a prospective deployment claim."}
  else{const hb=selected.map(r=>[labels[r.endpoint],fmt(r.bt_plus_plus_prediction)]);byId("hypothesis").innerHTML=table(["Endpoint","BT++ forecast"],hb);byId("hypothesis-note").textContent="Strongest dose-informed comparator chosen without outer-test labels."}
  byId("reveal-panel").hidden=!byId("reveal").checked;byId("revealed").innerHTML=table(["Endpoint","Observed DIV12"],selected.map(r=>[labels[r.endpoint],fmt(r.target12)]));
}
byId("chemical").addEventListener("change",updateDose);byId("dose").addEventListener("change",updateWell);byId("well").addEventListener("change",render);byId("div9").addEventListener("change",render);byId("reveal").addEventListener("change",render);
byId("count").textContent=` ${unique(rows.map(r=>r.sample_id)).length} held-out wells are embedded from a deterministic cohort-balanced subset.`;updateDose();
</script>
</body></html>'''


def build(source: Path, output: Path, per_cohort: int) -> None:
    selected = select_rows(pd.read_csv(source), per_cohort=per_cohort)
    records = json.loads(selected.to_json(orient="records", double_precision=10))
    rendered = HTML.replace("__DATA__", json.dumps(records, separators=(",", ":")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {output} with {selected['sample_id'].nunique()} wells and {len(selected)} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the self-contained MEACompass static demo")
    parser.add_argument("--source", type=Path, default=Path("results/demo_predictions.csv"))
    parser.add_argument("--output", type=Path, default=Path("docs/demo/index.html"))
    parser.add_argument("--per-cohort", type=int, default=50)
    args = parser.parse_args()
    build(args.source, args.output, args.per_cohort)


if __name__ == "__main__":
    main()
