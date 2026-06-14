"""
sovereignty.py governance acknowledgment for black_hills_mining_twin.

He Sapa (the Black Hills) is unceded Lakota territory.
This module makes that context visible at the top of every notebook
and in every data citation block.
"""
from __future__ import annotations
from src.constants import TREATY_PROVENANCE, GOVERNANCE_REFS

_PREAMBLE = """
BLACK HILLS MINING DIGITAL TWIN TREATY TERRITORY ACKNOWLEDGMENT

He Sapa (the Black Hills) is unceded Lakota territory.

The 1868 Fort Laramie Treaty guaranteed He Sapa and surrounding lands to the Lakota
and their allies in perpetuity. After Custer's 1874 expedition confirmed gold, 
the US Congress unilaterally took the Black Hills in 1877. The US Supreme
Court ruled this action as unconstitutional in United States v. Sioux Nation of
Indians, 448 U.S. 371 (1980). The Sioux Nations have declined
the offered compensation. The Black Hills are not for sale.

Every record in this system carries that context as a provenance field.

GOVERNANCE FRAMEWORKS:

OCAP®  : The Oceti Sakowin and allied Nations have Ownership, Control, Access,
  and Possession of data describing their territory and resources.
  Phase I uses public federal data only. Any results describing
  He Sapa should be shared with relevant Lakota governance bodies
  before external publication or distribution.
  Reference: https://fnigc.ca/ocap-training/

CARE   : Collective Benefit, Authority to Control, Responsibility,
  Ethics. This system is designed to support Lakota environmental
  accountability and historical documentation, not to enable
  further extraction or dispossession.
  Reference: https://www.gida-global.org/care

FAIR   : Findable, Accessible, Interoperable, Reusable.
  All Phase I data is from public sources, fully reproducible,
  and exported in open formats.
  Reference: https://www.go-fair.org/fair-principles/

IEEE 2890-2025 : Recommended Practice for Provenance of Indigenous
  Peoples' Data. Every record documents its source, transformation
  chain, governance status, and territorial context.
  Reference: https://standards.ieee.org/ieee/2890/10318/

TK Notice : All records describing He Sapa carry a Traditional
  Knowledge Notice. Indigenous interests exist in this material.
  Contact originating Lakota communities before use.
  Reference: https://localcontexts.org/label/tk-notice/
"""

_DATA_SOURCES = {
    "mrds": {
        "name":    "USGS Mineral Resources Data System (MRDS)",
        "url":     "https://mrdata.usgs.gov/mrds/",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
        "citation": (
            "US Geological Survey. Mineral Resources Data System (MRDS). "
            "https://mrdata.usgs.gov/mrds/ "
            "doi:10.3133/ds20"
        ),
        "note": (
            "MRDS systematic updates ceased in 2011. Records reflect "
            "historical data quality issues. Claude API extraction from "
            "primary USGS bulletins supplements and corrects MRDS records."
        ),
    },
    "blm_claims": {
        "name":    "BLM LR2000 Mining Claims for South Dakota",
        "url":     "https://www.blm.gov/lr2000",
        "steward": "Bureau of Land Management",
        "license": "Public domain (BLM)",
        "note": (
            "Covers active and closed claims on federal land. "
            "Lawrence, Custer, and Pennington counties = Black Hills."
        ),
    },
    "wbd": {
        "name":    "USGS Watershed Boundary Dataset (WBD)",
        "url":     "https://www.usgs.gov/national-hydrography/watershed-boundary-dataset",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
    },
    "nhd": {
        "name":    "USGS National Hydrography Dataset Plus HR (NHD)",
        "url":     "https://www.usgs.gov/national-hydrography/nhdplus-high-resolution",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
    },
    "3dep": {
        "name":    "USGS 3D Elevation Program (3DEP) 1/3 arc-second DEM",
        "url":     "https://www.usgs.gov/3d-elevation-program",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
    },
    "nlcd": {
        "name":    "USGS/MRLC National Land Cover Database (NLCD) 2021",
        "url":     "https://www.mrlc.gov/data",
        "steward": "USGS / Multi-Resolution Land Characteristics Consortium",
        "license": "Public domain (USGS)",
        "citation": (
            "Dewitz, J. (2023). National Land Cover Database (NLCD) 2021. "
            "US Geological Survey. doi:10.5066/P9OGBGM6"
        ),
    },
    "claude_api": {
        "name":    "Anthropic Claude API — structured extraction",
        "url":     "https://www.anthropic.com",
        "steward": "Daear Consulting / ESIIL (extraction pipeline)",
        "license": "Outputs are derivative of public-domain USGS source documents",
        "note": (
            "AI-extracted records enter the gazetteer only after human review. "
            "No autonomous historical interpretation. "
            "ai_generated=True and human_verified fields track extraction source."
        ),
    },
    "usgs_bulletins": {
        "name":    "USGS Mineral Resource Bulletins and Professional Papers",
        "url":     "https://pubs.usgs.gov/",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
        "note": (
            "Primary source documents for Claude API extraction pipeline. "
            "Key reference: USGS IMAP 2445 26 quadrangle maps at 1:24,000 "
            "covering He Sapa mine locations, prospects, and patented claims."
        ),
    },
}


