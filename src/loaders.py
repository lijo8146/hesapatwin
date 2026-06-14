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
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    Load mine records from USGS MRDS via WFS (GML format).

    MRDS WFS only supports GML output as JSON is not available.
    Fields returned: dep_id, site_name, dev_stat, fips_code,
                     huc_code, quad_code, url, code_list, geometry
    """
    cache_key  = f"mrds_{bbox[0]:.2f}_{bbox[1]:.2f}_{bbox[2]:.2f}_{bbox[3]:.2f}.geojson"
    cache_file = CACHE_DIR / cache_key

    if cache_file.exists() and not force_refresh:
        return gpd.read_file(cache_file)

    r = requests.get(
        "https://mrdata.usgs.gov/wfs/mrds",
        params={
            "service":     "WFS",
            "version":     "1.0.0",
            "request":     "GetFeature",
            "typeName":    "mrds",
            "bbox":        f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "maxFeatures": "5000",
        },
        timeout=120,
    )
    r.raise_for_status()

    if not r.text.strip():
        warnings.warn("MRDS WFS returned empty response.", UserWarning)
        return gpd.GeoDataFrame()

    from xml.etree import ElementTree as ET
    from shapely.geometry import Point

    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        warnings.warn(f"MRDS WFS GML parse error: {e}", UserWarning)
        return gpd.GeoDataFrame()

    ns = {
        "wfs": "http://www.opengis.net/wfs",
        "gml": "http://www.opengis.net/gml",
        "ms":  "http://mapserver.gis.umn.edu/mapserver",
    }

    TEXT_FIELDS = [
        "dep_id", "site_name", "dev_stat", "fips_code",
        "huc_code", "quad_code", "url", "code_list",
    ]

    records = []
    for member in root.findall(".//gml:featureMember", ns):
        node = member.find("ms:mrds", ns)
        if node is None:
            continue

        rec = {}
        for field in TEXT_FIELDS:
            el = node.find(f"ms:{field}", ns)
            rec[field] = el.text.strip() if el is not None and el.text else None

        coords_el = node.find(".//gml:coordinates", ns)
        if coords_el is not None and coords_el.text:
            try:
                first_pair = coords_el.text.strip().split()[0]
                lon, lat   = [float(v) for v in first_pair.split(",")]
                rec["geometry"] = Point(lon, lat)
            except (ValueError, IndexError):
                rec["geometry"] = None
        else:
            rec["geometry"] = None

        if rec["geometry"] is not None:
            records.append(rec)

    if not records:
        warnings.warn(
            f"MRDS WFS returned 0 parseable records for bbox {bbox}. "
            "Mine monitoring coverage on Tribal lands may be sparse.",
            UserWarning,
        )
        return gpd.GeoDataFrame()

    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
    gdf.to_file(cache_file, driver="GeoJSON")
    log.info("MRDS loaded and cached: %d mines", len(gdf))
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
