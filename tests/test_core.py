from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from src.constants import COMMODITY_GROUPS
from src.loaders import _bbox_tiles, _fetch_arcgis_geojson_pages, assign_commodity_group
from src.sovereignty import build_record_provenance
from src.validation import REQUIRED_PROVENANCE_FIELDS, validate_gazetteer, write_manifest


def test_commodity_classifier_uses_mrds_code_list_text():
    assert assign_commodity_group("AU, AG, CU", COMMODITY_GROUPS) == "gold"
    assert assign_commodity_group("cassiterite; SN", COMMODITY_GROUPS) == "tin"
    assert assign_commodity_group(None, COMMODITY_GROUPS) == "other"


def test_bbox_tiles_cover_study_area_without_large_requests():
    tiles = _bbox_tiles((-104.6, 43.4, -103.3, 44.6), max_span_degrees=0.5)
    assert len(tiles) == 9
    assert all(tile[2] - tile[0] <= 0.5 for tile in tiles)
    assert all(tile[3] - tile[1] <= 0.5 for tile in tiles)


def test_arcgis_pagination_fetches_beyond_service_limit(monkeypatch):
    calls = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    def fake_get(url, params, timeout):
        calls.append(params.copy())
        offset = params["resultOffset"]
        count = 2_000 if offset == 0 else 17
        return Response({
            "type": "FeatureCollection",
            "features": [{"id": offset + i} for i in range(count)],
            "exceededTransferLimit": offset == 0,
        })

    monkeypatch.setattr("src.loaders.requests.get", fake_get)
    features = _fetch_arcgis_geojson_pages("https://example.test", {}, "test")
    assert len(features) == 2_017
    assert [call["resultOffset"] for call in calls] == [0, 2_000]


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
