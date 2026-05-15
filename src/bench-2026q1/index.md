---
title: ContrailBench V1
---

<!-- ─── Styles ─────────────────────────────────────────────────────────────── -->
<style>
body { max-width: 860px; }

/* ── Toggle button groups ─────────────────────────────────── */
.ctrl-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.4rem 2rem;
  align-items: flex-start;
  margin: 1rem 0 0.75rem;
}
.ctrl-block { display: flex; flex-direction: column; gap: 5px; }
.ctrl-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--theme-foreground-muted);
}
.btn-group { display: flex; flex-wrap: wrap; gap: 5px; }
.btn-toggle {
  padding: 5px 13px;
  border-radius: 99px;
  border: 1.5px solid var(--theme-foreground-fainter);
  background: transparent;
  color: var(--theme-foreground-muted);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  white-space: nowrap;
}
.btn-toggle:hover:not(.dimmed) {
  border-color: var(--theme-foreground-faint);
  color: var(--theme-foreground);
}
.btn-toggle.active {
  background: var(--theme-foreground);
  border-color: var(--theme-foreground);
  color: var(--theme-background);
}
.btn-toggle.dimmed {
  opacity: 0.3;
  cursor: not-allowed;
}
.btn-toggle.source-iagos.active         { background: #161a26; border-color: #161a26; color: #fff; }
.btn-toggle.source-iagos:hover:not(.dimmed):not(.active) { border-color: #161a26; color: #161a26; }
.btn-toggle.source-gruan.active         { background: #1093ff; border-color: #1093ff; color: #fff; }
.btn-toggle.source-gruan:hover:not(.dimmed):not(.active) { border-color: #1093ff; color: #1093ff; }
.btn-toggle.source-cw.active            { background: #f26400; border-color: #f26400; color: #fff; }
.btn-toggle.source-cw:hover:not(.dimmed):not(.active)    { border-color: #f26400; color: #f26400; }
.ci-row { display: flex; align-items: center; gap: 7px; }
.ci-help {
  display: inline-flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--theme-foreground-fainter);
  color: var(--theme-foreground); font-size: 10px; font-weight: 700;
  cursor: help; position: relative; flex-shrink: 0;
}
.ci-help::after {
  content: attr(data-tip);
  display: none; position: absolute;
  left: 22px; top: -4px;
  background: var(--theme-foreground); color: var(--theme-background);
  padding: 7px 11px; border-radius: 4px;
  font-size: 12px; font-weight: 400; width: 300px;
  white-space: normal; line-height: 1.5; z-index: 100;
}
.ci-help:hover::after { display: block; }
.bench-downloads { font-size: 12px; color: var(--theme-foreground-muted); margin-top: 0.5rem; }
.bench-downloads a { color: var(--theme-foreground-muted); margin-right: 1rem; }
</style>

```js
import "../@components/observer.js";
```

```js
const allData = await FileAttachment("benchmarks.csv").csv({typed: true});
```

```js
const SOURCE_COLS = {
  "IAGOS":         { val: "iagos_hit_rate",        lo: "iagos_hit_rate_lo",         hi: "iagos_hit_rate_hi"         },
  "GRUAN":         { val: "gruan_hit_rate",         lo: "gruan_hit_rate_lo",         hi: "gruan_hit_rate_hi"         },
  "ContrailWatch": { val: "contrailwatch_hit_rate", lo: "contrailwatch_hit_rate_lo", hi: "contrailwatch_hit_rate_hi" },
};
const SOURCE_COLOR   = { "IAGOS": "#161a26", "GRUAN": "#1093ff", "ContrailWatch": "#f26400" };
const FORECAST_LABEL = { "contrails-org": "Contrails.org", "google": "Google" };
const SEASON_LABEL   = {
  annual: "January–December 2024",
  winter: "January/February/December 2024 (NH winter)",
  spring: "March–May 2024 (NH spring)",
  summer: "June–August 2024 (NH summer)",
  autumn: "September–November 2024 (NH autumn)",
};
const IAGOS_PCR = {
  "global/annual": 10.0, "global/winter": 11.5, "global/spring": 12.0,
  "global/summer":  7.0, "global/autumn":  9.5, "conus/annual":   9.5,
};
const BASE_URL = "https://storage.googleapis.com/contrailbench-public-data/2026Q1/benchmarks";
```

```js
function RadioButtons(choices, {value, format = d => d} = {}) {
  let current = value ?? choices[0];
  const el = html`<div class="btn-group"></div>`;
  const btns = {};
  for (const c of choices) {
    const b = html`<button type="button" class="btn-toggle${c === current ? " active" : ""}">${format(c)}</button>`;
    b.addEventListener("click", () => {
      if (b.classList.contains("dimmed")) return;
      Object.values(btns).forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      current = c;
      el.dispatchEvent(new Event("input", {bubbles: true}));
    });
    btns[c] = b;
    el.append(b);
  }
  Object.defineProperty(el, "value", { get: () => current });
  el._btns = btns;
  return el;
}

function CheckButtons(choices, {value = [], format = d => d, className = () => ""} = {}) {
  let current = [...value];
  const el = html`<div class="btn-group"></div>`;
  const btns = {};
  for (const c of choices) {
    const extra = className(c) ? ` ${className(c)}` : "";
    const b = html`<button type="button" class="btn-toggle${extra}${current.includes(c) ? " active" : ""}">${format(c)}</button>`;
    b.addEventListener("click", () => {
      if (b.classList.contains("dimmed")) return;
      const idx = current.indexOf(c);
      if (idx >= 0) current = current.filter(v => v !== c);
      else current = [...current, c];
      b.classList.toggle("active", current.includes(c));
      el.dispatchEvent(new Event("input", {bubbles: true}));
    });
    btns[c] = b;
    el.append(b);
  }
  Object.defineProperty(el, "value", {
    get: () => current,
    set: v => { current = [...v]; Object.entries(btns).forEach(([c, b]) => b.classList.toggle("active", current.includes(c))); },
  });
  el._btns = btns;
  el._setDimmed = (choice, on) => {
    btns[choice]?.classList.toggle("dimmed", on);
    if (on && current.includes(choice)) el.value = current.filter(v => v !== choice);
  };
  return el;
}

function ToggleButton(label, {value = true} = {}) {
  let current = value;
  const b = html`<button type="button" class="btn-toggle${current ? " active" : ""}">${label}</button>`;
  b.addEventListener("click", () => {
    current = !current;
    b.classList.toggle("active", current);
    b.dispatchEvent(new Event("input", {bubbles: true}));
  });
  Object.defineProperty(b, "value", { get: () => current });
  return b;
}
```

```js
const regionEl    = RadioButtons(["global","conus"], { value: "global", format: x => x === "global" ? "Global" : "Continental US" });
const region      = Generators.input(regionEl);

const seasonEl    = RadioButtons(["annual","winter","spring","summer","autumn"], {
  value: "annual",
  format: x => ({annual:"All year",winter:"Winter",spring:"Spring",summer:"Summer",autumn:"Autumn"})[x],
});
const season = Generators.input(seasonEl);

const forecastsEl = CheckButtons(["contrails-org","google"], {
  value: ["contrails-org"],
  format: x => FORECAST_LABEL[x],
});
const forecasts = Generators.input(forecastsEl);

const sourcesEl = CheckButtons(["IAGOS","GRUAN","ContrailWatch"], {
  value: ["IAGOS","GRUAN"],
  format: x => x,
  className: x => x === "IAGOS" ? "source-iagos" : x === "GRUAN" ? "source-gruan" : "source-cw",
});
const sources   = Generators.input(sourcesEl);

const showCIEl = ToggleButton("Confidence intervals", { value: false });
const showCI   = Generators.input(showCIEl);
```

```js
// Dim ContrailWatch when on Global
{ sourcesEl._setDimmed("ContrailWatch", region === "global"); }
```

```js
// Dim seasonal options when on CONUS (only annual available)
{
  for (const s of ["winter","spring","summer","autumn"])
    seasonEl._btns[s]?.classList.toggle("dimmed", region === "conus");
  if (region === "conus" && season !== "annual")
    seasonEl._btns["annual"]?.click();
}
```

# ContrailBench V1

```js
{
  const fLabel = forecasts.map(f => FORECAST_LABEL[f]).join(" & ") || "No forecast selected";
  const rLabel = region === "global" ? "Global" : "CONUS";
  display(html`<p style="margin:0 0 1rem; color:var(--theme-foreground-muted); font-size:14px;">
    ${fLabel} · ${rLabel}, ${SEASON_LABEL[season]}
  </p>`);
}
```

```js
html`<div class="ctrl-row">
  <div class="ctrl-block"><span class="ctrl-label">Region</span>${regionEl}</div>
  <div class="ctrl-block"><span class="ctrl-label">Season</span>${seasonEl}</div>
  <div class="ctrl-block"><span class="ctrl-label">Forecast</span>${forecastsEl}</div>
  <div class="ctrl-block"><span class="ctrl-label">Observation sources</span>${sourcesEl}</div>
  <div class="ctrl-block">
    <span class="ctrl-label">Options</span>
    <div class="ci-row">
      ${showCIEl}
      <span class="ci-help" data-tip="Error bars show 95% bias-corrected and accelerated (BCa) bootstrap confidence intervals, estimated by resampling daily flight data 1,000 times per forecast–dataset pair.">?</span>
    </div>
  </div>
</div>`
```

```js
const activeSources = region === "global" ? sources.filter(s => s !== "ContrailWatch") : sources;

const filtered = allData.filter(d =>
  d.region === region && d.season === season && forecasts.includes(d.forecast)
);

const long = filtered.flatMap(r =>
  activeSources.flatMap(src => {
    const c = SOURCE_COLS[src];
    const val = +r[c.val];
    if (isNaN(val)) return [];
    return [{
      buffer:      +r.horizontal_buffer,
      penalty:     +r.penalty     * 100,
      penalty_lo:  +r.penalty_lo  * 100,
      penalty_hi:  +r.penalty_hi  * 100,
      hit_rate:    val            * 100,
      hit_rate_lo: +r[c.lo]      * 100,
      hit_rate_hi: +r[c.hi]      * 100,
      source: src, forecast: r.forecast,
    }];
  })
);

const pcrRate = IAGOS_PCR[`${region}/${season}`] ?? null;
```

```js
const W = Math.min(width, 680);
const H = Math.round(W * 420 / 680);
const screenAngleDeg = Math.atan2(H / 100, W / 28) * 180 / Math.PI;

const marks = [
  Plot.line([[0,0],[28,28]], { stroke:"#939598", strokeDasharray:"4 3", strokeWidth:1 }),
  Plot.text([[1.5, 5.5]], { text:["Random forecast"], fill:"#939598", fontSize:13, rotate:-screenAngleDeg, textAnchor:"start" }),
];

if (pcrRate !== null) {
  marks.push(
    Plot.ruleX([pcrRate], { stroke:"#939598", strokeDasharray:"4 3", strokeWidth:1 }),
    Plot.text([[pcrRate + 0.7, 2]], { text:[`IAGOS PCR rate (${pcrRate}%)`], fill:"#939598", fontSize:13, textAnchor:"start" }),
  );
}

for (const src of activeSources) {
  const color = SOURCE_COLOR[src];
  for (const fcast of forecasts) {
    const rows = long.filter(d => d.source === src && d.forecast === fcast);
    if (!rows.length) continue;
    const dash = (forecasts.length > 1 && fcast === "google") ? "5 3" : null;
    marks.push(
      Plot.line(rows, { x:"penalty", y:"hit_rate", stroke:color, strokeWidth:2, strokeDasharray:dash }),
      Plot.dot(rows, {
        x:"penalty", y:"hit_rate", fill:color, r:4, tip:true,
        title: d => {
          const ftype = d.forecast === "contrails-org" ? "Deterministic" : "Probabilistic";
          const bufLabel = d.forecast === "contrails-org" ? "Buffer" : "Threshold";
          return `Source: ${d.source}\nForecast type: ${ftype}\n${bufLabel}: ${d.buffer}\nPenalty: ${d.penalty.toFixed(1)} %\nHit rate: ${d.hit_rate.toFixed(1)} %`;
        },
      }),
    );
    if (showCI) marks.push(
      Plot.ruleY(rows, { y:"hit_rate", x1:"penalty_lo", x2:"penalty_hi", stroke:color, strokeOpacity:0.4, strokeWidth:1.5 }),
      Plot.ruleX(rows, { x:"penalty", y1:"hit_rate_lo", y2:"hit_rate_hi", stroke:color, strokeOpacity:0.4, strokeWidth:1.5 }),
    );
  }
}

const chartEl = Plot.plot({
  className: "plot",
  width: W, height: H,
  style: { fontSize: "15px" },
  marginLeft: 60,
  marginBottom: 52,
  x: { label: "Flight distance in forecast PCR (%)", domain:[0,28], line:true, labelOffset: 42 },
  y: { label: "Hit rate (%)", domain:[0,100], line:true, labelOffset: 52 },
  marks,
});
display(chartEl);
```

```js
const legendSources   = activeSources.filter(s => long.some(d => d.source === s));
const legendForecasts = forecasts.filter(f => long.some(d => d.forecast === f));

html`<div style="font-size:12px; color:var(--theme-foreground-muted); margin-top:0.4rem;">
  ${legendForecasts.length > 1
    ? legendSources.map(src => html`<div style="display:flex; align-items:center; gap:1rem; margin-bottom:3px;">
        <span style="min-width:90px; font-weight:600; color:${SOURCE_COLOR[src]}">${src}</span>
        <span style="display:flex; align-items:center; gap:4px;">
          <svg width="26" height="10" style="vertical-align:middle">
            <line x1="0" y1="5" x2="26" y2="5" stroke="${SOURCE_COLOR[src]}" stroke-width="2"/>
            <circle cx="13" cy="5" r="3" fill="${SOURCE_COLOR[src]}"/>
          </svg> Contrails.org
        </span>
        <span style="display:flex; align-items:center; gap:4px;">
          <svg width="26" height="10" style="vertical-align:middle">
            <line x1="0" y1="5" x2="26" y2="5" stroke="${SOURCE_COLOR[src]}" stroke-width="2" stroke-dasharray="5 3"/>
            <circle cx="13" cy="5" r="3" fill="${SOURCE_COLOR[src]}"/>
          </svg> Google
        </span>
      </div>`)
    : html`<div style="display:flex; flex-wrap:wrap; gap:0.4rem 1.2rem;">
        ${legendSources.map(src => html`<span style="display:flex; align-items:center; gap:4px;">
          <svg width="26" height="10" style="vertical-align:middle">
            <line x1="0" y1="5" x2="26" y2="5" stroke="${SOURCE_COLOR[src]}" stroke-width="2.5"/>
            <circle cx="13" cy="5" r="3" fill="${SOURCE_COLOR[src]}"/>
          </svg> ${src}
        </span>`)}
      </div>`
  }
</div>`
```


```js
{
  const dlBtn = html`<button type="button" class="btn-toggle" style="margin-bottom:0.5rem">⬇ Download PNG</button>`;
  dlBtn.addEventListener("click", async () => {
    const svg = chartEl.querySelector ? (chartEl.querySelector("svg") ?? chartEl) : chartEl;
    const clone = svg.cloneNode(true);
    // Inline a style block so CSS vars resolve when rasterised off-page
    const st = document.createElement("style");
    st.textContent = `svg { font-family: system-ui, sans-serif; }`;
    clone.prepend(st);
    const svgStr = new XMLSerializer().serializeToString(clone);
    const svgBlob = new Blob([svgStr], {type: "image/svg+xml;charset=utf-8"});
    const chartUrl = URL.createObjectURL(svgBlob);

    const scale = 2;
    const chartW = parseInt(svg.getAttribute("width")) || W;
    const chartH = parseInt(svg.getAttribute("height")) || H;
    const pad = 16;
    const headerH = 72;

    // Build subtitle text
    const fLabel = forecasts.map(f => FORECAST_LABEL[f]).join(" & ") || "No forecast selected";
    const rLabel = region === "global" ? "Global" : "Continental US";
    const subtitle = `${fLabel} · ${rLabel}, ${SEASON_LABEL[season]}`;

    const canvas = document.createElement("canvas");
    canvas.width = chartW * scale;
    canvas.height = (headerH + chartH) * scale;
    const ctx = canvas.getContext("2d");
    ctx.scale(scale, scale);

    // White background
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, chartW, headerH + chartH);

    // Title
    ctx.fillStyle = "#161a26";
    ctx.font = "700 20px system-ui, sans-serif";
    ctx.fillText("ContrailBench V1", pad, pad + 20);

    // Subtitle
    ctx.fillStyle = "#888888";
    ctx.font = "400 13px system-ui, sans-serif";
    ctx.fillText(subtitle, pad, pad + 20 + 8 + 13);

    // Logo (top-right; skip silently if unavailable)
    try {
      const logoResp = await fetch("/@static/logo-black.svg");
      if (logoResp.ok) {
        const logoBlob = await logoResp.blob();
        const logoUrl = URL.createObjectURL(logoBlob);
        await new Promise(res => {
          const logoImg = new Image();
          logoImg.onload = () => {
            const logoH = 28;
            const logoW = logoImg.naturalWidth * (logoH / logoImg.naturalHeight);
            ctx.drawImage(logoImg, chartW - logoW - pad, (headerH - logoH) / 2, logoW, logoH);
            URL.revokeObjectURL(logoUrl);
            res();
          };
          logoImg.onerror = res;
          logoImg.src = logoUrl;
        });
      }
    } catch (_) {}

    // Chart SVG
    await new Promise((res, rej) => {
      const img = new Image();
      img.onload = () => { ctx.drawImage(img, 0, headerH); res(); };
      img.onerror = rej;
      img.src = chartUrl;
    });
    URL.revokeObjectURL(chartUrl);

    canvas.toBlob(b => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(b);
      a.download = `contrailbench-${region}-${season}.png`;
      a.click();
    }, "image/png");
  });
  display(dlBtn);
}
```

```js
html`<div class="bench-downloads">
  Download data:
  ${forecasts.map(f => {
    const parts = [region, ...(season !== "annual" ? [season] : []), f];
    const stem = parts.join("-");
    return html`<a href="${BASE_URL}/${stem}.pq">${FORECAST_LABEL[f]} ↓</a><a href="${BASE_URL}/${stem}-ci.pq">${FORECAST_LABEL[f]} CI ↓</a>`;
  })}
</div>`
```
