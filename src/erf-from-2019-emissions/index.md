---
title: Effective Radiative Forcing from 2019 Aviation Emissions
---

<!-- Imports -->
```js
import "../components/observer.js";

```

<!-- Inputs -->
```js
// constants
const seconds_per_year = 31557600; // s
const mass_atmosphere = 5.1352e18; // kg 
const m_co2 = 44.01; // g/mol
const m_air = 28.97; // g/mol
const eta_co2 = 420e-6;  // mol/mol
const surface_area_earth = 510072000000000.0; // m

// CO2 impulse response function coefficients
// https://doi.org/10.5194/acp-13-2793-2013
const a0 = 0.2174; // nondim
const a1 = 0.2240; // nondim
const a2 = 0.2824; // nondim
const a3 = 0.2763; // nomdim
const t1 = 394.4; // yr
const t2 = 36.54; // yr
const t3 = 4.304; // yr

// global/annual average contrail erf in 2019
// https://doi.org/10.5194/acp-24-6071-2024
const contrail_erf = 26.1    // mW m-2

// aviation co2 emissions in 2019
// https://doi.org/10.1016/j.atmosenv.2020.117834
const co2_emissions = 1020e9  // kg

```

<!-- Radiative forcing timeseries -->
```js
var co2 = [];
var contrails = [];

for (var t = 0; t <= 50; t++) {
   
   // set contrail radiative forcing
   // add two points in 2020 to capture sharp dropoff at end of 2019
   if (t <= 1) {
      contrails.push({"t": 2019 + t, "erf": contrail_erf});
   }
   if (t >= 1) {
      contrails.push({"t": 2019 + t, "erf": 0.0});
   }
   
   // calculate CO2 radiative forcing (mass -> concentration -> forcing)
   const m = co2_emissions * (a0 + a1*Math.exp(-t/t1) + a2*Math.exp(-t/t2) + a3*Math.exp(-t/t3));
   const c = m / mass_atmosphere * m_air / m_co2;
   const rf = 5350.0 * c / eta_co2;
   co2.push({"t": 2019 + t, "erf": rf});

}

```

<!-- Plot -->
```js
Plot.plot({
    x: {
        label: null,
        tickFormat: "" // format as 2019 rather than 2,019
    },
    y: {
        label: "Effective radiative forcing (mW/m²)",
        domain: [0, 28]
    },
    marks: [
        Plot.ruleY([0]),
        Plot.ruleX([2019]),
        Plot.areaY(contrails, {x: "t", y: "erf", fill: "black"}),
        Plot.text([[2021, 24.5]], {text: ["2019 contrails"], textAnchor: "start", fontWeight: "bold"}),
        Plot.text([[2021, 23.5]], {text: ["Large amount of short-lived warming"], textAnchor: "start"}),
        Plot.areaY(co2, {x: "t", y: "erf", fill: "gray"}),
        Plot.text([[2040, 3.0]], {text: ["2019 CO₂ emissions"], textAnchor: "start", fill: "gray", fontWeight: "bold"}),
        Plot.text([[2040, 2.0]], {text: ["Small amount of long-lived warming"], textAnchor: "start", fill: "gray"}),
    ]
})

```

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/erf-from-2019-emissions/index.md)

</div>
