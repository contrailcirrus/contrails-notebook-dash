---
title: Global Contrail Heatmap
---

<!-- ----- Dashboard imports ----- -->

<!-- Add any custom styles for this dashboard -->
<!-- Other global styles in `style.css` -->
<style>
  body {
    font-family: var(--sans-serif);

    /* Ghost post max-width */
    max-width: 1000px;
  }
  p, table, figure, figcaption, h1, h2, h3, h4, h5, h6, .katex-display {
    max-width: 100%
  }
</style>

```js
// Resize observer. Required to update parent `iframe` height dynamically.
// See README for script tag required in post body.
import "../components/observer.js";
```

<!-- ----------------------------- -->

```js
import deck from "npm:deck.gl";
const {
  DeckGL,
  _GlobeView,
  MapView,
  COORDINATE_SYSTEM,
  GeoJsonLayer,
  BitmapLayer,
  TextLayer,
} = deck;
```

```js
// geojson natural earth polygons
const land = FileAttachment("data/ne_110m_land.geojson")
const ocean = FileAttachment("data/ne_110m_ocean.geojson")
const firsTopo = FileAttachment("data/worldfirs.topojson").json()
const firImpacts = FileAttachment("data/fir-impacts.json").json()

const erfImages = {
  "2019": FileAttachment("data/2019.png"),
  "2024": FileAttachment("data/2024.png")
}
```

<!-- Inputs -->

```js
// Type of Deck.gl Map
const mapTypeInput = Inputs.radio(["globe", "flat"], {
  value: "globe",
  label: "Map type",
});
const mapType = Generators.input(mapTypeInput);

// Time input
const yearInput = Inputs.radio(Object.keys(erfImages), {
  value: "2024",
  label: "Year",
});
const year = Generators.input(yearInput);

// FIR upper/lower layers
const firLayerInput = Inputs.radio(["Lower", "Upper"], {
  value: "Upper",
  label: "FIR Layer",
});
const firLayer = Generators.input(firLayerInput);

// AGWP timescale
const agwpTimescaleInput = Inputs.radio([20, 50, 100], { value: 100 });
const agwpTimescale = Generators.input(agwpTimescaleInput);

// Mitigation potential (mW m-2).
// Default and bounds from Lee 2021.
const contrailCirrusERFInput = Inputs.range([17, 98], { value: 57, step: 1 });
const contrailCirrusERF = Generators.input(contrailCirrusERFInput);

// Mitigation efficacy (%)
const efficacyInput = Inputs.range([0, 100], { value: 70, step: 5 });
const efficacy = Generators.input(efficacyInput);
```

<!-- Data prep -->
```js
// load world FIRs to GeoJSON
const firs = topojson.feature(firsTopo, firsTopo.objects.data)

// Filter by upper/lower regions
if (firLayer === "Upper") {
  firs["features"] = firs["features"].filter(
    (d) => d.properties.upper === null,
  );
} else {
  firs["features"] = firs["features"].filter((d) => d.properties.lower === 0);
}

// Create search input FIR data from
const firData = firs["features"].map((d) => d.properties);
const firSearchInput = Inputs.search(firData, {
  placeholder: "Search FIRs...",
});
const firSearch = Generators.input(firSearchInput);
```

```js
const firTableInput = Inputs.table(firSearch, {
  columns: ["designator", "name", "value"],
  format: {
    value: (v) => (v ? `${v.toFixed(2)}%` : ``),
  },
  sort: "value",
  reverse: true,
  required: false,
});
const selectedFIRs = Generators.input(firTableInput);

function selectFIR(info, event) {
  console.log(info)
//   console.log(selectedFIRs);
//   if (info.object) {
//     const tableRow = firTableInput.value.filter(
//       (d) => d.designator === info.object.properties.designator,
//     );
//     selectedFIRs.value.push(tableRow);
//   }
}
```

<!-- Calculate migitation potential -->

```js
const selectedDesignators = selectedFIRs.map((d) => d.designator);
const selectedPotential = selectedFIRs.reduce((acc, d) => acc + d.value, 0);

// AGWP, yr W m-2 / kg-CO2 (Lee 2021, Supplementary Data, Sheet AGWP-CO2)
const AGWP =
  agwpTimescale === 100
    ? 8.8e-14
    : agwpTimescale === 50
    ? 5.08e-14
    : agwpTimescale === 20
    ? 2.39e-14
    : null;

// Contrail warming in CO2-eq, GWP100 (Mtonnes / year)
const contrailWarming = contrailCirrusERF / 1e3 / (AGWP * 1e9);

// Contrail warming avoided in CO2-eq (Mtonnes / year)
const contrailWarmingAvoided =
  (selectedPotential / 100) * ((efficacy / 100) * contrailWarming);
```

