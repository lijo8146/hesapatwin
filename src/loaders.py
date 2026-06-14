"""
loaders.py data download and cache functions for black_hills_mining_twin.

Primary sources:
  - USGS MRDS via WFS 1.1.0  (mine locations, commodities, dates)
  - USGS WBD                  (watershed boundaries)
  - USGS NHD                  (stream network)
  - USGS 3DEP TNM API         (elevation)
"""
from __future__ import annotations

import io
import json
import logging
import warnings
import zipfile
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import geopandas as gpd
from tenacity import retry, stop_after_attempt, wait_exponential

from src.constants import (
    CACHE_DIR, CRS_GEOGRAPHIC, CRS_PROJECTED,
    BLACK_HILLS_BBOX, MRDS_WFS_URL,
)

log = logging.getLogger(__name__)

_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


# MRDS Mine Gazetteer

@_retry
def load_mrds_mines(
    bbox: tuple[float, float, float, float] = BLACK_HILLS_BBOX,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    Query USGS MRDS WFS for all mine records within the bounding box.
    Uses WFS 1.1.0 with a bounding box spatial filter.
    Returns all MRDS fields available in the condensed WFS output.

    Parameters
    bbox : (min_lon, min_lat, max_lon, max_lat) (default Black Hills)

    Returns
    GeoDataFrame with one row per mine record, EPSG:4326
    """
    cache_file = CACHE_DIR/f"mrds_mines_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.geojson".replace("-", "n")

    if cache_file.exists() and not force_refresh:
        log.info("MRDS loaded from cache")
        return gpd.read_file(cache_file)

    print("Querying USGS MRDS WFS for Black Hills mines...")
    print(f"  Bounding box: {bbox}")

    # WFS 1.1.0 BBOX query 
    params = {
        "service":     "WFS",
        "version":     "1.1.0",
        "request":     "GetFeature",
        "typeName":    "mrds",
        "outputFormat":"json",
        "BBOX":        f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]},EPSG:4326",
        "maxFeatures": 5000,
    }

    try:
        r = requests.get(MRDS_WFS_URL, params=params, timeout=120)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        warnings.warn(f"MRDS WFS query failed: {e}", UserWarning)
        return gpd.GeoDataFrame()

    features = payload.get("features", [])
    if not features:
        warnings.warn(
            "MRDS returned 0 features for this bounding box.",
            UserWarning,
        )
        return gpd.GeoDataFrame()

    gdf = gpd.GeoDataFrame.from_features(features, crs=CRS_GEOGRAPHIC)

    # Standardize column names to lowercase
    gdf.columns = [c.lower() for c in gdf.columns]

    print(f"  MRDS records returned: {len(gdf):,}")
    gdf.to_file(cache_file, driver="GeoJSON")
    return gdf


def clean_mrds(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Standardize and clean MRDS fields for use in the gazetteer.

    Handles common MRDS data quality issues:
    - Mixed case field names
    - Null/empty string active dates
    - Commodity field cleaning
    - Duplicate depid records
    """
    # Remove exact duplicates on deposit ID if present
    id_col = next((c for c in gdf.columns if c in ("depid", "dep_id", "id")), None)
    if id_col:
        gdf = gdf.drop_duplicates(subset=[id_col]).reset_index(drop=True)

    # Parse active dates MRDS stores as free text (ex. "1890", "1890-1934")
    for date_col in ("actv_dt", "actv_date", "prod_date"):
        if date_col in gdf.columns:
            gdf[date_col] = gdf[date_col].replace("", None)

    # Normalize commodity to lowercase
    if "commod1" in gdf.columns:
        gdf["commod1"] = gdf["commod1"].str.lower().str.strip()

    # Normalize site name
    if "site_name" in gdf.columns:
        gdf["site_name"] = gdf["site_name"].str.strip().str.title()

    # Normalize development status
    if "dev_stat" in gdf.columns:
        gdf["dev_stat"] = gdf["dev_stat"].str.lower().str.strip()

    return gdf


# WBD Watershed Boundaries

@_retry
def load_wbd(
    bbox: tuple[float, float, float, float] = BLACK_HILLS_BBOX,
    huc_level: int = 8,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    Load USGS Watershed Boundary Dataset for the Black Hills.

    Parameters
    huc_level : 8 (subbasin), 10, or 12 (subwatershed)
    """
    cache_file = CACHE_DIR/f"wbd_huc{huc_level}_black_hills.geojson"
    if cache_file.exists() and not force_refresh:
        return gpd.read_file(cache_file)

    # WBD MapServer layer IDs: 1=HUC2, 2=HUC4, 3=HUC6, 4=HUC8, 5=HUC10, 6=HUC12
    layer_map  = {2: 1, 4: 2, 6: 3, 8: 4, 10: 5, 12: 6}
    layer_id   = layer_map.get(huc_level, 4)
    url        = f"https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/{layer_id}/query"

    r = requests.get(
        url,
        params={
            "where":          "1=1",
            "outFields":      f"huc{huc_level},name,areasqkm",
            "f":              "geojson",
            "returnGeometry": "true",
            "outSR":          "4326",
            "geometry":       f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "geometryType":   "esriGeometryEnvelope",
            "spatialRel":     "esriSpatialRelIntersects",
            "inSR":           "4326",
        },
        timeout=120,
    )

    try:
        payload = r.json()
    except Exception:
        warnings.warn("WBD response is not valid JSON.", UserWarning)
        return gpd.GeoDataFrame()

    if payload.get("error") or not payload.get("features"):
        warnings.warn(f"WBD returned no features: {payload.get('error')}", UserWarning)
        return gpd.GeoDataFrame()

    gdf = gpd.read_file(io.BytesIO(r.content))
    if not gdf.empty:
        gdf = gdf.set_crs(CRS_GEOGRAPHIC, allow_override=True)
        gdf.to_file(cache_file, driver="GeoJSON")
    print(f"WBD HUC-{huc_level}: {len(gdf)} watersheds")
    return gdf


# NHD Stream Network

@_retry
def load_nhd_streams(
    bbox: tuple[float, float, float, float] = BLACK_HILLS_BBOX,
    min_stream_order: int = 2,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    Load NHD stream flowlines for the Black Hills.
    Parameters
    min_stream_order : Strahler order filter (2+ keeps named streams)
    """
    cache_file = CACHE_DIR/f"nhd_streams_order{min_stream_order}.geojson"
    if cache_file.exists() and not force_refresh:
        return gpd.read_file(cache_file)

    url = (
        "https://hydro.nationalmap.gov/arcgis/rest/services"
        "/NHDPlus_HR/MapServer/3/query"
    )
    r = requests.get(
        url,
        params={
            "where":          f"streamorde >= {min_stream_order}",
            "outFields":      "reachcode,gnis_name,streamorde,lengthkm",
            "f":              "geojson",
            "returnGeometry": "true",
            "outSR":          "4326",
            "geometry":       f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "geometryType":   "esriGeometryEnvelope",
            "spatialRel":     "esriSpatialRelIntersects",
            "inSR":           "4326",
        },
        timeout=120,
    )
    try:
        payload = r.json()
    except Exception:
        return gpd.GeoDataFrame()

    if payload.get("error") or not payload.get("features"):
        return gpd.GeoDataFrame()

    gdf = gpd.read_file(io.BytesIO(r.content))
    if not gdf.empty:
        gdf = gdf.set_crs(CRS_GEOGRAPHIC, allow_override=True)
        reach_col = next((c for c in gdf.columns if c.lower() == "reachcode"), None)
        if reach_col:
            gdf = gdf.drop_duplicates(subset=[reach_col]).reset_index(drop=True)
        gdf.to_file(cache_file, driver="GeoJSON")
    print(f"NHD streams (order >= {min_stream_order}): {len(gdf):,} segments")
    return gdf


# Black Hills boundary

def load_black_hills_boundary() -> gpd.GeoDataFrame:
    """
    Return a simple bounding polygon for He Sapa (Black Hills proper).
    Used as a spatial reference frame throughout the series.

    In Phase II this can be replaced with the 1868 Treaty boundary
    for the broader territorial context layer.
    """
    from shapely.geometry import box
    gdf = gpd.GeoDataFrame(
        {
            "name": ["He Sapa (Black Hills)"],
            "note": ["Black Hills proper — study area boundary"],
        },
        geometry=[box(*BLACK_HILLS_BBOX)],
        crs=CRS_GEOGRAPHIC,
    )
    return gdf
