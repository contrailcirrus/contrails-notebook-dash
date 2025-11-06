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
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>
<link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
<!-- ----------------------------- -->

```js
import * as L from "npm:leaflet";
import "npm:leaflet-draw"
```

```js
// geojson natural earth polygons
const land = FileAttachment("ne_110m_land.geojson").json()
const ocean = FileAttachment("ne_110m_ocean.geojson").json()
const erfImage = FileAttachment("2019wm.png")
```

```js
const map = L.map("map")
  .setView([30,-30], 2);

L.geoJSON(land, {
    style: {stroke: true, color: "#ffffff", opacity: 0.3, fill: true, fillColor: "#aaaaaa", fillOpacity: 1}
}).addTo(map);

L.geoJSON(ocean, {
    style: {stroke: false, fill: true, fillColor: "#ffffff", fillOpacity: 1}
}).addTo(map);

L.imageOverlay(erfImage.href, [[90, -180], [-90, 180]], {
  zIndex: 1000,
  opacity: 0.5
}).addTo(map);

// Layer to hold drawn items
const drawnItems = new L.FeatureGroup().addTo(map);

// Activate Leaflet.draw with rectangle tool only
const drawControl = new L.Control.Draw({
  draw: {
    polygon: true,
    rectangle: false,
    marker: false,
    circlemarker: false,
    circle: false,
    polyline: false,
  },
  edit: false
});
map.addControl(drawControl);

map.on('draw:drawstart', function () {
  drawnItems.clearLayers();
});

// Capture the rectangle once drawn
map.on('draw:created', function (e) {
  const layer = e.layer;
  drawnItems.addLayer(layer);

  // Get corner coordinates
  const corners = layer.getLatLngs()[0]; // clockwise starting SW
  console.log('Rectangle corners:', corners);
});

// clean up if this code re-runs
invalidation.then(() => {
  map.innerHTML = "";
});

```

# 2019 Global Contrail ERF heatmap


This map shows the proportion of contrail forcing relative to the 2019 global annual contrail forcing.


<div class="card">

<figure>

  <div id="map" style="border-radius: 8px; overflow: hidden; background: #ffffff; height: 60vh; margin: 1rem 0; ">
  </div>
  <figcaption>Data: <a href="https://acp.copernicus.org/articles/24/6071/2024/">Teoh 2024</a></figcaption>
</figure>

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

