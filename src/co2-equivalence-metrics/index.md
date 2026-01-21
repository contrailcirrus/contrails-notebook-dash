---
title: Dashboard Template
---

<!-- Imports -->
```js
import "../components/observer.js";

```

<!-- Custom styles -->
<style>
    body {
        /* Ghost post max-width */
        max-width: 1000px;
    }

    .subplot-cols-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }

    @media (max-width: 1000px) {
        .subplot-cols-2 {
            display: block;
        }

        .subplot {
            margin-bottom: 10px;
        }
    }
</style>

<!-- Constant inputs -->
```js
// constants
const seconds_per_year = 31557600; // s
const mass_atmosphere = 5.1352e18; // kg 
const m_co2 = 44.01; // g/mol
const m_air = 28.97; // g/mol
const eta_co2 = 400e-6;  // mol/mol
const surface_area_earth = 510072000000000.0; // m2

// Contrail EF (aka AGWP)
// Approximately equal to EF from 1 year of flights
const agwp_contrail = 50e-3 * surface_area_earth * seconds_per_year;

// CO2 impulse response function coefficients
// https://doi.org/10.5194/acp-13-2793-2013
const a0 = 0.2174; // nondim
const a1 = 0.2240; // nondim
const a2 = 0.2824; // nondim
const a3 = 0.2763; // nomdim
const t1 = 394.4; // yr
const t2 = 36.54; // yr
const t3 = 4.304; // yr

// Temperature impulse response function coefficients
//  https://doi.org/10.1016/j.enpol.2007.08.039
const c1 = 0.631; // K/(W/m2)
const c2 = 0.429; // K/(W/m2)
const d1 = 8.4;   // yr
const d2 = 409.5; // yr

```

<!-- User inputs -->
```js
// Equivalence metric (GWP or GTP)
const metric_input = Inputs.radio(["GWP", "GTP"], {value: "GWP"});
const metric = Generators.input(metric_input);

// Metric time horizon (years)
const horizon_input = Inputs.range([5, 200], {step: 1, value: 100, transform: Math.sqrt});
const horizon = Generators.input(horizon_input);

```

<!-- Compute contrail AGTP -->
```js
const agtp_contrail = agwp_contrail / (surface_area_earth * seconds_per_year) * (
    c1 / d1 * Math.exp(-horizon / d1) +
    c2 / d2 * Math.exp(-horizon / d2)
);

```

<!-- Compute temperature change from contrail -->
```js
var t_contrail = [];
for (var t = 0; t < 200; t++) {
    const dT = agwp_contrail / (surface_area_earth * seconds_per_year) * (
        c1 / d1 * Math.exp(-t / d1) +
        c2 / d2 * Math.exp(-t / d2)
    );
    t_contrail.push({"t": t, "dT": dT});
}

```

<!-- Compute AGWP for 1 kg CO2 -->
```js
const agwp_kg_co2 = 5.35 * seconds_per_year * surface_area_earth * (
    a0 * horizon +
    a1 * t1 * (1.0 - Math.exp(-horizon/t1)) +
    a2 * t2 * (1.0 - Math.exp(-horizon/t2)) +
    a3 * t3 * (1.0 - Math.exp(-horizon/t3))
) / (eta_co2 * mass_atmosphere); // J/kg

```

<!-- Compute AGTP for 1 kg CO2 -->
```js
const rf0_kg = 5.35 / (eta_co2 * mass_atmosphere);
const agtp_kg_co2 = rf0_kg * (
    a0 * c1 * (1.0 - Math.exp(-horizon/d1)) +
    a0 * c2 * (1.0 - Math.exp(-horizon/d2)) +
    a1 * c1 * t1 / (t1 - d1) * (
        Math.exp(-(t1 + d1) * horizon / (t1 * d1)) - Math.exp(-horizon / d1)
    ) +
    a1 * c2 * t1 / (t1 - d2) * (
        Math.exp(-(t1 + d2) * horizon / (t1 * d2)) - Math.exp(-horizon / d2)
    ) +
    a2 * c1 * t2 / (t2 - d1) * (
        Math.exp(-(t2 + d1) * horizon / (t2 * d1)) - Math.exp(-horizon / d1)
    ) +
    a2 * c2 * t2 / (t2 - d2) * (
        Math.exp(-(t2 + d2) * horizon / (t2 * d2)) - Math.exp(-horizon / d2)
    ) +
    a3 * c1 * t3 / (t3 - d1) * (
        Math.exp(-(t3 + d1) * horizon / (t3 * d1)) - Math.exp(-horizon / d1)
    ) +
    a3 * c2 * t3 / (t3 - d2) * (
        Math.exp(-(t3 + d2) * horizon / (t3 * d2)) - Math.exp(-horizon / d2)
    )
)

```

