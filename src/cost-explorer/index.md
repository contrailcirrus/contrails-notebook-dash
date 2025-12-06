---
title: Contrail Cost Explorer
---

<!-- ----- Dashboard imports ----- -->

<!-- Add any custom styles for this dashboard -->
<!-- Other global styles in `style.css` -->
<style>

  body {
    /* Ghost post max-width */
    max-width: 1000px;
  }
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
  "upfrontRD",
  "ongoingRD",
  "annualInfra",
  "annualWorkforce",
]);

const floatParams = new Set([
  "additionalFuel",
  "fuelCost",
  "reroutingFactor"
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
  reroutingFactor: 1.15,    //
  fuelCost: 2.05,           // $ / gal
  upfrontRD: 250,           // $M / year
  ongoingRD: 10,            // $M / year
  annualInfra: 20,          // $M / year
  annualWorkforce: 15,       // $M / year
} : (scenario === "Pessimistic") ? {
  contrailCirrusERF: 26,
  efficacy: 50,
  additionalFuel: 0.5,
  reroutingFactor: 1.2,
  fuelCost: 2.80,
  upfrontRD: 500,
  ongoingRD: 30,
  annualInfra: 200,
  annualWorkforce: 30,
} : (scenario === "Optimistic") ? {
  contrailCirrusERF: 57,
  efficacy: 80,
  additionalFuel: 0.1,
  reroutingFactor: 1.1,
  fuelCost: 2.00,
  upfrontRD: 200,
  ongoingRD: 5,
  annualInfra: 10,
  annualWorkforce: 5,
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
const fuelIntensityCO2 = 3.89     // kg CO2 / kg fuel, ICAO's well-to-wake figure for Jet A
const tonnesPerBarrel = 0.127     // tonnes / barrel Jet-A
const gallonsPerBarrel = 42       // 42 US gallons / barrel
const discountRate = 0.02         // 2%, assumed economic discount rate
const rndAmortization = 50        // years, amortization time for upfront R&D
// const totalRevenues = 979e9       // $ / year, 2025 expectations, https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/
const totalExpenses = 913e9       // $ / year, 2025 expectations, https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/
const fuelEfficiency = 0.087      // gal / RTK, 2025 expectations, https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/
const RTK = 1.19e12                // RTK, 2025 expectations, https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/
const flights = 38                 // millions of annual flights, 2025 expectations, https://www.iata.org/en/iata-repository/pressroom/fact-sheets/industry-statistics/
// const loadFactor = 0.83            // 83%, 2019 load factor from Teoh et al 2024
// const seatsPerFlight = 160         // average seats per flight, https://www.oag.com/blog/average-flight-capacity-increasing-at-fastest-rate-ever
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

// Increases added fuel costs by an additional maintenance / compliance factor
const reroutingFactorInput = Inputs.range([1, 1.2], { value: inputs.reroutingFactor, step: 0.01 })
const reroutingFactor = Generators.input(reroutingFactorInput)

// Annual aviation fuel cost ($ / gal)
// https://www.iata.org/en/publications/economics/fuel-monitor/
const fuelCostInput = Inputs.range([2.0, 2.80], { value: inputs.fuelCost, step: 0.01 })
const fuelCost = Generators.input(fuelCostInput)

// R&D costs ($M / year)
const upfrontRDInput = Inputs.range([100, 500], { value: inputs.upfrontRD, step: 10})
const upfrontRD = Generators.input(upfrontRDInput)

const ongoingRDInput = Inputs.range([0, 30], { value: inputs.ongoingRD, step: 1})
const ongoingRD = Generators.input(ongoingRDInput)

// Annual monitoring infrastructure costs ($M / year)
const annualInfraInput = Inputs.range([0, 200], { value: inputs.annualInfra, step: 5})
const annualInfra = Generators.input(annualInfraInput)

// Annual additional workload costs ($M / year)
const annualWorkforceInput = Inputs.range([0, 30], { value: inputs.annualWorkforce, step: 1})
const annualWorkforce = Generators.input(annualWorkforceInput)
```

<!-- Model -->
```js
// Fuel cost ($ / tonne)
const fuelCostTonnes = fuelCost * gallonsPerBarrel / tonnesPerBarrel

// Aviation fuel consumption (Billions gallons / year)
const fuelConsumption = fuelEfficiency * RTK / 1e9

// Aviation fuel consumption (Mtonnes fuel / year)
const fuelConsumptionMt = (fuelConsumption * 1e9 / gallonsPerBarrel) * tonnesPerBarrel / 1e6

// Aviation fuel CO2 emission, including upstream CO2 (Mtonnes / year)
const fuelCO2 = fuelConsumptionMt * fuelIntensityCO2

// Contrail warming in CO2-eq, GWP100 (Mtonnes / year)
const contrailWarming = (contrailCirrusERF / 1e3) / (AGWP * 1e9)

// Contrail warming avoided in CO2-eq (Mtonnes / year)
const contrailWarmingAvoided = Math.max(((efficacy / 100) * contrailWarming) - ((additionalFuel / 100) * fuelCO2), 0)

// Fuel costs ($M / year)
const additionalFuelCost = (additionalFuel / 100) * (fuelCost * fuelConsumption * 1e9) * reroutingFactor / 1e6

// R&D costs ($M / year)
const amortizedRDCost = upfrontRD * discountRate / (1 - (1 + discountRate)**(-rndAmortization))
const RDCost = amortizedRDCost + ongoingRD

// Total annual ($M / year)
const totalCost = additionalFuelCost + RDCost + annualInfra + annualWorkforce
```

<!-- Visuals -->
```js
const costPie = [
  {name: "Fuel", value: Math.round(100*(additionalFuelCost / totalCost)), format: (v) => `${v}%`, color: "#f26400"}, // solar-orange
  {name: "Infrastructure", value: Math.round(100*(annualInfra / totalCost)), format: (v) => `${v}%`, color: "#1093ff"}, // tropo-blue
  {name: "R&D", value: Math.round(100*(RDCost / totalCost)), format: (v) => `${v}%`, color: "#99a1af"}, // gray-400
  {name: "Workforce", value: Math.round(100*(annualWorkforce / totalCost)), format: (v) => `${v}%`, color: "#000000"}, // black
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
  reroutingFactor: reroutingFactor,
  fuelCost: fuelCost,
  upfrontRD: upfrontRD,
  ongoingRD: ongoingRD,
  annualInfra: annualInfra,
  annualWorkforce: annualWorkforce,
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

# Contrail Cost Explorer

<div id="sharecontainer" class="share">${shareButton}</div>

<!-- Only show this message when on dash.contrails.org -->
${(window.self === window.top) ? html`<em>See original post on the <a href='https://notebook.contrails.org'>Contrails Notebook</a></em>` : ""}

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">

<div>

### Inputs

<div class="card">

## Scenario

${scenarioInput}

## Implementation cost

<details>
<summary>Upfront R&D [$M]</summary>

*The upfront R&D necessary to make contrail management standard practice, in millions of US dollars. This R&D value is amortized over ${rndAmortization} years at a discount rate of ${Math.round(discountRate * 100)}% to come up with an annual cost.*

</details>

${upfrontRDInput}

<details>
<summary>Ongoing R&D [$M / year]</summary>

*The ongoing R&D necessary to maintain and improve contrail management practices over time, in millions of US dollars.*

</details>

${ongoingRDInput}

<details>
<summary>Forecast & Measurement Infrastructure [$M / year]</summary>

*The recurring cost of infrastructure required to forecast, monitor, and measure contrails, in millions of US dollars per year.*

</details>

${annualInfraInput}

<details>
<summary>Workforce [$M / year]</summary>

*The additional human capital necessary to implement contrail avoidance at scale, in millions of US dollars per year.*

</details>

${annualWorkforceInput}

## Fuel cost

<details>
<summary>Additional Fuel [%]</summary>

*Additional fuel (across the whole fleet) for contrail avoidance, as a percentage of global annual fuel consumption.*

</details>

${additionalFuelInput}

## Mitigation Potential

<details>
<summary>Contrail Cirrus Effective Radiative Forcing [mW / m<sup>2</sup>]</summary>

*Global annual contrail effective radiative forcing (ERF). Central estimate and bounds taken from [Lee et al. 2021](https://linkinghub.elsevier.com/retrieve/pii/S1352231020305689).*

</details>

${contrailCirrusERFInput}

<details>
<summary>Mitigation Efficacy [%]</summary>

*Contrail avoidance will never be 100% effective. This factor reduces the mitigation potential to capture errors in contrail forecasting and infeasible avoidance measures.*

</details>

${efficacyInput}

</div>

<div class="card">

<details>
<summary><h2>Additional Inputs</h2></summary>

## Scenario

<details>
<summary>Time Horizon [years]</summary>

*Time horizon for calculating CO<sub>2-eq</sub> [Global Warming Potential](https://en.wikipedia.org/wiki/Global_warming_potential).*

</details>

${agwpTimescaleInput}

## Fuel

<details>
<summary>Fuel Cost [$ / gal]  &nbsp; <em>(\$${Math.round(fuelCostTonnes)} / tonne)</em> </summary>

*The average cost of Jet-A fuel, in US dollars per US gallon.*

</details>

${fuelCostInput}

<details>
<summary>Rerouting Factor</summary>

*This factor scales the additional fuel cost to account for other potential rerouting costs, like overflight charges and engine maintenance.*

</details>

${reroutingFactorInput}

</div>
</div>

<div>

### Outputs

<div class="card">

## Warming avoided

<span class="big">${Math.round(contrailWarmingAvoided)}</span><br/>
<span class="muted">Mtonnes CO<sub>2-eq</sub> per year (GWP-${agwpTimescale})</span>

## Mitigation cost

<span class="big">$ ${(totalCost / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

<span class="big">$ ${(totalCost / flights ).toFixed(2)}</span><br/>
<span class="muted">per flight</span>

<!-- <span class="big">$ ${((totalCost / flights) / (loadFactor * seatsPerFlight)).toFixed(2)}</span><br/>
<span class="muted">per seat</span> -->

</div>

<div class="card" style="text-align: center">

${DonutChart(costPie, {centerText: "Annual Cost", width: 300, colorDomain: costPie.map(c => c.name), colorRange: costPie.map(c => c.color)})}

</div>

<div class="card">

<details>
<summary><h2>Total cost</h2></summary>

<span class="big">$${Math.round(totalCost).toLocaleString('en-US')}M</span><br/>
<span class="muted">per year</span>

<span class="big">${(100 * totalCost * 1e6 / totalExpenses).toFixed(2)} %</span><br/>
<!-- <span class="muted">of expected 2025 aviation revenues</span> -->
<span class="muted">of expected <a href="https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/">2025 aviation expenses</a></span>

</details>
</div>

<!-- Additional outputs for reference -->
<div class="grid grid-cols-2" style="grid-auto-rows: auto;">

<div class="card">

<details>
<summary><h2>Additional fuel</h2></summary>

<span class="big">$${Math.round(additionalFuelCost).toLocaleString('en-US')}M</span><br/>
<span class="muted">per year</span>

<span class="big">$${(additionalFuelCost / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

</details>
</div>

<div class="card">

<details>
<summary><h2>Infrastructure</h2></summary>

<span class="big">$${annualInfra}M</span><br/>
<span class="muted">per year</span>

<span class="big">$${(annualInfra / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

</details>
</div>

<div class="card">

<details>
<summary><h2>R&D</h2></summary>

<span class="big">$${RDCost.toFixed(2)}M</span><br/>
<span class="muted">per year</span>

<span class="big">$${(RDCost / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

</details>
</div>

<div class="card">

<details>
<summary><h2>Workforce</h2></summary>

<span class="big">$${annualWorkforce}M</span><br/>
<span class="muted">per year</span>

<span class="big">$${(annualWorkforce / contrailWarmingAvoided).toFixed(2)}</span><br/>
<span class="muted">per tonne CO<sub>2-eq</sub> (GWP-${agwpTimescale})</span>

</details>
</div>

<!-- <div class="card">

<details>
<summary><h2>Baseline Fuel Consumption</h2></summary>

<span class="big">${Math.round(fuelConsumption)}</span><br/>
<span class="muted">Billions gallons per year</span>

<span class="big">${Math.round(fuelConsumptionMt)}</span><br/>
<span class="muted">Megatonnes CO<sub>2</sub> per year</span>

</details>
</div> -->
