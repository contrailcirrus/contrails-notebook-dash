---
title: Cost Explorer

---

<!-- Imports -->
```js
import "../components/observer.js";

import {DonutChart} from "../components/donutChart.js";
```

<!-- Inputs -->
```js
// constants
const AGWP100 = 8.8e-14 // yr W m-2 / kg-CO2 (Gaillot 2023)
const fuelIntensityCO2 = 3.89 // kg CO2 / kg fuel (Teoh 2024)
const contrailCirrusERF = 0.0574 // W m-2 (Lee 2021)
const fuelConsumption = 280 // Mtonnes fuel / year

// Mitigation efficacy (%)
const efficacyInput = Inputs.range([0, 100], { value: 50, step: 5 })
const efficacy = Generators.input(efficacyInput)

// Fuel penalty across fleet (%)
const fuelPenaltyInput = Inputs.range([0, 1], { value: 0.3, step: 0.05 })
const fuelPenalty = Generators.input(fuelPenaltyInput)

// Annual aviation fuel cost ($B / yr)
const fuelCostInput = Inputs.range([190, 300], { value: 260, step: 10 })
const fuelCost = Generators.input(fuelCostInput)

// R&D costs
const discountRate = 0.02  // 2%, assumed economic discount rate
const years = 20
const upfrontRDInput = Inputs.range([0, 500], { value: 100, step: 10})
const upfrontRD = Generators.input(upfrontRDInput)

// Annual monitoring infrastructure costs
const annualInfraInput = Inputs.range([0, 500], { value: 150, step: 10})
const annualInfra = Generators.input(annualInfraInput)
```

<!-- Model -->
```js
// Aviation fuel CO2 emission, including upstream CO2 (Mtonnes / yr)
const fuelCO2 = fuelConsumption * fuelIntensityCO2

// Contrail warming in CO2-eq, GWP100 (Mtonnes / yr)
const contrailWarming = contrailCirrusERF / AGWP100 / 1e3 / 1e6

// Contrail warming avoided in CO2-eq, GWP100 (Mtonnes / yr)
const contrailWarmingAvoided = ((efficacy / 100) * contrailWarming) - ((fuelPenalty / 100) * fuelCO2)

// Fuel costs ($M / yr)
const additionalFuelCost = (fuelPenalty / 100) * fuelCost * 1e3

// R&D costs ($M / yr)
const amortizedRDCost = upfrontRD * discountRate / (1 - (1 + discountRate)**(-years))

// Total annual ($M / yr)
const totalCost = additionalFuelCost + amortizedRDCost + annualInfra
```

<!-- Visuals -->
```js
const costPie = [
  {name: "Fuel", value: Math.round(100*(additionalFuelCost / totalCost)), format: (v) => `${v}%`, color: "#f26400"},
  {name: "R&D", value: Math.round(100*(amortizedRDCost / totalCost)), format: (v) => `${v}%`, color: "#162440"},
  {name: "Infrastructure", value: Math.round(100*(annualInfra / totalCost)), format: (v) => `${v}%`, color: "#1093ff"}
]
```

<noscript>
  <div class="note">
  See <a href="https://notebook.contrails.org/the-cost-of-contrail-management">web version of this post</a> for interactive cost explorer.
  </div>
</noscript>

<div class="card">

## Development cost

Upfront R&D Cost ($M) ${upfrontRDInput}

Annual Infrastructure Cost ($M / year) ${annualInfraInput}

Mitigation Efficacy (%) ${efficacyInput}

## Fuel cost

Fuel penalty (%) ${fuelPenaltyInput}

Aviation Fuel Cost ($B / year) ${fuelCostInput}

</div>


<div class="grid grid-cols-2">
  <div class="card">

## Warming avoided

<span class="big">${Math.round(contrailWarmingAvoided)}</span><br/>
<span class="muted">Mtonnes CO<sub>2-eq</sub> per year (GWP-100)</span>

## Annual cost

<span class="big">$${Math.round(totalCost).toLocaleString('en-US')} M</span><br/>
<span class="muted">per year</span>

## Abatement cost

<span class="big">$ ${((additionalFuelCost + amortizedRDCost + annualInfra) / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-100)</span>

  </div>
  <div class="card">

${DonutChart(costPie, {centerText: "Annual Cost", width: 300, colorDomain: costPie.map(c => c.name), colorRange: costPie.map(c => c.color)})}

  </div>
</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/cost-explorer/index.md)

</div>
