---
title: Effective Radiative Forcing from Future Emissions
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
const eta_co2 = 400e-6;  // mol/mol
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

// Assumed yearly emissons
const co2 = 10e9;  // kg CO2
const contrails = 6e9;  // kg CO2e (GWP50 basis)

```

<!-- Compute CO2 AGWP50 -->
```js
var agwp50 = 0.0;  // J/kg CO2
for (var t = 0; t <= 50; t++) {
   const m = a0 + a1*Math.exp(-t/t1) + a2*Math.exp(-t/t2) + a3*Math.exp(-t/t3);
   const c = m / mass_atmosphere * m_air / m_co2;
   const rf = 5.35 * c / eta_co2;
   agwp50 += rf * surface_area_earth * seconds_per_year;
}

```

<!-- Convert contrail CO2e to radiative forcing -->
```js
const contrail_erf = 1e3 * contrails * agwp50 / surface_area_earth / seconds_per_year;

```

<!-- Generate scenario -->
```js
var data_co2 = [];
var data_contrail = [];
var data_total = [];

// assume emissions rates remain constant for 50 years
for (var t = 0; t <= 50; t++) {
   
   // compute current CO2 radiative forcing
   // need to include emissions from year 0 to present
   var m = 0.0;
   for (var dt = t; dt >= 0; dt--) {
      m += co2 * (a0 + a1*Math.exp(-dt/t1) + a2*Math.exp(-dt/t2) + a3*Math.exp(-dt/t3));      
   }
   const c = m / mass_atmosphere * m_air / m_co2;
   const erf = 5350.0 * c / eta_co2;
   data_co2.push({"t": 2025 + t, "erf": erf});

   // for short-lived contrails, constant emissions rate means constant ERF
   data_contrail.push({"t": 2025 + t, "erf": contrail_erf});
   data_total.push({"t": 2025 + t, "erf": erf + contrail_erf});
}

const ilabel = 10;
const labels = [
    {"label": "Total", "t": data_total[ilabel].t, "erf": data_total[ilabel].erf},
    {"label": "Contrails", "t": data_contrail[ilabel].t, "erf": data_contrail[ilabel].erf},
    {"label": "CO2", "t": data_co2[ilabel].t, "erf": data_co2[ilabel].erf},
]

```

<!-- Plot -->
```js
Plot.plot({
    width: Math.min(width, 460),
    height: 400/460*Math.min(width, 460),
    style: "display: block; margin: auto",
    x: {
        label: null,
        tickFormat: "d",
        line: true
    },
    y: {
        label: "Effective radiative forcing (mW/m²)",
        domain: [0, 0.9],
        line: true
    },
    marks: [
        Plot.line(data_total, {x: "t", y: "erf", stroke: "black"}),
        Plot.line(data_contrail, {x: "t", y: "erf", stroke: "black", strokeDasharray: "35,10"}),
        Plot.line(data_co2, {x: "t", y: "erf", stroke: "black", strokeDasharray: "5,5"}),
        Plot.text(labels, {x: "t", y: "erf", text: "label", dy: 10, textAnchor: "start"}),
        Plot.ruleX(data_total, Plot.pointerX({x: "t", py: "erf", stroke: "lightgray"})),
        Plot.dot(data_total, Plot.pointerX({x: "t", y: "erf", fill: "black"})),
        Plot.dot(data_contrail, Plot.pointerX({x: "t", y: "erf", fill: "black"})),
        Plot.dot(data_co2, Plot.pointerX({x: "t", y: "erf", fill: "black"})),
        Plot.text(data_contrail, Plot.pointerX({px: "t", py: "erf", frameAnchor: "top-right", dy: -16.5, text: (d) => {
            const year = d.t;
            const erf_contrail = d.erf;
            const erf_co2 = data_co2.find(d => d.t === year).erf;
            if (erf_contrail > erf_co2) {
                return `${year}: contrail ERF is ${(erf_contrail/erf_co2).toFixed(1)}x CO2 ERF`;
            } else {
                return `${year}: contrail ERF is ${(100*erf_contrail/erf_co2).toFixed(0)}% of CO2 ERF`;
            }
        }}))
    ]   
})

```

<div style="max-width: 460px; margin: auto" class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/erf-from-future-emissions/index.md)

</div>