<!-- Compute CO2 equivalent -->
```js
const co2e = metric == "GWP" ? agwp_contrail / agwp_kg_co2 : agtp_contrail / agtp_kg_co2;
const rf0 = 5.35 * co2e / (eta_co2 * mass_atmosphere);

```

<!-- Compute radiative forcing from CO2 equivalent -->
```js
var rf_co2 = [];
for (var t = 0; t <= 200; t++) {
    const rf = rf0 * (
        a0 +
        a1 * Math.exp(-t/t1) +
        a2 * Math.exp(-t/t2) +
        a3 * Math.exp(-t/t3)
    ); // W/m2
    rf_co2.push({"t": t, "rf": rf});
}

```

<!-- Compute temperature change from CO2 equivalent -->
```js
var t_co2 = [];
for (var t = 0; t <= 200; t++) {
    const dT = rf0 * (
        a0 * c1 * (1.0 - Math.exp(-t/d1)) +
        a0 * c2 * (1.0 - Math.exp(-t/d2)) +
        a1 * c1 * t1 / (t1 - d1) * (Math.exp(-(t1 + d1) * t / (t1 * d1)) - Math.exp(-t / d1)) +
        a1 * c2 * t1 / (t1 - d2) * (Math.exp(-(t1 + d2) * t / (t1 * d2)) - Math.exp(-t / d2)) +
        a2 * c1 * t2 / (t2 - d1) * (Math.exp(-(t2 + d1) * t / (t2 * d1)) - Math.exp(-t / d1)) +
        a2 * c2 * t2 / (t2 - d2) * (Math.exp(-(t2 + d2) * t / (t2 * d2)) - Math.exp(-t / d2)) +
        a3 * c1 * t3 / (t3 - d1) * (Math.exp(-(t3 + d1) * t / (t3 * d1)) - Math.exp(-t / d1)) +
        a3 * c2 * t3 / (t3 - d2) * (Math.exp(-(t3 + d2) * t / (t3 * d2)) - Math.exp(-t / d2))
    )
    t_co2.push({"t": t, "dT": dT})
}
// for labeling in plot
const ilab = t_co2.findLastIndex((elem) => elem.dT < 20e-9);

```

