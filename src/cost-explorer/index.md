---
title: Cost Explorer
---

<!-- Imports -->
```js
import "../components/observer.js";

import {DonutChart} from "../components/donutChart.js";
```

<!-- Parse url inputs -->
```js
// parameters from URL ?param1=val1&param2=val2
const getParams = (defaults= {}, intParams = new Set([]), floatParams= new Set([])) => {

  // cast ints and floats
  const cast = (key, value) => {
    if (intParams.has(key)) return parseInt(value, 10);
    if (floatParams.has(key)) return parseFloat(value);
    return value;
  };

  // read params
  const params = Object.fromEntries(
    [...new URLSearchParams(location.search)].map(([k, v]) => [k, cast(k, v)])
  );

  // reset URL params to empty
  // history.replaceState({}, document.title, location.pathname);

  // add defaults on return
  return { ...defaults, ...params}
};

// int and float param keys
// (by default all URL params are read as strings)
const intParams = new Set([
  "agwpTimescale",
  "contrailCirrusERF",
  "efficacy",
  "fuelCost",
  "fuelConsumption",
  "upfrontRD",
  "annualInfra"
]);

const floatParams = new Set([
  "fuelPenalty"
]);

// dashboard defaults
// see scenarioInputs for scenario defaults.
// but all can be overwritten via URL params
const defaults = {
  scenario: "Nominal",
  agwpTimescale: 100,
};
const userInputs = getParams(defaults, intParams, floatParams);
```

<!-- Scenario Input -->
```js
// Scenario
const scenarioInput = Inputs.radio(["Pessimistic", "Nominal", "Optimistic"], {value: userInputs.scenario});
const scenario = Generators.input(scenarioInput)
```

<!-- Timescale Input -->
```js
// AGWP timescale
const agwpTimescaleInput = Inputs.radio([20, 50, 100], {value: userInputs.agwpTimescale});
const agwpTimescale = Generators.input(agwpTimescaleInput)
```

<!-- Runs when `scenario` is changed -->
```js
const scenarioInputs = (scenario === "Nominal") ? {
  contrailCirrusERF: 57,  // mW m-2
  efficacy: 70,           // %
  fuelPenalty: 0.5,       // %
  fuelCost: 90,           // $ / barrel
  fuelConsumption: 103,   // Billions gallons / year
  upfrontRD: 200,         // $M / year
  annualInfra: 100        // $M / year
} : (scenario === "Pessimistic") ? {
  contrailCirrusERF: 26,
  efficacy: 50,
  fuelPenalty: 1,
  fuelCost: 120,
  fuelConsumption: 110,
  upfrontRD: 500,
  annualInfra: 450
} : (scenario === "Optimistic") ? {
  contrailCirrusERF: 57,
  efficacy: 85,
  fuelPenalty: 0.1,
  fuelCost: 90,
  fuelConsumption: 103,
  upfrontRD: 100,
  annualInfra: 20
} : {};

// merge the user inputs with the default scenario inputs
const inputs = { ...scenarioInputs, ...userInputs };

// delete all keys from userInputs after using the first time
// this makes sure that the scenario inputs take precedent
Object.keys(userInputs).forEach(key => delete userInputs[key]);
```

<!-- Constants -->
```js
// AGWP, yr W m-2 / kg-CO2 (Lee 2021, Supplementary Data, Sheet AGWP-CO2)
const AGWP = (agwpTimescale === 100) ? 8.8e-14
  : (agwpTimescale === 50) ? 5.08e-14
  : (agwpTimescale === 20) ? 2.39e-14
  : null;

// constants
const fuelIntensityCO2 = 3.89     // kg CO2 / kg fuel (ICAO - TODO)
const tonnesPerBarrel = 0.127     // tonnes / barrel Jet-A
const gallonsPerBarrel = 42       // 42 US gallons / barrel
```

