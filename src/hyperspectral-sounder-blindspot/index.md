---
title: Hyperspectral sounder blind spot
footer: false
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

<!-- Data -->
```js
const data = [
  {pressure: 1000, error: 15, temp_error: 1.2, alt_ft: 0,     alt_label: "Surface"},
  {pressure: 800,  error: 18, temp_error: 0.9, alt_ft: 6500,  alt_label: "6,500 ft"},
  {pressure: 700,  error: 21, temp_error: 0.8, alt_ft: 10000, alt_label: "10,000 ft"},
  {pressure: 600,  error: 19, temp_error: 0.8, alt_ft: 14000, alt_label: "14,000 ft"},
  {pressure: 500,  error: 24, temp_error: 0.9, alt_ft: 18000, alt_label: "18,000 ft"},
  {pressure: 400,  error: 29, temp_error: 1.0, alt_ft: 24000, alt_label: "24,000 ft"},
  {pressure: 300,  error: 30, temp_error: 1.2, alt_ft: 30000, alt_label: "30,000 ft"},
  {pressure: 200,  error: 46, temp_error: 1.5, alt_ft: 39000, alt_label: "39,000 ft"},
  {pressure: 100,  error: 86, temp_error: 1.8, alt_ft: 53000, alt_label: "53,000 ft"}
];
```

```js
const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(d3.csvFormat(data));
```

## The hyperspectral sounder blind spot at cruise altitudes

<div class="small">
Suomi-NPP satellite water vapor and temperature errors compared to collocated radiosondes.
</div>

<!-- Plot -->
```js
Plot.plot({
    className: "plot",
    style: {
      fontFamily: "Aeonik, sans-serif",
      fontSize: "16px",
    },
    width: 800,
    height: 500,
    marginLeft: 100,
    marginBottom: 60,
    x: {
      domain: [0, 100],
      label: "RMS Error (Kelvin for Temperature, % for Water Vapor)",
      grid: true
    },
    y: {
      label: "Altitude",
      grid: true,
      tickFormat: d => `${d.toLocaleString()} ft`
    },
    marks: [
      // Cruise altitude shading
      Plot.rect([{x1: 0, x2: 100, y1: 30000, y2: 40000}], {
        x1: "x1", x2: "x2", y1: "y1", y2: "y2",
        fill: "#99a1af",
        fillOpacity: 0.1
      }),
      Plot.text([{x: 98, y: 35000}], {
        x: "x", y: "y",
        text: () => "Typical cruise altitude\n of commercial aircraft",
        fontSize: 16,
        fontWeight: "bold",
        textAnchor: "end",
        lineHeight: 1.2
      }),

      // Temperature series (Tropo Blue)
      Plot.line(data, {x: "temp_error", y: "alt_ft", stroke: "#1093FF", strokeWidth: 3}),
      Plot.dot(data, {
        x: "temp_error",
        y: "alt_ft",
        fill: "#1093FF",
        r: 6,
        tip: true,
        title: d => `Altitude: ${d.alt_label}\nPressure: ${d.pressure} hPa\nError: ${d.temp_error} K`
      }),

      // Water vapor series (Orange)
      Plot.line(data, {x: "error", y: "alt_ft", stroke: "#f26400", strokeWidth: 3}),
      Plot.dot(data, {
        x: "error",
        y: "alt_ft",
        fill: "#f26400",
        r: 6,
        tip: true,
        title: d => `Altitude: ${d.alt_label}\nPressure: ${d.pressure} hPa\nError: ${d.error}%`
      }),

      // Direct line labels
      Plot.text([{x: 3, y: 10000}], {
        x: "x", y: "y", text: () => "Temperature",
        fill: "#1093FF", fontWeight: "bold", textAnchor: "start", dx: 5
      }),
      Plot.text([{x: 22, y: 10000}], {
        x: "x", y: "y", text: () => "Water Vapor",
        fill: "#f26400", fontWeight: "bold", textAnchor: "start", dx: 10
      })
    ]
  })
```

<div class="small">

<a href="${csvContent}" download="nalli_2018_sounder_error.csv">Data</a> adapted from
[Nalli et al. (2018)](https://doi.org/10.1109/TGRS.2017.2744558)

</div>