<!-- Deck setup -->

```js
const getTooltip = ({ object }) => {
  return (
    object &&
    object.properties &&
    `${object.properties.designator}\n${
      object.properties.name
    }\n${object.properties.value.toFixed(2)}%`
  );
};
const deckInstance = new DeckGL({
  container: document.getElementById("container"),
  style: { position: "relative" },
  views: mapType === "globe" ? [new _GlobeView()] : [new MapView()],
  initialViewState: {
    longitude: -2,
    latitude: 53.5,
    zoom: 2,
    minZoom: 1,
    maxZoom: 6,
    pitch: 0,
    bearing: 0,
  },
  getTooltip: getTooltip,
  controller: true,
});

// clean up if this code re-runs
invalidation.then(() => {
  deckInstance.finalize();
  container.innerHTML = "";
});
```

```js
deckInstance.setProps({
  layers: [
    new GeoJsonLayer({
      id: "land",
      data: land.href,
      stroked: false,
      filled: true,
      getFillColor: [210, 210, 210],
    }),
    new GeoJsonLayer({
      id: "ocean",
      data: ocean.href,
      stroked: false,
      filled: true,
      getFillColor: [255, 255, 255],
    }),
    new BitmapLayer({
      id: "erfImage",
      bounds: [-180.0, -90.0, 180.0, 90.0],
      image: erfImages[year].href,
      _imageCoordinateSystem: COORDINATE_SYSTEM.LNGLAT,
      opacity: 0.1,
      pickable: true,
      // makes sure that layer sites above geojson layers above
      parameters: { cullMode: "back", depthCompare: "always" },
    }),
    new GeoJsonLayer({
      id: "firs",
      data: firs,
      pickable: true,
      stroked: true,
      filled: true,
      lineWidthMinPixels: 1,
      // autoHighlight: true,
      // highlightColor: [242, 100, 0, 50],
      // getLineColor: [0, 0, 0],
      getLineColor: [0, 0, 0],
      getFillColor: (d) => {
        if (selectedDesignators.includes(d.properties.designator)) {
          return [242, 100, 0, 125];
        }
        return [0, 0, 0, 0];
      },
      onClick: selectFIR,
      updateTriggers: {
        getFillColor: selectedDesignators,
      },
      parameters: { cullMode: "back", depthCompare: "always" },
    }),
    new TextLayer({
      id: "firLabels",
      data: firs["features"],
      getText: (f) => f.properties.designator,
      getPosition: (f) => {
        // Calculate centroid
        const coords = f.geometry.coordinates[0];
        const lon = coords.reduce((sum, c) => sum + c[0], 0) / coords.length;
        const lat = coords.reduce((sum, c) => sum + c[1], 0) / coords.length;
        return [lon, lat];
      },
      getSize: 10,
      getColor: [0, 0, 0],
      billboard: false,
      getAngle: mapType === "globe" ? 180 : 0,
      fontFamily: "monospace",
    }),
  ],
});
```

# Global Contrail Heatmap

This map shows the proportion of global annual contrail forcing by FIR.

<div class="card">

## Inputs

${yearInput}

${firLayerInput}

</div>
<div class="card">

<figure>

## Explore FIRs

${mapTypeInput}

<div id="container" style="border-radius: 8px; overflow: hidden; background: rgb(0,0,0); height: 75vh; margin: 1rem 0; ">
</div>
<figcaption>
  Contrail Data: <a href="https://acp.copernicus.org/articles/24/6071/2024/">Teoh 2024</a><br/>
  FIR Regions: <a href="https://observablehq.com/@openaviation/flight-information-regions">Open Aviation</a>
</figcaption>
</figure>
</div>

<div class="card">

## Select FIR

${firSearchInput}

${firTableInput}

</div>
<div class="card">

## Mitigation Potential

Timescale (years): ${agwpTimescaleInput}

Contrail Cirrus Effective Radiative Forcing [mW / m<sup>2</sup>] ${contrailCirrusERFInput}

Mitigation Efficacy [%] ${efficacyInput}

<span class="big">${selectedPotential.toFixed(2)}%</span><br/>
<span class="muted">global contrail forcing</span>

<span class="big">${Math.round(contrailWarmingAvoided)}</span><br/>
<span class="muted">Mtonnes CO<sub>2-eq</sub> per year (GWP-100)</span>

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>
