---
title: 2019 Contrail ERF Percentage
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
const erfImage = FileAttachment("2019.png")
```

```js
const mapTypeInput = Inputs.radio(["globe", "flat"], {value: "globe"});
const mapType = Generators.input(mapTypeInput)
```

```js
const deckInstance = new Deck({
  parent: document.getElementById("container"),
  style: {"position": "relative"},
  views: mapType === "globe" ? [
    new _GlobeView()
  ] : [
    new MapView()
  ],
  initialViewState,
  // getTooltip: ({bitmap}) => bitmap && `${bitmap.pixel}`,
  controller: true,
});

// clean up if this code re-runs
invalidation.then(() => {
  deckInstance.finalize();
  container.innerHTML = "";
});
```

```js
const initialViewState = {
  longitude: -2,
  latitude: 53.5,
  zoom: 2,
  minZoom: 1,
  maxZoom: 6,
  pitch: 0,
  bearing: 0
};
```

```js
deckInstance.setProps({
  layers: [
    new GeoJsonLayer({
      id: "land",
      data: land.href,
      stroked: true,
      filled: true,
      getFillColor: [210, 210, 210],
      lineWidthMinPixels: 1,
      getLineColor: [220, 220, 220],
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
      image: erfImage.href,
      _imageCoordinateSystem: COORDINATE_SYSTEM.LNGLAT,
      opacity: 0.1,
      pickable: true,
      // makes sure that layer sites above geojson layers above
      parameters: { cullMode: 'back', depthCompare: 'always' }
    }),
  ]
});
```

# 2019 Global Contrail ERF heatmap


This map shows the proportion of contrail forcing relative to the 2019 global annual contrail forcing.


<div class="card">

<figure>

  ${mapTypeInput}

  <div id="container" style="border-radius: 8px; overflow: hidden; background: rgb(0,0,0); height: 75vh; margin: 1rem 0; ">
  </div>
  <figcaption>Data: <a href="https://acp.copernicus.org/articles/24/6071/2024/">Teoh 2024</a></figcaption>
</figure>

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

