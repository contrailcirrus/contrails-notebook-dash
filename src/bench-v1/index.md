---
title: ContrailBench v1
---

<!-- ─── Styles ─────────────────────────────────────────────────────────────── -->
<style>
  .share {
    position: absolute;
    right: 0;
    top: 0;

    form {
      width: unset;
    }
    svg {
      margin-bottom: -3px;
    }
    /* "Copied!" text */
    .observablehq-pre-copied::before {
      padding: 0px 8px;
    }
  }
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
  .btn-toggle:hover:not(.dimmed):not(.active) {
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
  .bench-downloads {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    gap: 1rem;
    font-size: 12px;
    color: var(--theme-foreground-muted);
    margin: 1rem 0;
  }
  .bench-downloads-links { display: flex; flex-wrap: wrap; gap: 0 1rem; align-items: center; }
  .bench-downloads a { color: var(--theme-foreground-muted); }
</style>

```js
import "../@components/observer.js";
```

```js
const allData = await FileAttachment("benchmarks.csv").csv({ typed: true });
```

```js
const SOURCE_COLS = {
  IAGOS: {
    val: "iagos_hit_rate",
    lo: "iagos_hit_rate_lo",
    hi: "iagos_hit_rate_hi",
  },
  GRUAN: {
    val: "gruan_hit_rate",
    lo: "gruan_hit_rate_lo",
    hi: "gruan_hit_rate_hi",
  },
  ContrailWatch: {
    val: "contrailwatch_hit_rate",
    lo: "contrailwatch_hit_rate_lo",
    hi: "contrailwatch_hit_rate_hi",
  },
};
const SOURCE_COLOR = {
  IAGOS: "#161a26",
  GRUAN: "#1093ff",
  ContrailWatch: "#f26400",
};
const FORECAST_LABEL = { "contrails-org": "Contrails.org", google: "Google" };
const SEASON_LABEL = {
  annual: "January–December 2024",
  winter: "January/February/December 2024 (NH winter)",
  spring: "March–May 2024 (NH spring)",
  summer: "June–August 2024 (NH summer)",
  autumn: "September–November 2024 (NH autumn)",
};
const IAGOS_PCR = {
  "global/annual": 10.0,
  "global/winter": 11.5,
  "global/spring": 12.0,
  "global/summer": 7.0,
  "global/autumn": 9.5,
  "conus/annual": 9.5,
};
```

```js
function RadioButtons(choices, { value, format = (d) => d } = {}) {
  let current = value ?? choices[0];
  const el = html`<div class="btn-group"></div>`;
  const btns = {};
  for (const c of choices) {
    const b = html`<button
      type="button"
      class="btn-toggle${c === current ? " active" : ""}"
    >
      ${format(c)}
    </button>`;
    b.addEventListener("click", () => {
      if (b.classList.contains("dimmed")) return;
      Object.values(btns).forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      current = c;
      el.dispatchEvent(new Event("input", { bubbles: true }));
    });
    btns[c] = b;
    el.append(b);
  }
  Object.defineProperty(el, "value", { get: () => current });
  el._btns = btns;
  return el;
}

function CheckButtons(
  choices,
  { value = [], format = (d) => d, className = () => "" } = {},
) {
  let current = [...value];
  const el = html`<div class="btn-group"></div>`;
  const btns = {};
  for (const c of choices) {
    const extra = className(c) ? ` ${className(c)}` : "";
    const b = html`<button
      type="button"
      class="btn-toggle${extra}${current.includes(c) ? " active" : ""}"
    >
      ${format(c)}
    </button>`;
    b.addEventListener("click", () => {
      if (b.classList.contains("dimmed")) return;
      const idx = current.indexOf(c);
      if (idx >= 0) current = current.filter((v) => v !== c);
      else current = [...current, c];
      b.classList.toggle("active", current.includes(c));
      el.dispatchEvent(new Event("input", { bubbles: true }));
    });
    btns[c] = b;
    el.append(b);
  }
  Object.defineProperty(el, "value", {
    get: () => current,
    set: (v) => {
      current = [...v];
      Object.entries(btns).forEach(([c, b]) =>
        b.classList.toggle("active", current.includes(c)),
      );
    },
  });
  el._btns = btns;
  el._setDimmed = (choice, on) => {
    btns[choice]?.classList.toggle("dimmed", on);
    if (on && current.includes(choice))
      el.value = current.filter((v) => v !== choice);
  };
  return el;
}

function ToggleButton(label, { value = true } = {}) {
  let current = value;
  const b = html`<button
    type="button"
    class="btn-toggle${current ? " active" : ""}"
  >
    ${label}
  </button>`;
  b.addEventListener("click", () => {
    current = !current;
    b.classList.toggle("active", current);
    b.dispatchEvent(new Event("input", { bubbles: true }));
  });
  Object.defineProperty(b, "value", { get: () => current });
  return b;
}
```

```js
// Read initial state from URL query params so shared links restore the view
const urlParams = new URLSearchParams(location.search);
const initRegion = (() => {
  const v = urlParams.get("region");
  return ["global", "conus"].includes(v) ? v : "global";
})();
const initSeason = (() => {
  const v = urlParams.get("season");
  return ["annual", "winter", "spring", "summer", "autumn"].includes(v)
    ? v
    : "annual";
})();
const initForecasts = urlParams.has("forecasts")
  ? urlParams
      .get("forecasts")
      .split(",")
      .filter((x) => ["contrails-org", "google"].includes(x))
  : ["contrails-org"];
const initSources = urlParams.has("sources")
  ? urlParams
      .get("sources")
      .split(",")
      .filter((x) => ["IAGOS", "GRUAN", "ContrailWatch"].includes(x))
  : ["IAGOS", "GRUAN"];
const initShowCI = urlParams.get("ci") === "1";
```

```js
const regionEl = RadioButtons(["global", "conus"], {
  value: initRegion,
  format: (x) => (x === "global" ? "Global" : "Continental US"),
});
const region = Generators.input(regionEl);

const seasonEl = RadioButtons(
  ["annual", "winter", "spring", "summer", "autumn"],
  {
    value: initSeason,
    format: (x) =>
      ({
        annual: "All year",
        winter: "Winter",
        spring: "Spring",
        summer: "Summer",
        autumn: "Autumn",
      })[x],
  },
);
const season = Generators.input(seasonEl);

const forecastsEl = CheckButtons(["contrails-org", "google"], {
  value: initForecasts,
  format: (x) => FORECAST_LABEL[x],
});
const forecasts = Generators.input(forecastsEl);

const sourcesEl = CheckButtons(["IAGOS", "GRUAN", "ContrailWatch"], {
  value: initSources,
  format: (x) => x,
  className: (x) =>
    x === "IAGOS"
      ? "source-iagos"
      : x === "GRUAN"
      ? "source-gruan"
      : "source-cw",
});
const sources = Generators.input(sourcesEl);

const showCIEl = ToggleButton("Confidence intervals", { value: initShowCI });
const showCI = Generators.input(showCIEl);
```

```js
// Dim ContrailWatch when on Global
{
  sourcesEl._setDimmed("ContrailWatch", region === "global");
}
```

```js
// Dim seasonal options when on CONUS (only annual available)
{
  for (const s of ["winter", "spring", "summer", "autumn"])
    seasonEl._btns[s]?.classList.toggle("dimmed", region === "conus");
  if (region === "conus" && season !== "annual")
    seasonEl._btns["annual"]?.click();
}
```

<!-- Share -->
```js
const currentScenario = {
  region: region,
  season: season,
  forecasts: forecasts,
  sources: sources,
  ci: showCI
}
```

```js
const showCopied = () => {
  const button = document.getElementById("sharecontainer").querySelector('button');

  // hack to steal the "Copied" text and animation from the <pre> code blocks
  button.classList.add("observablehq-pre-copied");
  button.addEventListener("animationend", () => button.classList.remove("observablehq-pre-copied"), { once: true });
}

const shareScenario = async () => {
  const baseUrl = location.origin + location.pathname;
  const params = new URLSearchParams(currentScenario);
  const paramString = params.toString();
  const shareUrl = `${baseUrl}?${paramString}`

  try {
    await navigator.share({
      title: "ContrailBench v1",
      url: shareUrl
    })
  } catch (e) {
    try {
      await navigator.clipboard.writeText(shareUrl);
      showCopied()
      // alert("Copied scenario URL to clipboard")
    } catch (error) {
      console.error(error)
    }
  }
}

const shareButtonText =html`Share
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path d="M 21 5 A 3 3 0 1 1 15 5 A 3 3 0 1 1 21 5 M 9 12 A 3 3 0 1 1 3 12 A 3 3 0 1 1 9 12 M 21 19 A 3 3 0 1 1 15 19 A 3 3 0 1 1 21 19 M 8.5 10.5 L 15.5 6.5 M 8.5 13.5 L 15.5 17.5" stroke-width="2"/>
    </svg>`
const shareButton = Inputs.button(shareButtonText, {value: null, reduce: shareScenario});
```

# ContrailBench

### `v1`

<div id="sharecontainer" class="share">${shareButton}</div>

<div class="card">

## Region

${regionEl}

## Season (Northern Hemisphere)

${seasonEl}

## Forecast

${forecastsEl}

## Observation sources

${sourcesEl}

## Options

${showCIEl} <span class="ci-help" data-tip="Error bars show 95% bias-corrected and accelerated (BCa) bootstrap confidence intervals, estimated by resampling daily flight data 1,000 times per forecast–dataset pair.">?</span>

</div>

```js
const activeSources =
  region === "global" ? sources.filter((s) => s !== "ContrailWatch") : sources;

const filtered = allData.filter(
  (d) =>
    d.region === region &&
    d.season === season &&
    forecasts.includes(d.forecast),
);

const long = filtered.flatMap((r) =>
  activeSources.flatMap((src) => {
    const c = SOURCE_COLS[src];
    const val = +r[c.val];
    if (isNaN(val)) return [];
    return [
      {
        horizontal_buffer: +r.horizontal_buffer,
        probability_threshold: +r.probability_threshold,
        penalty: +r.penalty * 100,
        penalty_lo: +r.penalty_lo * 100,
        penalty_hi: +r.penalty_hi * 100,
        hit_rate: val * 100,
        hit_rate_lo: +r[c.lo] * 100,
        hit_rate_hi: +r[c.hi] * 100,
        source: src,
        forecast: r.forecast,
      },
    ];
  }),
);

const pcrRate = IAGOS_PCR[`${region}/${season}`] ?? null;
```

```js
const W = Math.min(width - 32, 860);  // subtracting padding of 2rem = 32px
const H = Math.max(250, Math.round(W * (460 / 860)));
const screenAngleDeg = (Math.atan2(H / 100, W / 28) * 180) / Math.PI;

const marks = [
  Plot.line(
    [
      [0, 0],
      [28, 28],
    ],
    { stroke: "#939598", strokeDasharray: "4 3", strokeWidth: 1 },
  ),
  Plot.text([[1.5, 5.5]], {
    text: ["Random forecast"],
    fill: "#939598",
    fontSize: 13,
    rotate: -screenAngleDeg,
    textAnchor: "start",
  }),
];

if (pcrRate !== null) {
  marks.push(
    Plot.ruleX([pcrRate], {
      stroke: "#939598",
      strokeDasharray: "4 3",
      strokeWidth: 1,
    }),
    Plot.text([[pcrRate + 0.3, 3.5]], {
      text: [`IAGOS PCR rate (${pcrRate}%)`],
      fill: "#939598",
      fontSize: 13,
      textAnchor: "start",
    }),
  );
}

for (const src of activeSources) {
  const color = SOURCE_COLOR[src];
  for (const fcast of forecasts) {
    const rows = long.filter((d) => d.source === src && d.forecast === fcast);
    if (!rows.length) continue;
    const dash = forecasts.length > 1 && fcast === "google" ? "5 3" : null;
    marks.push(
      Plot.line(rows, {
        x: "penalty",
        y: "hit_rate",
        stroke: color,
        strokeWidth: 2,
        strokeDasharray: dash,
      }),
      Plot.dot(rows, { x: "penalty", y: "hit_rate", fill: color, r: 4 }),
    );
    if (showCI)
      marks.push(
        Plot.ruleY(rows, {
          y: "hit_rate",
          x1: "penalty_lo",
          x2: "penalty_hi",
          stroke: color,
          strokeOpacity: 0.4,
          strokeWidth: 1.5,
        }),
        Plot.ruleX(rows, {
          x: "penalty",
          y1: "hit_rate_lo",
          y2: "hit_rate_hi",
          stroke: color,
          strokeOpacity: 0.4,
          strokeWidth: 1.5,
        }),
      );
  }
}

// Single global tooltip across all (source, forecast) groups — avoids the
// duplicated tips that appear when per-mark tip:true on overlapping points
// each spawn their own tooltip.
marks.push(
  Plot.tip(
    long,
    Plot.pointer({
      anchor: "top",
      x: "penalty",
      y: "hit_rate",
      title: (d) => {
        const fName = FORECAST_LABEL[d.forecast];
        const ftype =
          d.forecast === "contrails-org" ? "Deterministic" : "Probabilistic";
        const paramLine =
          d.forecast === "contrails-org"
            ? `Horizontal Buffer: +${d.horizontal_buffer} 0.25\u00b0 \u00d7 0.25\u00b0 cell`
            : `Probability Threshold: ${(d.probability_threshold * 100).toFixed(
                1,
              )}%`;
        return `Forecast: ${fName}\nSource: ${
          d.source
        }\nType: ${ftype}\n${paramLine}\nPenalty: ${d.penalty.toFixed(
          1,
        )} %\nHit rate: ${d.hit_rate.toFixed(1)} %`;
      },
    }),
  ),
);

if (forecasts.length > 1) {
  marks.push(
    Plot.line(
      [
        [0.5, 95],
        [3, 95],
      ],
      { stroke: "#888", strokeWidth: 2, className: "forecast-inline-legend" },
    ),
    Plot.text([[3.5, 95]], {
      text: ["Contrails.org"],
      fill: "#888",
      fontSize: 13,
      textAnchor: "start",
      className: "forecast-inline-legend",
    }),
    Plot.line(
      [
        [0.5, 88],
        [3, 88],
      ],
      {
        stroke: "#888",
        strokeWidth: 2,
        strokeDasharray: "5 3",
        className: "forecast-inline-legend",
      },
    ),
    Plot.text([[3.5, 88]], {
      text: ["Google"],
      fill: "#888",
      fontSize: 13,
      textAnchor: "start",
      className: "forecast-inline-legend",
    }),
  );
}

const chartEl = Plot.plot({
  className: "plot",
  width: W,
  height: H,
  style: { fontSize: "15px" },
  marginLeft: 40,
  marginRight: 5,
  marginBottom: 52,
  marginTop: 24,
  x: {
    label: "Flight distance in forecast PCR (%)",
    domain: [0, 32],
    line: true,
    labelOffset: 42,
  },
  y: { label: "Hit rate (%)", domain: [0, 100], line: true, labelOffset: 5 },
  marks,
});
```


```js
const csvUrl = await FileAttachment("benchmarks.csv").url();
const logoUrl = await FileAttachment("../@static/logo-black.svg").url();; // PNG download always uses light-mode logo

const pngLink = html`<a href="#">↓ Download PNG</a>`;
const csvLink = html`<a href="${csvUrl}" download="contrailbench-v1.csv"
  >↓ Download data (CSV)</a
>`;

pngLink.addEventListener("click", async (e) => {
  e.preventDefault();
  const svg = chartEl.querySelector
    ? chartEl.querySelector("svg") ?? chartEl
    : chartEl;
  const clone = svg.cloneNode(true);
  // Remove in-chart forecast legend — will be redrawn as canvas overlay
  for (const el of clone.querySelectorAll(".forecast-inline-legend"))
    el.remove();
  const st = document.createElement("style");
  st.textContent = `svg { font-family: system-ui, sans-serif; }`;
  clone.prepend(st);
  const svgStr = new XMLSerializer().serializeToString(clone);
  const svgBlob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
  const chartUrl = URL.createObjectURL(svgBlob);

  const scale = 3;
  const chartW = parseInt(svg.getAttribute("width")) || W;
  const chartH = parseInt(svg.getAttribute("height")) || H;
  const pad = 16;
  const headerH = 72;
  const chartMarginLeft = 72; // matches Plot.plot marginLeft
  const chartMarginTop = 24; // matches Plot.plot marginTop

  const fLabel =
    forecasts.map((f) => FORECAST_LABEL[f]).join(" & ") ||
    "No forecast selected";
  const rLabel = region === "global" ? "Global" : "Continental US";
  const legendSrcItems = activeSources.filter((s) =>
    long.some((d) => d.source === s),
  );
  const legendFcastItems = forecasts.length > 1 ? forecasts : [];

  const canvas = document.createElement("canvas");
  canvas.width = chartW * scale;
  canvas.height = (headerH + chartH) * scale;
  const ctx = canvas.getContext("2d");
  ctx.scale(scale, scale);

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, chartW, headerH + chartH);
  await document.fonts.ready;

  // Title
  ctx.fillStyle = "#161a26";
  ctx.font = "700 20px Aeonik, system-ui, sans-serif";
  ctx.fillText("ContrailBench v1", pad, pad + 20);

  // Subtitle with colored source names
  let sx = pad;
  const subY = pad + 20 + 8 + 13;
  ctx.fillStyle = "#888888";
  ctx.font = "400 13px Aeonik, system-ui, sans-serif";
  const subtitleBase = `${fLabel} · ${rLabel}, ${SEASON_LABEL[season]}`;
  ctx.fillText(subtitleBase, sx, subY);
  sx += ctx.measureText(subtitleBase).width;
  if (legendSrcItems.length > 0) {
    ctx.fillStyle = "#888888";
    ctx.fillText(" · ", sx, subY);
    sx += ctx.measureText(" · ").width;
    for (let i = 0; i < legendSrcItems.length; i++) {
      if (i > 0) {
        ctx.fillStyle = "#888888";
        ctx.font = "400 13px Aeonik, system-ui, sans-serif";
        ctx.fillText(" · ", sx, subY);
        sx += ctx.measureText(" · ").width;
      }
      const src = legendSrcItems[i];
      ctx.fillStyle = SOURCE_COLOR[src];
      ctx.font = "700 13px Aeonik, system-ui, sans-serif";
      ctx.fillText(src, sx, subY);
      sx += ctx.measureText(src).width;
      ctx.font = "400 13px Aeonik, system-ui, sans-serif";
    }
  }

  // Logo: load /@static/logo-black.svg and draw in top-right
  const logoH = 24;
  const logoW = Math.round((logoH * 796.795) / 132.633);
  await new Promise((res) => {
    const logoImg = new Image();
    logoImg.onload = () => {
      ctx.drawImage(
        logoImg,
        chartW - logoW - pad,
        (headerH - logoH) / 2,
        logoW,
        logoH,
      );
      res();
    };
    logoImg.onerror = (e) => {
      console.warn("PNG logo failed to load", e);
      res();
    };
    logoImg.src = logoUrl;
  });

  // Chart SVG
  await new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, 0, headerH);
      res();
    };
    img.onerror = rej;
    img.src = chartUrl;
  });
  URL.revokeObjectURL(chartUrl);

  // Legend overlaid on top-left of chart plot area
  let lx = chartMarginLeft + 8;
  let ly = headerH + chartMarginTop + 8;
  ctx.font = "400 13px Aeonik, system-ui, sans-serif";
  for (const src of legendSrcItems) {
    const color = SOURCE_COLOR[src];
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(lx, ly + 5);
    ctx.lineTo(lx + 22, ly + 5);
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(lx + 11, ly + 5, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = color;
    ctx.fillText(src, lx + 28, ly + 9);
    ly += 20;
  }
  if (legendFcastItems.length > 0) {
    ly += 4;
    for (const fcast of legendFcastItems) {
      ctx.strokeStyle = "#888";
      ctx.lineWidth = 2;
      ctx.setLineDash(fcast === "google" ? [5, 3] : []);
      ctx.beginPath();
      ctx.moveTo(lx, ly + 5);
      ctx.lineTo(lx + 22, ly + 5);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#555";
      ctx.fillText(FORECAST_LABEL[fcast], lx + 28, ly + 9);
      ly += 20;
    }
  }

  canvas.toBlob((b) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(b);
    a.download = `contrailbench-${region}-${season}.png`;
    a.click();
  }, "image/png");
});
```

### Benchmarks

<div class="card">
  ${chartEl}

  <div class="bench-downloads">
    <div class="bench-downloads-links">${pngLink} ${csvLink}</div>
  </div>
</div>



