---
title: Contrail Avoidance Efficacy
---

<style>
  body {
    max-width: 1150px;
  }
</style>

```js
import "../@components/observer.js";
```

```js
const PRESETS = {
  "Pre-tactical Vertical": {
    eta_optim: 0.82, eta_constraints: 0.82, eta_integration: 0.97,
    eta_selection: 0.78, eta_avoidance_traj: 0.97, eta_operational: 0.97,
    eta_dispatch: 0.61, eta_crew: 0.90,
  },
  "Pre-tactical 3D": {
    eta_optim: 0.82, eta_constraints: 0.90, eta_integration: 0.97,
    eta_selection: 0.78, eta_avoidance_traj: 0.97, eta_operational: 0.97,
    eta_dispatch: 0.61, eta_crew: 0.90,
  },
  "Tactical Vertical": {
    eta_optim: 0.82, eta_constraints: 0.82, eta_integration: 1.00,
    eta_selection: 0.90, eta_avoidance_traj: 0.97, eta_operational: 0.80,
    eta_dispatch: 1.00, eta_crew: 0.40,
  },
  "Tactical 3D": {
    eta_optim: 0.82, eta_constraints: 0.90, eta_integration: 1.00,
    eta_selection: 0.90, eta_avoidance_traj: 0.97, eta_operational: 0.80,
    eta_dispatch: 1.00, eta_crew: 0.30,
  },
};
```

```js
const presetInput = Inputs.select(Object.keys(PRESETS), {label: "Preset scenario"});
const preset = Generators.input(presetInput);
```

```js
// System-level — reset to preset values when preset changes
const etaDispatchInput = Inputs.range([0, 1], {
  value: PRESETS[preset].eta_dispatch, step: 0.01, label: "η_acceptance_dispatch",
});
const eta_dispatch = Generators.input(etaDispatchInput);

const etaCrewInput = Inputs.range([0, 1], {
  value: PRESETS[preset].eta_crew, step: 0.01, label: "η_acceptance_crew",
});
const eta_crew = Generators.input(etaCrewInput);
```

```js
// Reference inputs (fixed across presets)
const nFlightsInput = Inputs.range([50, 10000], {value: 500, step: 50, label: "Recommendations sent"});
const n_flights = Generators.input(nFlightsInput);

const co2eqInput = Inputs.range([0.1, 500], {
  value: 8.0, step: 0.5, label: "Avg contrail impact / treated flight (t CO₂eq)",
});
const co2eq_per_flight = Generators.input(co2eqInput);
```

```js
// Per-flight efficiencies — reset to preset values when preset changes
const etaOptimInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_optim, step: 0.01, label: "η_optim"});
const eta_optim = Generators.input(etaOptimInput);

const etaConstraintsInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_constraints, step: 0.01, label: "η_constraints"});
const eta_constraints = Generators.input(etaConstraintsInput);

const etaIntegrationInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_integration, step: 0.01, label: "η_integration"});
const eta_integration = Generators.input(etaIntegrationInput);

const etaSelectionInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_selection, step: 0.01, label: "η_selection"});
const eta_selection = Generators.input(etaSelectionInput);

const etaTrajInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_avoidance_traj, step: 0.01, label: "η_avoidance_traj"});
const eta_avoidance_traj = Generators.input(etaTrajInput);

const etaOperationalInput = Inputs.range([0, 1], {value: PRESETS[preset].eta_operational, step: 0.01, label: "η_operational"});
const eta_operational = Generators.input(etaOperationalInput);
```

```js
const eta_per_flight   = eta_optim * eta_constraints * eta_integration * eta_selection * eta_avoidance_traj * eta_operational;
const eta_system       = eta_per_flight * eta_dispatch * eta_crew;
const n_rerouted       = Math.round(n_flights * eta_dispatch * eta_crew);
const total_impact     = n_rerouted * co2eq_per_flight;
const total_mitigation = total_impact * eta_per_flight;
const max_mitigation   = eta_optim * eta_constraints;
```

```js
// System cascade chart (3-bar)
const cascadeData = [
  {x: "Sent",     value: 100,                            color: "#4a6fc8"},
  {x: "Dispatch", value: eta_dispatch * 100,             color: "#2042a0"},
  {x: "Rerouted", value: eta_dispatch * eta_crew * 100, color: "#162e70"},
];

const systemChart = Plot.plot({
  title: "System View — Acceptance Cascade",
  width: Math.floor(width * 0.70) - 48,
  height: 280,
  marginBottom: 40,
  x: {domain: ["Sent", "Dispatch", "Rerouted"], label: null, tickSize: 0, padding: 0.3},
  y: {domain: [0, 125], label: "% of recommendations"},
  marks: [
    Plot.barY(cascadeData, {x: "x", y: "value", fill: "color", stroke: "#222", strokeWidth: 0.5}),
    Plot.text(cascadeData, {
      x: "x",
      y: d => d.value / 2,
      text: d => `${d.value.toFixed(0)}%`,
      fill: "white", fontWeight: "bold", fontSize: 13,
    }),
  ],
  style: {fontSize: "11px"},
});
```

