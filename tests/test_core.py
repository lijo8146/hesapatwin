from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from src.constants import COMMODITY_GROUPS
from src.loaders import assign_commodity_group
from src.sovereignty import build_record_provenance
from src.validation import REQUIRED_PROVENANCE_FIELDS, validate_gazetteer, write_manifest


def test_commodity_classifier_uses_mrds_code_list_text():
    assert assign_commodity_group("AU, AG, CU", COMMODITY_GROUPS) == "gold"
    assert assign_commodity_group("cassiterite; SN", COMMODITY_GROUPS) == "tin"
    assert assign_commodity_group(None, COMMODITY_GROUPS) == "other"


def test_provenance_does_not_self_certify_compliance():
    provenance = build_record_provenance("mrds")
    assert provenance["ieee_2890_status"] == "scaffold_only_review_required"
    assert "ieee_2890_compliant" not in provenance


def test_gazetteer_validation_and_manifest(tmp_path: Path):
    provenance = build_record_provenance("mrds")
    frame = gpd.GeoDataFrame(
        [{**provenance, "commodity_group": "gold", "geometry": Point(-103.9, 44.0)},
         {**provenance, "commodity_group": "tin", "geometry": Point(-104.0, 44.1)}],
        crs="EPSG:4326",
    )
    validate_gazetteer(frame)
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("auditable", encoding="utf-8")
    manifest = write_manifest([artifact], tmp_path / "manifest.json", {"mrds": {}})
    assert '"sha256"' in manifest.read_text(encoding="utf-8")


def test_validation_rejects_one_commodity_group():
    provenance = build_record_provenance("mrds")
    frame = gpd.GeoDataFrame(
        [{**provenance, "commodity_group": "other", "geometry": Point(0, 0)}],
        crs="EPSG:4326",
    )
    with pytest.raises(ValueError, match="at least two"):
        validate_gazetteer(frame)