def print_data_acknowledgment(source_keys: list[str] | None = None) -> None:
    """Print territorial acknowledgment and data source provenance."""
    print(_PREAMBLE)
    if not source_keys:
        return
    print("DATA SOURCES FOR THIS NOTEBOOK")
    print("=" * 60)
    for key in source_keys:
        src = _DATA_SOURCES.get(key)
        if not src:
            print(f"  [Unknown source key: {key}]")
            continue
        print(f"\n  {src['name']}")
        print(f"  URL     : {src['url']}")
        print(f"  Steward : {src['steward']}")
        print(f"  License : {src['license']}")
        if src.get("citation"):
            print(f"  Cite as : {src['citation']}")
        if src.get("note"):
            print(f"  Note    : {src['note']}")


def generate_citations(source_keys: list[str]) -> str:
    """Return a plain-text citation block for notebook outputs."""
    lines = ["DATA CITATIONS", "=" * 60]
    for key in source_keys:
        src = _DATA_SOURCES.get(key)
        if not src:
            continue
        lines.append(f"\n{src['name']}")
        if src.get("citation"):
            lines.append(f"  {src['citation']}")
        lines.append(f"  {src['url']}")
        lines.append(f"  Steward: {src['steward']} | License: {src['license']}")
    lines.append("\nTERRITORIAL PROVENANCE (all records)")
    lines.append(f"  {TREATY_PROVENANCE['treaty_territory']}")
    lines.append(f"  {TREATY_PROVENANCE['treaty_status']}")
    lines.append(f"  {TREATY_PROVENANCE['legal_citation']}")
    lines.append(f"  TK Label: {TREATY_PROVENANCE['tk_label']} — {TREATY_PROVENANCE['tk_label_note']}")
    lines.append("\nGOVERNANCE FRAMEWORKS: OCAP® | CARE | FAIR | IEEE 2890-2025")
    for name, url in GOVERNANCE_REFS.items():
        lines.append(f"  {name.upper()}: {url}")
    return "\n".join(lines)


def build_record_provenance(
    source_key: str,
    ai_generated: bool = False,
    human_verified: bool = False,
    notes: str = "",
) -> dict:
    """
    Return a complete IEEE 2890-2025 provenance dict for a single record.
    Attach this to every row in the gazetteer.

    Parameters
    source_key     : Key from _DATA_SOURCES (e.g. 'mrds', 'claude_api')
    ai_generated   : True if this record was extracted by Claude API
    human_verified : True if a human reviewer confirmed the record
    notes          : Free-text provenance notes
    """
    src = _DATA_SOURCES.get(source_key, {})
    return {
        **TREATY_PROVENANCE,
        "prov_source":        src.get("name", source_key),
        "prov_source_url":    src.get("url", ""),
        "prov_data_steward":  src.get("steward", ""),
        "prov_license":       src.get("license", ""),
        "ai_generated":       ai_generated,
        "human_verified":     human_verified,
        "prov_notes":         notes,
        "ieee_2890_compliant": True,
    }
