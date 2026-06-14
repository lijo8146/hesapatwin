"""
constants.py project-wide constants for black_hills_mining_twin.

Every spatial query, provenance record, and governance field
in this repository derives from values defined here.
"""
from __future__ import annotations
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]

# Coordinate reference systems 
CRS_GEOGRAPHIC = "EPSG:4326"    # WGS84 for API queries and output
CRS_PROJECTED  = "EPSG:5070"    # Albers Equal Area CONUS for area/distance

# Study area: He Sapa 
# Bounding box: (min_lon, min_lat, max_lon, max_lat)
# Covers the full Black Hills uplift including the geographic, geologic,
# and mining district boundary defining the area of extraction.
# The 1868 Fort Laramie Treaty territory extends beyond this box;
# that broader context is documented in TREATY_PROVENANCE below,
# not truncated by this spatial filter.
BLACK_HILLS_BBOX = (-104.6, 43.4, -103.3, 44.6)

# Centroid for point-based queries
BLACK_HILLS_LAT = 44.0
BLACK_HILLS_LON = -103.9

# Data directories
CACHE_DIR   = REPO_ROOT/"data"/"cache"
OUTPUTS_DIR = REPO_ROOT/"outputs"
FIGURES_DIR = OUTPUTS_DIR/"figures"

for _d in [CACHE_DIR, OUTPUTS_DIR, FIGURES_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# MRDS WFS endpoint 
# USGS Mineral Resources Data System WFS 1.1.0
# Confirmed active; supports bounding box queries
MRDS_WFS_URL = "https://mrdata.usgs.gov/wfs/mrds"

# BLM mining claims
# LR2000 serial register SD counties in Black Hills
BLM_COUNTIES = ["Lawrence", "Custer", "Pennington"]

# Commodity classifications
# Used for map symbology and filtering
COMMODITY_GROUPS = {
    "gold":     ["gold", "au", "placer gold", "lode gold"],
    "silver":   ["silver", "ag"],
    "lead_zinc":["lead", "zinc", "pb", "zn", "galena"],
    "tin":      ["tin", "sn", "cassiterite"],
    "tungsten": ["tungsten", "w", "scheelite"],
    "uranium":  ["uranium", "u", "vanadium"],
    "copper":   ["copper", "cu"],
    "iron":     ["iron", "fe", "iron ore"],
    "mica":     ["mica", "muscovite", "feldspar", "pegmatite"],
    "other":    [],
}

# Mine status classifications (from MRDS dev_stat field)
STATUS_GROUPS = {
    "producer":   ["producer", "active"],
    "past_producer": ["past producer", "historic"],
    "prospect":   ["prospect", "occurrence"],
    "plant":      ["plant"],
    "unknown":    ["", None],
}

# Map symbology
COMMODITY_COLORS = {
    "gold":       "#FFD700",
    "silver":     "#C0C0C0",
    "lead_zinc":  "#6B6B6B",
    "tin":        "#B87333",
    "tungsten":   "#4A4A8A",
    "uranium":    "#7FFF00",
    "copper":     "#B87333",
    "iron":       "#8B0000",
    "mica":       "#E8D5B7",
    "other":      "#888888",
}

# Temporal bins for reconstruction
# Based on major periods in Black Hills mining history
ERA_BINS = {
    "Pre-1876 (pre-rush)":       (None, 1875),
    "Gold Rush (1876–1890)":     (1876, 1890),
    "Industrial Era (1891–1920)":(1891, 1920),
    "Mid-Century (1921–1960)":   (1921, 1960),
    "Modern (1961–2000)":        (1961, 2000),
    "Contemporary (2001–)":      (2001, None),
}

# IEEE 2890-2025 and Tribal provenance fields
# These fields appear on EVERY record in the gazetteer.
# Language authored with Lakota team input.
# Reference: United States v. Sioux Nation of Indians, 448 U.S. 371 (1980)

TREATY_PROVENANCE = {
    "treaty_territory":  "1868 Fort Laramie Treaty He Sapa (Black Hills)",
    "treaty_status": (
        "Unceded Lakota territory. The 1877 Congressional act taking "
        "He Sapa was ruled unconstitutional by the US Supreme Court in "
        "United States v. Sioux Nation of Indians (1980). The Treaty "
        "Nations have declined compensation, maintaining that the land "
        "was never legally transferred."
    ),
    "legal_citation":    "United States v. Sioux Nation of Indians, 448 U.S. 371 (1980)",
    "tk_label":          "TK Notice",
    "tk_label_note": (
        "Indigenous interests exist in all records describing He Sapa. "
        "Contact originating Lakota communities before use. "
        "See: https://localcontexts.org/label/tk-notice/"
    ),
    "care_collective_benefit": (
        "This data describes He Sapa for purposes of historical "
        "documentation and environmental accountability. Results should "
        "benefit Lakota Nations who hold rights to this territory."
    ),
    "visibility_level":        "public",
    "phase_ii_sensitivity":    "review_required",
    "tribal_review_required":  "yes for any external publication or distribution",
    "redistribution_allowed":  "yes with attribution and TK Notice label",
    "ieee_2890_compliant":     True,
    "data_steward_phase1":     "Daear Consulting, LLC",
    "data_steward_note": (
        "Phase I stewardship is temporary. Transfer to Lakota Nation "
        "stewardship is the intended Phase II outcome."
    ),
}

# Governance references
GOVERNANCE_REFS = {
    "ocap":        "https://fnigc.ca/ocap-training/",
    "care":        "https://www.gida-global.org/care",
    "fair":        "https://www.go-fair.org/fair-principles/",
    "ieee_2890":   "https://standards.ieee.org/ieee/2890/10318/",
    "tk_notice":   "https://localcontexts.org/label/tk-notice/",
    "scotus_1980": "https://supreme.justia.com/cases/federal/us/448/371/",
}
