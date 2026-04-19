---
title: GRUAN Sonde map
---

<!-- ----- Dashboard imports ----- -->

<!-- Add any custom styles for this dashboard -->
<!-- Other global styles in `style.css` -->
<style></style>


```js
// Resize observer. Required to update parent `iframe` height dynamically.
// See README for script tag required in post body.
import "../@components/observer.js";
```

<!-- ----------------------------- -->

## Over 100,000 Sonde Profiles from GRAUN

<!-- Data -->
```js
const sites = FileAttachment("gruan-sites.csv").csv({typed: true});
const world110m = FileAttachment("../@static/110m.topojson").json();
```

<!-- Processing -->
```js
// Load the world map data (TopoJSON)
const countries110m = topojson.feature(world110m, world110m.objects.countries)
```

<!-- Input -->
```js
const longitudeInput = Inputs.range([-180, 180], {label: "longitude", step: 1, value: 90})
const longitude = Generators.input(longitudeInput)

const siteColors = {
  "certified": "#1093ff",  // tropo-blue
  "uncertified": "#f26400", // orange
  "historical": "#99a1af", // grey
  "candidate": "#162440", // meso blue
}
```

<!-- Map -->
```js
Plot.plot({
  className: "plot",
  width,
  height: 500,
  color: {
    legend: true,
    domain: Object.keys(siteColors),
    range: Object.values(siteColors),
  },
  projection: {
    type: "orthographic",
    rotate: [-longitude, 0]
  },
  marks: [
    // Graticule - need to use d3 if we want more coarse
    Plot.graticule({
      strokeOpacity: 0.1,
    }),

    // Land topojson
    Plot.geo(countries110m, {
        fill: "#a5b3ab",
        stroke: "#ffffff",
        strokeWidth: 0.5
    }),

    // Labels - Matching map_show_labels: true
    Plot.text(sites, {
      x: "longitude",
      y: "latitude",
      text: "Station Code",
      dx: 18,
      fontSize: 12,
    }),

    // Stations
    Plot.dot(sites, {
      x: "longitude",
      y: "latitude",
      r: (site) => site["Number of Sonde Profiles"] > 20000 ? 20 :
          site["Number of Sonde Profiles"] > 10000 ? 10 : 6,
      fill: "GRUAN Status",
      stroke: "#000000",
      strokeWidth: 0.5,
      tip: {fontSize: 14},
      title: s => `${s.full_name} (${s["Station Code"]})\n${s["GRUAN Status"]}\n\nNumber of Sonde Profiles: ${s["Number of Sonde Profiles"]}\nAltitude: ${s["Altitude"]}\nFirst Launch: ${s["First Launch"]}\nLatest Launch: ${s["Latest Launch"]}`

    })
  ]
})
```

${longitudeInput}
