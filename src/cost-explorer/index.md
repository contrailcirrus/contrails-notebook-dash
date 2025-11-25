---
title: Cost Explorer
---

<!-- ----- Dashboard imports ----- -->

<!-- Add any custom styles for this dashboard -->
<!-- Other global styles in `style.css` -->
<style>
  .share {
    position: absolute;
    right: 0;
    top: 0;

    form {
      width: unset;
    }
    svg {
      margin-bottom: -3px;
    }
    /* "Copied!" text */
    .observablehq-pre-copied::before {
      padding: 0px 8px;
    }
  }
</style>

<!-- Imports -->
```js
import "../components/observer.js";

import {DonutChart} from "../components/donutChart.js";
```

<!-- ----------------------------- -->

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
  history.replaceState({}, document.title, location.pathname);

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
  "upfrontRD",
  "annualInfra",
  "flights"
]);

const floatParams = new Set([
  "additionalFuel",
  "maintenanceFactor"
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
  contrailCirrusERF: 57,    // mW m-2
  efficacy: 70,             // %
  additionalFuel: 0.3,      // %
  maintenanceFactor: 1.15,  //
  fuelCost: 90,             // $ / barrel
  upfrontRD: 250,           // $M / year
  annualInfra: 20,          // $M / year
  flights: 38,              // M flights / year
  fuelPerFlight: 2690,      // gal / flight
} : (scenario === "Pessimistic") ? {
  contrailCirrusERF: 26,
  efficacy: 50,
  additionalFuel: 0.5,
  maintenanceFactor: 1.2,
  fuelCost: 120,
  upfrontRD: 500,
  annualInfra: 200,
  flights: 38,
  fuelPerFlight: 2690,
} : (scenario === "Optimistic") ? {
  contrailCirrusERF: 57,
  efficacy: 80,
  additionalFuel: 0.1,
  maintenanceFactor: 1.1,
  fuelCost: 90,
  upfrontRD: 150,
  annualInfra: 10,
  flights: 38,
  fuelPerFlight: 2690,
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
const discountRate = 0.02         // 2%, assumed economic discount rate
```

<!-- Inputs -->
```js
// Mitigation potential (mW m-2).
// Default and bounds from Lee 2021.
const contrailCirrusERFInput = Inputs.range([17, 98], { value: inputs.contrailCirrusERF, step: 1 })
const contrailCirrusERF = Generators.input(contrailCirrusERFInput)

// Mitigation efficacy (%)
const efficacyInput = Inputs.range([50, 100], { value: inputs.efficacy, step: 5 })
const efficacy = Generators.input(efficacyInput)

// Fuel penalty across fleet (%)
const additionalFuelInput = Inputs.range([0, 0.5], { value: inputs.additionalFuel, step: 0.05 })
const additionalFuel = Generators.input(additionalFuelInput)

// gal / flight, 2025F https://www.iata.org/en/iata-repository/pressroom/
const fuelPerFlightInput = Inputs.range([2500, 2800], { value: inputs.fuelPerFlight, step: 10 })
const fuelPerFlight = Generators.input(fuelPerFlightInput)

// Increases added fuel costs by an additional maintenance / compliance factor
const maintenanceFactorInput = Inputs.range([1, 1.2], { value: inputs.maintenanceFactor, step: 0.01 })
const maintenanceFactor = Generators.input(maintenanceFactorInput)

// Annual aviation fuel cost ($ / barrel)
// https://www.iata.org/en/publications/economics/fuel-monitor/
const fuelCostInput = Inputs.range([80, 120], { value: inputs.fuelCost, step: 1 })
const fuelCost = Generators.input(fuelCostInput)

// Annual aviation fuel consumption (Billions gallons / year)
// https://www.iata.org/en/iata-repository/pressroom/fact-sheets/industry-statistics/
// const fuelConsumptionInput = Inputs.range([90, 110], { value: inputs.fuelConsumption, step: 1 })
// const fuelConsumption = Generators.input(fuelConsumptionInput)

// R&D costs ($M / year)
const upfrontRDInput = Inputs.range([0, 500], { value: inputs.upfrontRD, step: 10})
const upfrontRD = Generators.input(upfrontRDInput)

// Annual monitoring infrastructure costs ($M / year)
const annualInfraInput = Inputs.range([0, 200], { value: inputs.annualInfra, step: 5})
const annualInfra = Generators.input(annualInfraInput)

// Global aviation activity (M flights / year)
const flightsInput = Inputs.range([30, 50], { value: inputs.flights, step: 1})
const flights = Generators.input(flightsInput)
```

<!-- Model -->
```js
// Fuel cost ($ / tonne)
const fuelCostTonnes = fuelCost / tonnesPerBarrel

// Aviation fuel consumption (Billions gallons / year)
const fuelConsumption = fuelPerFlight * flights * 1e6 / 1e9

// Aviation fuel consumption (Mtonnes fuel / year)
const fuelConsumptionMt = (fuelConsumption * 1e9 / gallonsPerBarrel) * tonnesPerBarrel / 1e6

// Aviation fuel CO2 emission, including upstream CO2 (Mtonnes / year)
const fuelCO2 = fuelConsumptionMt * fuelIntensityCO2

// Contrail warming in CO2-eq, GWP100 (Mtonnes / year)
const contrailWarming = (contrailCirrusERF / 1e3) / (AGWP * 1e9)

// Contrail warming avoided in CO2-eq (Mtonnes / year)
const contrailWarmingAvoided = Math.max(((efficacy / 100) * contrailWarming) - ((additionalFuel / 100) * fuelCO2), 0)

// Fuel costs ($M / year)
const additionalFuelCost = (additionalFuel / 100) * (fuelCostTonnes * fuelConsumptionMt) * maintenanceFactor

// R&D costs ($M / year)
// TODO: Does it make sense to have amortized cost the same as AGWP Timescale?
const amortizedRDCost = upfrontRD * discountRate / (1 - (1 + discountRate)**(-agwpTimescale))

// Total annual ($M / year)
const totalCost = additionalFuelCost + amortizedRDCost + annualInfra
```

<!-- Visuals -->
```js
const costPie = [
  {name: "Fuel", value: Math.round(100*(additionalFuelCost / totalCost)), format: (v) => `${v}%`, color: "#f26400"}, // solar-orange
  {name: "R&D", value: Math.round(100*(amortizedRDCost / totalCost)), format: (v) => `${v}%`, color: "#99a1af"}, // gray-400
  {name: "Infrastructure", value: Math.round(100*(annualInfra / totalCost)), format: (v) => `${v}%`, color: "#1093ff"} // tropo-blue
]
```

<!-- Share -->
```js
const currentScenario = {
  scenario: scenario,
  agwpTimescale: agwpTimescale,
  contrailCirrusERF: contrailCirrusERF,
  efficacy: efficacy,
  additionalFuel: additionalFuel,
  fuelCost: fuelCost,
  fuelConsumption: fuelConsumption,
  upfrontRD: upfrontRD,
  annualInfra: annualInfra,
  flights: flights
}
```

```js
const showCopied = () => {
  const button = document.getElementById("sharecontainer").querySelector('button');

  // hack to steal the "Copied" text and animation from the <pre> code blocks
  button.classList.add("observablehq-pre-copied");
  button.addEventListener("animationend", () => button.classList.remove("observablehq-pre-copied"), { once: true });
}

const shareScenario = async () => {
  const baseUrl = location.origin + location.pathname;
  const params = new URLSearchParams(currentScenario);
  const paramString = params.toString();
  const shareUrl = `${baseUrl}?${paramString}`

  try {
    await navigator.share({
      title: "Contrail Cost Explorer",
      url: shareUrl
    })
  } catch (e) {
    try {
      await navigator.clipboard.writeText(shareUrl);
      showCopied()
      // alert("Copied scenario URL to clipboard")
    } catch (error) {
      console.error(error)
    }
  }
}

const shareButtonText =html`Share
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path d="M 21 5 A 3 3 0 1 1 15 5 A 3 3 0 1 1 21 5 M 9 12 A 3 3 0 1 1 3 12 A 3 3 0 1 1 9 12 M 21 19 A 3 3 0 1 1 15 19 A 3 3 0 1 1 21 19 M 8.5 10.5 L 15.5 6.5 M 8.5 13.5 L 15.5 17.5" stroke-width="2"/>
    </svg>`
const shareButton = Inputs.button(shareButtonText, {value: null, reduce: shareScenario});
```

# Cost Explorer

<div id="sharecontainer" class="share">${shareButton}</div>

<!-- Only show this message when on dash.contrails.org -->
${(window.self === window.top) ? html`<em>See original post on the <a href='https://notebook.contrails.org'>Contrails Notebook</a></em>` : ""}

<div class="card">

## Scenario

${scenarioInput}

## Development cost

Upfront R&D Cost [$M] ${upfrontRDInput}

Annual Infrastructure Cost [$M / year] ${annualInfraInput}

## Fuel cost

Additional fuel [%] ${additionalFuelInput}


## Mitigation Potential

Contrail Cirrus Effective Radiative Forcing [mW / m<sup>2</sup>] ${contrailCirrusERFInput}

Mitigation Efficacy [%] ${efficacyInput}

</div>

<div class="card">

<details>
  <summary><b>Advanced Inputs</b></summary>

## Scenario

Timescale (years): ${agwpTimescaleInput}

Flights [Millions flights / year]: ${flightsInput}

## Fuel

Fuel Cost [$ / barrel] &nbsp;&nbsp; *(\$${Math.round(fuelCostTonnes)} / tonne)* ${fuelCostInput}

Fuel per flight [gal / flight] ${fuelPerFlightInput}

Maintenance Factor ${maintenanceFactorInput}




<!-- Annual Fuel Consumption [Billions gallons / year] ${fuelConsumptionInput} -->

</details>
</div>


<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
<div class="card">

## Warming avoided

<span class="big">${Math.round(contrailWarmingAvoided)}</span><br/>
<span class="muted">Mtonnes CO<sub>2-eq</sub> per year (GWP-${agwpTimescale})</span>

## Annual cost

<span class="big">$${Math.round(totalCost).toLocaleString('en-US')} M</span><br/>
<span class="muted">per year</span>

## Mitigation cost

<span class="big">$ ${(totalCost / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

<span class="big">$ ${(totalCost / flights ).toFixed(2)}</span><br/>
<span class="muted">per flight</span>

</div>

<div class="card" style="text-align: center">

${DonutChart(costPie, {centerText: "Annual Cost", width: 300, colorDomain: costPie.map(c => c.name), colorRange: costPie.map(c => c.color)})}

</div>
</div>

<div class="card">

<details>
  <summary><b>Additional Outputs</b></summary>

- **Annual Fuel Consumption** [Billions gallons / year] ${Math.round(fuelConsumption)}
- **Annual Fuel Consumption** [Mt / year] ${Math.round(fuelConsumptionMt)}
- **Additional fuel cost**: $${Math.round(additionalFuelCost)}M / year ($${(additionalFuelCost / contrailWarmingAvoided).toFixed(2)} per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale}))
- **Annual infrastructure**: $${annualInfra}M / year ($${(annualInfra / contrailWarmingAvoided).toFixed(2)} per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale}))
- **Amortized R&D cost**: $${Math.round(amortizedRDCost)}M / year ($${(amortizedRDCost / contrailWarmingAvoided).toFixed(2)} per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale}))

</details>
</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/cost-explorer/index.md)

</div>