```js
// Flight waterfall chart (7-bar)
const intended_pct     = eta_optim * eta_constraints * 100;
const integration_loss = intended_pct * (1 - eta_integration);
const selection_loss   = intended_pct * eta_integration * (1 - eta_selection);
const traj_loss        = intended_pct * eta_integration * eta_selection * (1 - eta_avoidance_traj);
const oper_loss        = intended_pct * eta_integration * eta_selection * eta_avoidance_traj * (1 - eta_operational);
const final_pct        = intended_pct * eta_integration * eta_selection * eta_avoidance_traj * eta_operational;

const wfCats    = ["Initial", "Intended", "Integ. Loss", "Select. Loss", "Traj. Loss", "Oper. Loss", "Final"];
const wfHeights = [100, intended_pct, integration_loss, selection_loss, traj_loss, oper_loss, final_pct];
const wfBottoms = [
  0, 0,
  intended_pct - integration_loss,
  intended_pct - integration_loss - selection_loss,
  intended_pct - integration_loss - selection_loss - traj_loss,
  intended_pct - integration_loss - selection_loss - traj_loss - oper_loss,
  0,
];
const wfColors = ["#4a6fc8", "#2042a0", "#aac2e8", "#93b0e0", "#7a9dd4", "#c2d3f0", "#162e70"];
const wfSigns  = ["", "+", "−", "−", "−", "−", ""];

const waterfallData = wfCats.map((cat, i) => ({
  x: cat,
  y1: wfBottoms[i],
  y2: wfBottoms[i] + wfHeights[i],
  h: wfHeights[i],
  color: wfColors[i],
  label: wfHeights[i] >= 1.5
    ? `${wfSigns[i]}${wfHeights[i].toFixed(1)}%\n${(wfHeights[i] / 100 * co2eq_per_flight).toFixed(1)} t`
    : "",
}));

// Weather loss = selection + avoidance trajectory losses combined
const weather_top = intended_pct - integration_loss;
const weather_bot = intended_pct - integration_loss - selection_loss - traj_loss;

// Horizontal connector lines at the "remaining" level between loss bars
const connectorLines = [];
const connectorPairs = [
  {x1: "Intended",     x2: "Integ. Loss",  y: intended_pct},
  {x1: "Integ. Loss",  x2: "Select. Loss", y: intended_pct - integration_loss},
  {x1: "Select. Loss", x2: "Traj. Loss",   y: intended_pct - integration_loss - selection_loss},
  {x1: "Traj. Loss",   x2: "Oper. Loss",   y: intended_pct - integration_loss - selection_loss - traj_loss},
];
for (const c of connectorPairs) {
  connectorLines.push({x: c.x1, y: c.y});
  connectorLines.push({x: c.x2, y: c.y});
  connectorLines.push({x: null, y: null});
}

const waterfallChart = Plot.plot({
  title: "Flight View — Mitigation Efficiency Cascade",
  width: Math.floor(width * 0.70) - 48,
  height: 360,
  marginBottom: 65,
  x: {domain: wfCats, label: null, tickSize: 0, padding: 0.2, tickRotate: -20},
  y: {domain: [-3, 135], label: "Impact (% of initial OFP contrail forcing)"},
  marks: [
    // Weather loss grouping box — render transform gives access to live D3 scales
    Plot.barY([{x: "Select. Loss", y1: weather_bot, y2: weather_top}], {
      x: "x", y1: "y1", y2: "y2",
      render(index, scales, values, dimensions, context) {
        const {x, y} = scales;
        const bw = x.bandwidth?.() ?? 0;
        const x1px = x("Select. Loss");
        const x2px = x("Traj. Loss") + bw;
        const y1px = y(weather_top);
        const y2px = y(weather_bot);
        const ns = "http://www.w3.org/2000/svg";
        const doc = context.document;
        const g = doc.createElementNS(ns, "g");
        const rect = doc.createElementNS(ns, "rect");
        rect.setAttribute("x", Math.min(x1px, x2px));
        rect.setAttribute("y", Math.min(y1px, y2px));
        rect.setAttribute("width", Math.abs(x2px - x1px));
        rect.setAttribute("height", Math.abs(y2px - y1px));
        rect.setAttribute("fill", "#dae3f8");
        rect.setAttribute("stroke", "#2042a0");
        rect.setAttribute("stroke-width", "1.5");
        rect.setAttribute("stroke-dasharray", "4,2");
        rect.setAttribute("opacity", "0.35");
        g.appendChild(rect);
        const label = doc.createElementNS(ns, "text");
        label.setAttribute("x", (x1px + x2px) / 2);
        label.setAttribute("y", Math.min(y1px, y2px) - 4);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("font-size", "9");
        label.setAttribute("fill", "#2042a0");
        label.setAttribute("font-style", "italic");
        label.setAttribute("font-weight", "bold");
        label.textContent = "← Weather Loss →";
        g.appendChild(label);
        return g;
      },
    }),
    Plot.barY(waterfallData, {
      x: "x", y1: "y1", y2: "y2",
      fill: "color", stroke: "#222", strokeWidth: 1, opacity: 0.85,
    }),
    Plot.text(waterfallData.filter(d => d.label), {
      x: "x",
      y: d => (d.y1 + d.y2) / 2,
      text: "label",
      fill: "white", fontWeight: "bold", fontSize: 9,
    }),
    Plot.ruleY([100], {stroke: "gray", strokeOpacity: 0.3, strokeWidth: 0.8}),
    Plot.line(connectorLines, {x: "x", y: "y", stroke: "#555", strokeDasharray: "4,2", strokeOpacity: 0.6}),
  ],
  style: {fontSize: "11px"},
});
```

