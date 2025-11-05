---
title: 2019 Contrail ERF Percentage
theme: slate
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
// import {NetCDFReader} from "npm:netcdfjs";
import maplibregl from "npm:maplibre-gl";
```
<!-- MapLibre Stylesheet -->
<link rel="stylesheet" href="npm:maplibre-gl/dist/maplibre-gl.css">
<script src="https://unpkg.com/@geomatico/maplibre-cog-protocol@0.5.0/dist/index.js"></script>

```js
// const erf = FileAttachment("2019-percent.nc").arrayBuffer().then((data) => new NetCDFReader(data));

// land
// const world = FileAttachment("countries-110m.json").json()
// const land = FileAttachment("countries-50m.json").json()

// map style
const mapstyle = FileAttachment("mapstyle.json")

const cogFile = FileAttachment("2019.tif")
```

```js
// function extractData(reader, varName) {
//   const variable = reader.getDataVariable(varName);
//   const lon = reader.getDataVariable('longitude');
//   const lat = reader.getDataVariable('latitude');

//   const data = [];
//   for (let i = 0; i < lat.length; i++) {
//     for (let j = 0; j < lon.length; j++) {
//       const value = variable[i * lon.length + j];
//       if (value !== null && value !== undefined) {
//         data.push({
//           position: [lon[j], lat[i]],
//           weight: value
//         });
//       }
//     }
//   }
//   return data;
// }
```
```js
// const land = topojson.feature(world, world.objects.land)
// const erf_percent = erf.getDataVariable("erf_percent")
// const erf_data = extractData(erf, "erf_percent")
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

// add COG protocol
maplibregl.addProtocol('cog', MaplibreCOGProtocol.cogProtocol);

const map = new maplibregl.Map({
  container: "map",
  zoom: 2,            // initial zoom
  maxZoom: 12,
  center: [-72, 42],  // initial center
  // style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
  // style: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
  // style: "https://demotiles.maplibre.org/globe.json"
  style: 'https://geoserveis.icgc.cat/contextmaps/icgc_mapa_base_gris_simplificat.json',
  // style: mapstyle.href
  // style: {
  //   version: 8,
  //   sources: {
  //     // erf: {
  //     //   type: 'raster',
  //     //   // url: `cog://https://storage.googleapis.com/contrails-301217-public-data/2019.tif`,
  //     //   url: `cog://${cogFile.href}`,
  //     //   tileSize: 256
  //     // },
  //     imageSource, {
  //       type: 'raster',
  //       url: 'cog://https://labs.geomatico.es/maplibre-cog-protocol/data/kriging.tif',
  //       tileSize: 256
  //     }
  //   },
  //   layers: [
  //     //   {
  //     //   id: 'erf',
  //     //   source: 'erf',
  //     //   type: 'raster'
  //     // },
  //     // {
  //     //   id: "osm",
  //     //   type: "raster",
  //     //   source: "osm"
  //     // },
  //     {
  //       id: 'imageLayer',
  //       source: 'imageSource',
  //       type: 'raster'
  //       }

  //   ]
  // },
});

// map.addControl(
//   new maplibregl.NavigationControl({
//     showZoom: true,
//   })
// );

/* ---------- 2.  Add the source and the heatmap layer ----------------------- */
map.on('load', () => {
  // map.addSource('erf', {
  //   type: 'raster',
  //   // url: `cog://https://storage.googleapis.com/contrails-301217-public-data/2019.tif`,
  //   url: `cog://${cogFile.href}`,
  //   tileSize: 256
  // });

  // map.addLayer({
  //   id: 'cogLayer',
  //   source: 'erf',
  //   type: 'raster'
  // });

  // MaplibreCOGProtocol.getCogMetadata(cogFile.href).then(metadata => {console.log(metadata)})

    map.addSource('imageSource', {
      type: 'raster',
      url: 'cog://https://labs.geomatico.es/maplibre-cog-protocol/data/kriging.tif#color:BrewerSpectral7,1.7084054885838,1.7919403772937,c',
      tileSize: 256
    });

    map.addLayer({
      source: 'imageSource',
      id: 'imageLayer',
      type: 'raster'
    });
});
```

# 2019 Contrail ERF Proportion

Proportion of 2019 global contrail ERF per grid cell

Longitude ${longitudeInput}

Latitude ${latitudeInput}


<div class="card">

<figure style="max-width: 95%; position: relative;">
  <div id="map" style="width: 90%; height: 550px;"></div>
  <!-- <div id="container" style="border-radius: 8px; overflow: hidden; background: rgb(18, 35, 48); height: 800px; margin: 1rem 0; "></div> -->
  <!-- <figcaption>Data: <a href="https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data">Department for Transport</a></figcaption> -->
</figure>

</div>

<div class="source">

[Source ↗︎](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/src/2019-global-erf-map/index.md)

</div>

