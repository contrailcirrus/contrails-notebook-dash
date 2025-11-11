---
title: Global Contrail Heatmap
# theme: slate
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
import { Deck, _GlobeView, MapView, COORDINATE_SYSTEM } from "npm:@deck.gl/core";
import { GeoJsonLayer, BitmapLayer } from 'npm:@deck.gl/layers';
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

<!-- Data prep -->
```js
const firs = topojson.feature(firsTopo, firsTopo.objects.data);
```

<!-- Inputs -->
```js
const mapTypeInput = Inputs.radio(["globe", "flat"], {value: "globe", label: "Map type"});
const mapType = Generators.input(mapTypeInput)

const yearInput = Inputs.radio(Object.keys(erfImages), { value: "2024", label: "Year"})
const year = Generators.input(yearInput)
```

<!-- Deck setup -->
```js
const deckInstance = new Deck({
  parent: document.getElementById("container"),
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
  // getTooltip: ({bitmap}) => bitmap && `${bitmap.pixel}`,
  controller: true,
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
      stroked: true,
      filled: false,
      lineWidthMinPixels: 1,
      getLineColor: [0, 0, 0],
      // getLineColor: [242, 100, 0],
      parameters: { cullMode: 'back', depthCompare: 'always' }
    }),
  ]
});

// clean up if this code re-runs
invalidation.then(() => {
  deckInstance.finalize();
  container.innerHTML = "";
});
```

# Global Contrail Heatmap


This map shows a heat map of local contrail forcing normalized by the global annual contrail forcing.

<div class="card">

## Inputs

${yearInput}

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

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

