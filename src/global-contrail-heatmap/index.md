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
const {DeckGL, _GlobeView, MapView, COORDINATE_SYSTEM, GeoJsonLayer, BitmapLayer, TextLayer} = deck;
```

```js
// geojson natural earth polygons
const land = FileAttachment("ne_110m_land.geojson")
const ocean = FileAttachment("ne_110m_ocean.geojson")
const firsTopo = FileAttachment("firs.topojson").json()

const erfImages = {
  "2019": FileAttachment("2019.png"),
  "2024": FileAttachment("2024.png")
}
```

<!-- Inputs -->
```js
const mapTypeInput = Inputs.radio(["globe", "flat"], {value: "globe", label: "Map type"});
const mapType = Generators.input(mapTypeInput)

const yearInput = Inputs.radio(Object.keys(erfImages), { value: "2024", label: "Year"})
const year = Generators.input(yearInput)

const firLayerInput = Inputs.radio(["Lower", "Upper"], { value: "Upper", label: "FIR Regions"})
const firLayer = Generators.input(firLayerInput)
```

<!-- Data prep -->
```js
const firs = topojson.feature(firsTopo, firsTopo.objects.data)

if (firLayer === "Upper") {
  firs["features"] = firs["features"].filter(d => d.properties.upper === null)
} else {
  firs["features"] = firs["features"].filter(d => d.properties.lower === 0)
}

const firData = firs["features"].map(d => d.properties).filter(d => d.type === "FIR")
const firSearchInput = Inputs.search(firData, {placeholder: "Search FIRs..."})
const firSearch = Generators.input(firSearchInput)
```

```js
const firTable = Inputs.table(firSearch, {
  columns: [
    "designator",
    "name",
    "value"
  ],
  format: {
    value: (v) => `${v.toFixed(2)}%`
  },
  sort: "value",
  reverse: true
})
```

<!-- Deck setup -->
```js

const getTooltip = ({object}) => {
  return object && `${object.properties.designator}\n${object.properties.name}\n${object.properties.value.toFixed(2)}%`
}
const deckInstance = new DeckGL({
  container: document.getElementById("container"),
  style: {"position": "relative"},
  views: mapType === "globe" ? [
    new _GlobeView()
  ] : [
    new MapView()
  ],
  initialViewState: {
    longitude: -2,
    latitude: 53.5,
    zoom: 2,
    minZoom: 1,
    maxZoom: 6,
    pitch: 0,
    bearing: 0
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
      parameters: { cullMode: 'back', depthCompare: 'always' }
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
      getLineColor: [0, 0, 0],
      getFillColor: [0,0,0,0], // required for getTooltip
      parameters: { cullMode: 'back', depthCompare: 'always' },
    }),
    new TextLayer({
      id: "firLabels",
      data: firs["features"],
      getText: f => f.properties.designator,
      getPosition: f => {
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
      fontFamily: "monospace"
    })
  ]
});
```
# Global Contrail Heatmap


This map shows a heat map of local contrail forcing normalized by the global annual contrail forcing.

<div class="card">

## Inputs

${yearInput}

${firLayerInput}

</div>
<div class="card">

<figure>

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

${firSearchInput}

${firTable}

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

