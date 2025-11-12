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

Download files:

```bash
$ gsutil -m cp contrails-301217-admin-data/contrails-notebook-dash/global-contrail-heatmap/* .
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

import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd
import shapely
import topojson as tp
import xarray as xr


years = ["2019", "2024"]

rpath = "worldfirs.topojson"
with open(rpath, "r") as f:
    FIRS_TOPOJSON = json.load(f)


def process_year(year: str) -> None:
    """Process single netcdf file

    Parameters
    ----------
    year : str
        Filestem
    """
    # load data
    ds = xr.open_dataset(f"{year}.nc")
    var = "ef_net_overlap"

    # --- Create Bitmap

    # transpose dims
    da_img = ds[var].T

    # reverse latitude
    da_img = da_img.isel(latitude=slice(None, None, -1))

    # select colormap
    cmap = "hot_r"

    # Save as PNG with proper extent
    plt.imsave(f"{year}.png", np.log10(da_img.values), cmap=cmap, vmin=-5, vmax=-2)

    # --- Intersect with FIRs

    # load TopoJSON
    firs_topo = tp.Topology(FIRS_TOPOJSON)
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

    # output topojson file with values in it
    firs_topo_out = tp.Topology(firs_geojson)
    firs_topo_out.to_json(f"{year}.topojson")

    # csv output
    pd.DataFrame(f["properties"] for f in firs_geojson["features"]).to_csv(
        f"{year}.csv", index=False
    )


if __name__ == "__main__":
    for year in years:
        print(f"Processing year {year}")
        process_year(year)