# Contrail Avoidance Efficacy

<!-- Row 1: main inputs (left) | efficiency metrics + both charts (right) -->
<div style="display: grid; grid-template-columns: 30fr 70fr; grid-auto-rows: auto; gap: 1rem;">
<div>

### Inputs

<div class="card">

## Preset

${presetInput}

<h2 style="margin-bottom:1em;">System-level efficiencies</h2>

<div style="margin-bottom:1.6em;">${etaDispatchInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Fraction of recommended reroutes that dispatch accepts and forwards to crew.</div></div>

<div style="margin-bottom:1.6em;">${etaCrewInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Fraction of dispatch-approved reroutes that the crew actually flies.</div></div>

<h2 style="margin-bottom:1em;">Per-flight efficiencies</h2>

<div style="margin-bottom:1.6em;">${etaOptimInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Holistic optimisation — contrails are not avoided at all costs; trade-offs with fuel, time, and other objectives reduce achievable mitigation.</div></div>

<div style="margin-bottom:1.6em;">${etaConstraintsInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Operational constraints — e.g. vertical rerouting only, maximum altitude deviations, airspace restrictions.</div></div>

<div style="margin-bottom:1.6em;">${etaIntegrationInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Translating a climate-optimal trajectory into a released flight plan (FPL format, ATC filing constraints…).</div></div>

<div style="margin-bottom:1.6em;">${etaSelectionInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Flight selection using a forecast issued at an earlier reference time than available in hindsight — non-optimal flights may be treated while beneficial ones are missed.</div></div>

<div style="margin-bottom:1.6em;">${etaTrajInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Avoidance trajectory computed with the operational forecast reference time rather than the latest available.</div></div>

<div>${etaOperationalInput}<div class="muted" style="font-size:0.78em;margin-top:0.5em;">Aircraft does not follow the flight plan exactly — lateral deviations, early departures, delays.</div></div>

</div>

</div>
<div>

### Outputs

<div class="card">

<div class="grid grid-cols-3" style="grid-auto-rows: auto; gap: 0.75rem;">

<div>
<div class="muted">η per-flight</div>
<span class="big">${(eta_per_flight * 100).toFixed(1)}%</span>
</div>

<div>
<div class="muted">η system</div>
<span class="big">${(eta_system * 100).toFixed(1)}%</span>
</div>

<div>
<div class="muted">Max mitigation potential</div>
<span class="big">${(max_mitigation * 100).toFixed(1)}%</span>
</div>

</div>

</div>

<div class="card">

${systemChart}

</div>

<div class="card">

${waterfallChart}

</div>

</div>

<!-- Row 2: reference inputs (left) | mitigation totals (right) -->
<div>

<div class="card">

## Reference inputs

${nFlightsInput}

${co2eqInput}

</div>

</div>
<div>

<div class="card">

<div class="grid grid-cols-3" style="grid-auto-rows: auto; gap: 0.75rem;">

<div>
<div class="muted">Total mitigation</div>
<span class="big">${total_mitigation.toLocaleString("en-US", {maximumFractionDigits: 0})}</span><br/>
<span class="muted">t CO₂eq</span>
</div>

<div>
<div class="muted">Total impact</div>
<span class="big">${total_impact.toLocaleString("en-US", {maximumFractionDigits: 0})}</span><br/>
<span class="muted">t CO₂eq</span>
</div>

<div>
<div class="muted">Flights rerouted</div>
<span class="big">${n_rerouted.toLocaleString("en-US")}</span><br/>
<span class="muted">of ${n_flights.toLocaleString("en-US")}</span>
</div>

</div>

</div>

</div>

</div>

<div class="card">

${tex.block`\eta_{\text{per-flight}} = \eta_{\text{optim}} \times \eta_{\text{constraints}} \times \eta_{\text{integration}} \times \eta_{\text{selection}} \times \eta_{\text{avoidance\_traj}} \times \eta_{\text{operational}}`}

${tex.block`\eta_{\text{system}} = \eta_{\text{per-flight}} \times \eta_{\text{acceptance\_dispatch}} \times \eta_{\text{acceptance\_crew}}`}

</div>
