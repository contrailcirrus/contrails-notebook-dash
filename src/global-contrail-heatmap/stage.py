"""
Stage data for Global Contrail Heatmap.

## Data

Data inputs in:
gs://contrails-301217-admin-data/contrails-notebook-dash/global-contrail-heatmap/

Contrail forcing output from Teoh 2024
https://acp.copernicus.org/articles/24/6071/2024/

World FIR TopoJSON from Open Aviation
https://observablehq.com/@openaviation/flight-information-regions

## Setup & Run

From this directory, download input files:

```bash
$ mkdir -p staging
$ gsutil -m cp -r "gs://contrails-301217-admin-data/contrails-notebook-dash/global-contrail-heatmap/*" staging/
```

Setup python env:

```bash
$ uv init
$ uv sync
```

Run processing:

```bash
$ uv run stage
```
"""

import json
import hashlib

import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd
import shapely
import topojson as tp
import xarray as xr


years = ["2019", "2024"]

def process_year(year: str) -> None:
    """Process single netcdf file

    Parameters
    ----------
    year : str
        Filestem
    """
    # load data
    ds = xr.open_dataset(f"staging/{year}.nc")
    var = "ef_net_overlap"

    # --- Create Bitmap

    # transpose dims
    da_img = ds[var].T

    # reverse latitude
    da_img = da_img.isel(latitude=slice(None, None, -1))

    # select colormap
    cmap = "hot_r"

    # Save as PNG with proper extent
    plt.imsave(f"data/{year}.png", np.log10(da_img.values), cmap=cmap, vmin=-5, vmax=-2)

    # --- Intersect with FIRs

    # load TopoJSON
    with open("data/firs.topojson", "r") as f:
        firs_topojson = json.load(f)

    firs_topo = tp.Topology(firs_topojson)
    firs_geojson = json.loads(firs_topo.to_geojson())

    # create points from the lon/lat grid of contrail coordinates
    contrail_coords = shapely.points(
        ds["longitude"].values[:, None], ds["latitude"].values[None, :]
    )

    # sum up % within each FIR
    for feature in firs_geojson["features"]:
        geom = shapely.from_geojson(json.dumps(feature["geometry"]))
        mask = shapely.contains(geom, contrail_coords)

        # add summed value to the properties
        feature["properties"]["value"] = ds[var].where(mask).sum().item()

    # csv output
    pd.DataFrame(f["properties"] for f in firs_geojson["features"]).to_csv(
        f"staging/{year}.csv", index=False
    )

def aggregate_outputs(years: list[str]) -> None:
    """Aggregate all outputs into a JSON list of dicts
    
    Parameters
    ----------
    years : list[str]
        List of input filestems
    """
    # load first year
    df = pd.read_csv(f"staging/{years[0]}.csv")
    df = df.rename(columns={"value": years[0]})

    # load subsequent years and append value col as year label
    for year in years[1:]:
        df2 = pd.read_csv(f"staging/{year}.csv")
        df[year] = df2["value"]

    # write out all to csv and JSON
    df.to_csv("data/fir-impacts.csv", index=False)
    df.to_json("data/fir-impacts.json", orient="records")

def add_fir_ids() -> None:
    """Add id to each FIR Geometry and save off new TopoJSON."""

    with open("staging/worldfirs.topojson", "r") as f:
        firs_topojson = json.load(f)

    # load TopoJSON
    firs_topo = tp.Topology(firs_topojson)
    firs_json = json.loads(firs_topo.to_json())
    for geom in firs_json["objects"]["data"]["geometries"]:
        geom["properties"]["id"] = hash_geom(geom)

    with open("data/firs.topojson", "w") as f:
        json.dump(firs_json, f, separators=(',', ':'))

def hash_geom(geom: dict) -> str:
    """Create unique hashed id for each FIR geometry
    
    Parameters
    ----------
    geom : dict
        TopoJSON Geometry
    
    Returns
    -------
    str
    """
    j = json.dumps(geom, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(j.encode()).hexdigest()[:8]

if __name__ == "__main__":
    print(f"Adding ids to FIRs")
    add_fir_ids()

    # calculate interesections and save off as CSVs
    for year in years:
        print(f"Processing year {year}")
        process_year(year)

    # aggregate interesections into single CSV, JSON files
    print(f"Aggregating outputs")
    aggregate_outputs(years)
