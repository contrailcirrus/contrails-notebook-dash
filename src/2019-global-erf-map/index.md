---
title: 2019 Contrail ERF Percentage
theme: default
---

<!-- ----- Dashboard imports ----- -->

<!-- Add any custom styles for this dashboard -->
<!-- Other global styles in `style.css` -->
<style></style>


```js
// Resize observer. Required to update parent `iframe` height dynamically.
// See README for script tag required in post body.
import "../components/observer.js";

```

<!-- ----------------------------- -->

```js
import {NetCDFReader} from "npm:netcdfjs";
import deck from "npm:deck.gl";
const {DeckGL, AmbientLight, _GlobeView, GeoJsonLayer, HeatmapLayer, LightingEffect, PointLight} = deck;
```

```js
const erf = FileAttachment("2019-percent.nc").arrayBuffer().then((data) => new NetCDFReader(data));

// land
const world = FileAttachment("countries-110m.json").json()
const land = FileAttachment("countries-50m.json").json()
```

```js
function extractData(reader, varName) {
  const variable = reader.getDataVariable(varName);
  const lon = reader.getDataVariable('longitude');
  const lat = reader.getDataVariable('latitude');

  const data = [];
  for (let i = 0; i < lat.length; i++) {
    for (let j = 0; j < lon.length; j++) {
      const value = variable[i * lon.length + j];
      if (value !== null && value !== undefined) {
        data.push({
          position: [lon[j], lat[i]],
          weight: value
        });
      }
    }
  }
  return data;
}
```
```js
// const land = topojson.feature(world, world.objects.land)
// const erf_percent = erf.getDataVariable("erf_percent")
const erf_data = extractData(erf, "erf_percent")
```

```js
// reverse dimensions
// erf.header.variables[0].dimensions[0] = 1
// erf.header.variables[0].dimensions[1] = 0
// console.log(erf.getDataVariable("erf_percent"))
// console.log(erf.header)

const longitudeInput = Inputs.range([-180, 180], { value: 1, step: 1})
const longitude = Generators.input(longitudeInput)

const latitudeInput = Inputs.range([-180, 180], { value: 1, step: 1})
const latitude = Generators.input(latitudeInput)
```

```js
const effects = [
  new LightingEffect({
    ambientLight: new AmbientLight({color: [255, 255, 255], intensity: 1.0}),
    pointLight: new PointLight({color: [255, 255, 255], intensity: 0.8, position: [-0.144528, 49.739968, 80000]}),
    pointLight2: new PointLight({color: [255, 255, 255], intensity: 0.8, position: [-3.807751, 54.104682, 8000]})
  })
];

const globeView = new _GlobeView()
```

```js
const deckInstance = new DeckGL({
  container,
  views: globeView,
  initialViewState,
  getTooltip,
  effects,
  controller: true
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
  maxZoom: 12,
  pitch: 0,
  bearing: 0
};
```

```js
function getTooltip({object}) {
  if (!object) return null;
  const [lng, lat] = object.position;
  return `latitude: ${lat.toFixed(2)}
    longitude: ${lng.toFixed(2)}
    ${object.weight}%`;
}
```


```js
deckInstance.setProps({
  layers: [
    new SimpleMeshLayer({
        id: 'earth-sphere',
        data: [0],
        mesh: new SphereGeometry({radius: EARTH_RADIUS_METERS, nlat: 18, nlong: 36}),
        coordinateSystem: COORDINATE_SYSTEM.CARTESIAN,
        getPosition: [0, 0, 0],
        getColor: [255, 255, 255]
      }),
    new GeoJsonLayer({
      id: "base-map",
      data: land,
      // Styles
      stroked: false,
      filled: true,
      // opacity: 0.1,
      // getFillColor: [30, 80, 120]
      // lineWidthMinPixels: 1,
      // getLineColor: [60, 60, 60],
      getFillColor: [9, 16, 29]
    }),
    // new HeatmapLayer({
    //   id: 'heatmap',
    //   erf_data,
    //   getPosition: d => d.position,
    //   getWeight: d => d.weight,
    //   radiusPixels: 30,
    //   intensity: 1,
    //   pickable: true,
    // })
  ]
});
```


# 2019 Contrail ERF Proportion

Proportion of 2019 global contrail ERF per grid cell

Longitude ${longitudeInput}

Latitude ${latitudeInput}

<div class="card" style="margin: 0 -1rem;">

<figure style="max-width: none; position: relative;">
  <div id="container" style="border-radius: 8px; overflow: hidden; background: rgb(18, 35, 48); height: 800px; margin: 1rem 0; "></div>
  <!-- <figcaption>Data: <a href="https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data">Department for Transport</a></figcaption> -->
</figure>

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

