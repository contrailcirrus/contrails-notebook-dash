---
title: Effective Radiative Forcing during 2019
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

// aviation co2 emissions from 1940 to 2019
// https://doi.org/10.1016/j.atmosenv.2020.117834
const co2_emissions = [
    32.5000000, 34.2814793, 33.9726505, 39.9257766, 39.6408036,
    45.5880779, 48.1252731, 50.4016524, 56.6261656, 62.2304961,
    67.9159151, 74.2010822, 79.2904032, 84.7713645, 90.6131811,
    98.9976544, 107.612237, 115.946262, 124.591923, 136.646849,
    147.164180, 158.656236, 175.484227, 187.227091, 192.449060,
    208.041776, 223.557273, 258.770197, 297.084093, 317.137158,
    322.767652, 327.916983, 342.503219, 357.632377, 356.685143,
    351.098911, 351.079967, 363.481135, 379.280079, 393.396577,
    402.048238, 401.043075, 396.250388, 404.588752, 421.631095,
    441.374296, 461.264582, 485.706806, 506.481662, 527.568545,
    543.607194, 539.476551, 526.645753, 532.515888, 540.450698,
    561.788368, 580.101204, 603.037822, 619.876812, 632.365391,
    656.491457, 674.216223, 656.853719, 656.875329, 667.693721,
    704.925343, 733.098481, 744.810293, 758.830179, 752.543398,
    727.621470, 758.508691, 781.350921, 789.926845, 812.138904,
    840.942589, 882.764005, 927.975627, 981.669938, 1020.00000
] // Mt/yr

```

<!-- Radiative forcing from 2019 and pre-2019 emissions -->
```js
// Sum contributions to 2019 airborne CO2 from 1940-2018 emissions
var m_pre = 0.0
for (var t = 1940; t <= 2018; t++) {
    const i = t - 1940;
    const tp = 2019 - t;
    m_pre += 1e9 * co2_emissions[i] * (a0 + a1*Math.exp(-tp/t1) + a2*Math.exp(-tp/t2) + a3*Math.exp(-tp/t3));
}

// Compute radiative forcing
const c_pre = m_pre / mass_atmosphere * m_air / m_co2;
const rf_pre = 5350.0 * c_pre / eta_co2;
const m_2019 = 1e9 * co2_emissions[2019 - 1940];
const c_2019 = m_2019 / mass_atmosphere * m_air / m_co2;
const rf_2019 = 5350.0 * c_2019 / eta_co2;

// Assemble data for plotting
const data = [
    {species: "CO₂", source: "pre-2019 flights", "erf": rf_pre},
    {species: "CO₂", source: "2019 flights", "erf": rf_2019},
    {species: "Contrails", source: "pre-2019 flights", "erf": 0.0},
    {species: "Contrails", source: "2019 flights", "erf": contrail_erf},
];

console.log(Plot.stackY(data, {x: "species", y: "erf"}).x)

```

<!-- Plot -->
```js
Plot.plot({
    color: {
        type: "categorical",
        range: ["black", "gray"],
    },
    x: {
        type: "band",
        padding: 0.4,
        label: null,
        line: true
    },
    y: {
        label: "2019 effective radiative forcing (mW/m²)",
        domain: [0, 35],
        line: true
    },
    marks: [
        Plot.barY(data, {x: "species", y: "erf", fill: "source"}),
        Plot.textY(
            data,
            Plot.stackY({filter: (d) => d.erf > 0, x: "species", y: "erf", text: "source", fill: "white"})
        )
    ]   
})

```

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/erf-during-2019/index.md)

</div>
