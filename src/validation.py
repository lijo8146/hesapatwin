"""Validation and release-manifest helpers for published project artifacts."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

from src.constants import PROJECT_VERSION

REQUIRED_PROVENANCE_FIELDS = {
    "treaty_territory",
    "treaty_status",
    "legal_citation",
    "tk_label",
    "prov_source",
    "prov_source_url",
    "ieee_2890_status",
}


def validate_gazetteer(frame: gpd.GeoDataFrame) -> None:
    """Fail fast when a gazetteer is incomplete or misleading."""
    if frame.empty:
        raise ValueError("Gazetteer is empty")
    missing = REQUIRED_PROVENANCE_FIELDS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing provenance fields: {sorted(missing)}")
    null_fields = [name for name in REQUIRED_PROVENANCE_FIELDS if frame[name].isna().any()]
    if null_fields:
        raise ValueError(f"Null provenance values: {sorted(null_fields)}")
    if frame.geometry.isna().any() or frame.crs is None:
        raise ValueError("Every record must have geometry and a declared CRS")
    if "commodity_group" not in frame or frame["commodity_group"].nunique() < 2:
        raise ValueError("Commodity classification must produce at least two groups")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(files: list[Path], destination: Path, source_metadata: dict) -> Path:
    """Write a versioned, checksum-bearing manifest for release artifacts."""
    payload = {
        "project_version": PROJECT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": source_metadata,
        "artifacts": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files
        ],
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination
