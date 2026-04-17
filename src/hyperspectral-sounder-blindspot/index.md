---
title: The hyperspectral sounder blind spot at cruise altitude
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

```js
function renderChart() {
  const wrapper = document.createElement("div");
  wrapper.style.width = "100%";
  wrapper.style.maxWidth = "800px";
  wrapper.style.margin = "0 auto";

  const plot = Plot.plot({
    title: htl.html`<div style="font-family: 'Aeonik', sans-serif; font-size: clamp(20px, 4vw, 24px); font-weight: bold; color: #161A26; margin-bottom: 5px; line-height: 1.2;">
      >_ The hyperspectral sounder blind spot at cruise altitudes
    </div>`,
    subtitle: htl.html`<div style="font-family: 'Aeonik', sans-serif; font-size: clamp(16px, 2vw, 16px); font-weight: normal; color: #161A26; margin-bottom: 15px; line-height: 1.4;">
      Suomi-NPP satellite water vapor and temperature errors compared to collocated global radiosondes
    </div>`,
    style: {
      fontFamily: "Aeonik, sans-serif",
      fontSize: "16px",
      color: "#161A26",
      background: "transparent"
    },
    width: 800,
    height: 500,
    marginLeft: 100,
    marginBottom: 60,
    x: {
      domain: [0, 100],
      label: "RMS Error (% for Water Vapor, Kelvin for Temperature)",
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
        fill: "#F26400",
        fillOpacity: 0.1
      }),
      Plot.text([{x: 98, y: 35000}], {
        x: "x", y: "y",
        text: () => "Typical cruise altitude\n of commercial aircraft",
        fill: "#F26400",
        fontSize: 16,
        fontWeight: "bold",
        textAnchor: "end",
        lineHeight: 1.2
      }),

      // Temperature series (Tropo Blue)
      Plot.line(data, {x: "temp_error", y: "alt_ft", stroke: "#1093FF", strokeWidth: 3}),
      Plot.dot(data, {
        x: "temp_error", y: "alt_ft",
        fill: "#1093FF", r: 6, tip: true,
        title: d => `Altitude: ${d.alt_label}\nPressure: ${d.pressure} hPa\nTemp Error: ${d.temp_error} K`
      }),

      // Water vapor series (Meso Blue)
      Plot.line(data, {x: "error", y: "alt_ft", stroke: "#162440", strokeWidth: 3}),
      Plot.dot(data, {
        x: "error", y: "alt_ft",
        fill: "#162440", r: 6, tip: true,
        title: d => `Altitude: ${d.alt_label}\nPressure: ${d.pressure} hPa\nWater Vapor Error: ${d.error}%`
      }),

      // Direct line labels
      Plot.text([{x: 3, y: 10000}], {
        x: "x", y: "y", text: () => "Temperature",
        fill: "#1093FF", fontWeight: "bold", textAnchor: "start", dx: 5
      }),
      Plot.text([{x: 22, y: 10000}], {
        x: "x", y: "y", text: () => "Water Vapor",
        fill: "#162440", fontWeight: "bold", textAnchor: "start", dx: 10
      })
    ]
  });

  // Footer with citation + logo
  const footer = document.createElement("div");
  footer.style.display = "flex";
  footer.style.justifyContent = "space-between";
  footer.style.alignItems = "flex-end";
  footer.style.marginTop = "10px";
  footer.style.gap = "15px";

  const citation = document.createElement("div");
  citation.style.fontFamily = "Aeonik, sans-serif";
  citation.style.fontSize = "clamp(11px, 2vw, 14px)";
  citation.style.color = "#161A26";
  citation.style.lineHeight = "1.3";
  citation.innerHTML = `<a href="${csvContent}" download="nalli_2018_sounder_error.csv" style="color: #1093FF; text-decoration: underline; font-weight: bold; cursor: pointer;" title="Download CSV">Data</a> adapted from <a href="https://doi.org/10.1109/TGRS.2017.2744558" target="_blank" style="color: #1093FF; text-decoration: none; font-weight: bold;">Nalli et al. (2018)</a>`;

  const logoLink = document.createElement("a");
  logoLink.href = "https://contrails.org";
  logoLink.target = "_blank";
  logoLink.style.width = "25%";
  logoLink.style.minWidth = "80px";
  logoLink.style.maxWidth = "120px";
  logoLink.style.flexShrink = "0";

  const logoImg = document.createElement("img");
  logoImg.src = "https://storage.ghost.io/c/0e/93/0e93dd1b-ada9-4033-b4c9-385cc66de4f3/content/images/2026/04/ContrailsOrg_Logo_Full_Black.svg";
  logoImg.alt = "Contrails.org";
  logoImg.style.width = "100%";
  logoImg.style.display = "block";

  logoLink.appendChild(logoImg);
  footer.appendChild(citation);
  footer.appendChild(logoLink);
  wrapper.appendChild(plot);
  wrapper.appendChild(footer);

  return wrapper;
}
```

<div class="card">${renderChart()}</div>