<!-- Plot RF -->
```js
const rf_ax = Plot.plot({
    width: 450,
    height: 400,
    className: "plot",
    x: {
        label: "Time (years)",
        line: true
    },
    y: {
        label: "Effective radiative forcing (mW/m²)",
        line: true,
        domain: [0, 1e3 * rf0 * (1.0 + (25e9 / co2e)**0.5)]
    },
    marks: [
        Plot.areaY(
            rf_co2,
            {
                filter: (d) => d.t <= horizon,
                x: (d) => d.t,
                y: (d) => d.rf * 1e3,
                fill: metric == "GWP" ? "var(--theme-blue, blue)" : "gray",
            },
        ),
        Plot.line(
            rf_co2,
            {
                x: (d) => d.t,
                y: (d) => d.rf * 1e3,
                strokeDasharray: "10,5"
            }
        ),
        Plot.text(
            [`CO2: ${(co2e * agwp_kg_co2 / 1e21).toFixed(2)} ZJ over ${horizon} yr`],
            {
                x: horizon > 70 ? horizon - 5 : horizon + 5,
                y: rf0 * 1e3 / 5,
                fill: horizon > 70 ? "white" : metric == "GWP" ? "var(--theme-blue, blue)" : "gray",
                textAnchor: horizon > 70 ? "end" : "start",
            }
        ),
        Plot.text(
            [`Contrail EF: ${(agwp_contrail / 1e21).toFixed(2)} ZJ\n(50 mW/m² over 1 year)`],
            {
                frameAnchor: "top-right",
                dx: -5,
                dy: 5,
                fill: metric == "GWP" ? "var(--theme-blue, blue)" : "gray",
            }
        ),
        Plot.text(
            ["CO2"],
            {
                x: rf_co2.at(-1).t,
                y: rf_co2.at(-1).rf * 1.1e3,
                textAnchor: "end"
            }
        )
    ]
});

```
<!-- Plot temperature response -->
```js
const temp_ax = Plot.plot({
    width: 450,
    height: 400,
    className: "plot",
    x: {
        label: "Time (years)",
        line: true
    },
    y: {
        type: "log",
        label: "Warming (mK)",
        line: true,
        domain: [0.01, 20],
        tickFormat: "f",
    },
    marks: [
        Plot.line(
            t_contrail,
            {x: (d) => d.t, y: (d) => d.dT * 1e3, clip: true}
        ),
        Plot.line(
            t_co2,
            {
                x: (d) => d.t,
                y: (d) => d.dT * 1e3,
                strokeDasharray: "10,5",
                clip: true
            }
        ),
        Plot.dot(
            [[horizon, agtp_contrail * 1e3]],
            {stroke: null, fill: metric == "GTP" ? "var(--theme-blue, blue)" : "gray"}
        ),
        Plot.dot(
            [[horizon, co2e * agtp_kg_co2 * 1e3]],
            {stroke: null, fill: metric == "GTP" ? "var(--theme-blue, blue)" : "gray"}
        ),
        Plot.ruleX([horizon], {stroke: metric == "GTP" ? "var(--theme-blue, blue)" : "gray"}),
        Plot.text(
            [
                `Contrails: ${(agtp_contrail * 1e3).toFixed(2)} mK after ${horizon} yr\n` +
                `CO2: ${(co2e * agtp_kg_co2 * 1e3).toFixed(2)} mK after ${horizon} yr`
            ],
            {
                x: horizon > 100 ? horizon - 5 : horizon + 5,
                y: 16,
                textAnchor: horizon > 100 ? "end" : "start",
                fill: metric == "GTP" ? "var(--theme-blue, blue)" : "gray"
            }
        ),
        Plot.text(
            ["Contrails"],
            {
                x: 200,
                y: 0.8e3 * t_contrail.at(-1).dT,
                textAnchor: "end",
            }
        ),
        Plot.text(
            ["CO2"],
            {
                x: t_co2.at(-1).t,
                y: t_co2.at(-1).dT > 0.2e-3 ? 0.8e3 * t_co2.at(-1).dT : 1.2e3 * t_co2.at(-1).dT,
                filter: t_co2.at(-1).dT < 20,
                textAnchor: "end"
            }
        )
    ]
});

```

<!-- Order axes based on layout and selected metric -->
```js
const first_ax = window.matchMedia('(max-width: 1000px)').matches && metric == "GTP" ? temp_ax : rf_ax;
const second_ax = window.matchMedia('(max-width: 1000px)').matches && metric == "GTP" ? rf_ax : temp_ax;

```

This tool is a work in progress. Results have not been carefully checked for accuracy!

<div class="grid grid-cols-3">
<div class="card">

## Equivalence Metric
${metric_input}
</div>
<div class="card">

## Time Horizon (years)
${horizon_input}
</div>

<div class="card">

## Contrail CO2e
<span class="big">${co2e > 1e12 ? `${Math.round(co2e / 1e10) / 1e2} Gt` : `${Math.round(co2e / 1e9)} Mt`}</span>
</div>
</div>

<div class="subplot-cols-2">
<div class="subplot">
${first_ax}
</div>

<div class="subplot">
${second_ax}
</div>
</div>
