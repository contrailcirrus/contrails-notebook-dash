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
```

```js
const erf = FileAttachment("2019-percent.nc").arrayBuffer().then((data) => new NetCDFReader(data));

// land
const world = FileAttachment("countries-110m.json").json()
```

```js
// reverse dimensions
// erf.header.variables[0].dimensions[0] = 1
// erf.header.variables[0].dimensions[1] = 0
// console.log(erf.getDataVariable("erf_percent"))
// console.log(erf.header)
const land = topojson.feature(world, world.objects.land)

const longitudeInput = Inputs.range([-180, 180], { value: 1, step: 1})
const longitude = Generators.input(longitudeInput)

const latitudeInput = Inputs.range([-180, 180], { value: 1, step: 1})
const latitude = Generators.input(latitudeInput)
```

# 2019 Contrail ERF Proportion

Proportion of 2019 global contrail ERF per grid cell

## Orthographic

Longitude ${longitudeInput}

Latitude ${latitudeInput}

```js
Plot.plot({
  projection: {type: "orthographic", rotate: [-longitude, latitudeInput]},
  color: {
    label: "ERF (%)",
    legend: true,
    // scheme: "reds"
  },
  marks: [
    Plot.sphere(),
    Plot.raster(erf.getDataVariable("erf_percent"), {
      width: erf.header.dimensions[0].size,
      height: erf.header.dimensions[1].size,
      x1: -180,
      y1: -90,
      x2: 180,
      y2: 90,
      interpolate: "barycentric",
      clip: "sphere"
    }),
    Plot.geo(land, {fill: "currentColor", fillOpacity: 0.2}),
  ]
})
```

## Equal Earth

```js

Plot.plot({
  projection: "equal-earth",
  color: {
    label: "ERF (%)",
    legend: true,
    scheme: "reds"
  },
  marks: [
    Plot.raster(erf.getDataVariable("erf_percent"), {
      width: erf.header.dimensions[0].size,
      height: erf.header.dimensions[1].size,
      x1: -180,
      y1: -90,
      x2: 180,
      y2: 90,
      interpolate: "barycentric",
      clip: "sphere"
    }),
    Plot.graticule({stroke: "black"})
  ]
})
```
<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>