<!-- Inputs -->
```js
// Mitigation potential (mW m-2).
// Default and bounds from Lee 2021.
const contrailCirrusERFInput = Inputs.range([17, 98], { value: inputs.contrailCirrusERF, step: 1 })
const contrailCirrusERF = Generators.input(contrailCirrusERFInput)

// Mitigation efficacy (%)
const efficacyInput = Inputs.range([0, 100], { value: inputs.efficacy, step: 5 })
const efficacy = Generators.input(efficacyInput)

// Fuel penalty across fleet (%)
const fuelPenaltyInput = Inputs.range([0, 1], { value: inputs.fuelPenalty, step: 0.05 })
const fuelPenalty = Generators.input(fuelPenaltyInput)

// Annual aviation fuel cost ($ / barrel)
// https://www.iata.org/en/publications/economics/fuel-monitor/
const fuelCostInput = Inputs.range([70, 130], { value: inputs.fuelCost, step: 5 })
const fuelCost = Generators.input(fuelCostInput)

// Annual aviation fuel consumption (Billions gallons / year)
// https://www.iata.org/en/iata-repository/pressroom/fact-sheets/industry-statistics/
const fuelConsumptionInput = Inputs.range([90, 110], { value: inputs.fuelConsumption, step: 1 })
const fuelConsumption = Generators.input(fuelConsumptionInput)

// R&D costs ($M / year)
const discountRate = 0.02   // 2%, assumed economic discount rate
const upfrontRDInput = Inputs.range([0, 500], { value: inputs.upfrontRD, step: 10})
const upfrontRD = Generators.input(upfrontRDInput)

// Annual monitoring infrastructure costs ($M / year)
const annualInfraInput = Inputs.range([0, 500], { value: inputs.annualInfra, step: 10})
const annualInfra = Generators.input(annualInfraInput)
```

<!-- Model -->
```js
// Aviation fuel consumption (Mtonnes fuel / year)
const fuelConsumptionMt = (fuelConsumption * 1e9 / gallonsPerBarrel) * tonnesPerBarrel / 1e6

// Aviation fuel CO2 emission, including upstream CO2 (Mtonnes / year)
const fuelCO2 = fuelConsumptionMt * fuelIntensityCO2

// Contrail warming in CO2-eq, GWP100 (Mtonnes / year)
const contrailWarming = (contrailCirrusERF / 1e3) / (AGWP * 1e9)

// Contrail warming avoided in CO2-eq (Mtonnes / year)
const contrailWarmingAvoided = ((efficacy / 100) * contrailWarming) - ((fuelPenalty / 100) * fuelCO2)

// Fuel costs ($M / year)
const additionalFuelCost = (fuelPenalty / 100) * (fuelCost / 0.127 * fuelConsumptionMt)

// R&D costs ($M / year)
// TODO: Does it make sense to have amortized cost the same as AGWP Timescale?
const amortizedRDCost = upfrontRD * discountRate / (1 - (1 + discountRate)**(-agwpTimescale))

// Total annual ($M / year)
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

# Cost Explorer

<!-- Only show this message when on dash.contrails.org -->
${(window.location.hostname === "dash.contrails.org") ? html`<em>See original post on the <a href='https://notebook.contrails.org'>Contrails Notebook</a></em>` : ""}

<div class="card">

## Scenarios

${scenarioInput}

Timescale (years): ${agwpTimescaleInput}

## Development cost

Upfront R&D Cost [$M] ${upfrontRDInput}

Annual Infrastructure Cost [$M / year] ${annualInfraInput}

## Fuel cost

Fuel penalty [%] ${fuelPenaltyInput}

Fuel Cost [$ / barrel] ${fuelCostInput}

Annual Fuel Consumption [Billions gallons / year] ${fuelConsumptionInput}

## Mitigation Potential

Contrail Cirrus Effective Radiative Forcing [mW / m<sup>2</sup>] ${contrailCirrusERFInput}

Mitigation Efficacy [%] ${efficacyInput}

</div>


<div class="grid grid-cols-2">
  <div class="card">

## Warming avoided

<span class="big">${Math.round(contrailWarmingAvoided)}</span><br/>
<span class="muted">Mtonnes CO<sub>2-eq</sub> per year (GWP-${agwpTimescale})</span>

## Annual cost

<span class="big">$${Math.round(totalCost).toLocaleString('en-US')} M</span><br/>
<span class="muted">per year</span>

## Abatement cost

<span class="big">$ ${((additionalFuelCost + amortizedRDCost + annualInfra) / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

  </div>
  <div class="card">

${DonutChart(costPie, {centerText: "Annual Cost", width: 300, colorDomain: costPie.map(c => c.name), colorRange: costPie.map(c => c.color)})}

  </div>
</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/cost-explorer/index.md)

</div>
