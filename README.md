# Black Hills Mining Landscape Digital Twin Phase I

**Authors:** Lilly Jones, PhD 
**Territory:** He Sapa (Black Hills) Unceded Lakota Territory                                          
**Phase:** I: Public data only. No sensitive Tribal data.

## Territorial Acknowledgment
He Sapa (the Black Hills) is unceded Lakota territory. The 1877
Congressional act taking He Sapa was ruled unconstitutional by the
US Supreme Court in *United States v. Sioux Nation of Indians*, 448
U.S. 371 (1980). The Treaty Nations have declined compensation,
maintaining that the land was never legally transferred.

This repository reconstructs the mining history of He Sapa using
public federal data. Every record in this system carries this Treaty status and 
territorial context as a provenance field.

## Purpose
A temporal, sovereignty-aware digital twin reconstructing
the evolution of mining landscapes in the Black Hills of South Dakota and Wyoming.

Phase I builds:
- A mine gazetteer from USGS MRDS and BLM claims data
- Environmental and watershed context layers
- A temporal reconstruction of mining activity over time
- A governance-aware data architecture ready for Phase II Tribal data
- An interactive demo map for presentation to Tribal leaders

Phase II will add sensitive Tribal data under full Tribal governance.
The architecture supports this without redesign.

## Notebooks
| Notebook | Title | Output |
|---|---|---|
| 01 | Mine Gazetteer | MRDS and BLM GeoPackage of all Black Hills mines |
| 02 | Environmental Context | Watersheds, hydrology, geology |
| 03 | Temporal Reconstruction | Mining activity by era, commodity, status |
| 04 | Disturbance and Impact | Tailings, contamination risk, watershed exposure |
| 05 | Governance Layer | CARE/OCAP/TK Notice/IEEE 2890-2025 on every record |
| 06 | Interactive Demo Map | Folium map with timeline, layers, mine inspections |

## Study Area
**He Sapa (Black Hills), South Dakota**  
Bounding box: `-104.6°W to -103.3°W`, `43.4°N to 44.6°N`

This captures the full Black Hills uplift and the geographic, geological,
and mining district boundary that defines the area of extraction.
The 1868 Fort Laramie Treaty territory extends far beyond this box;
that broader context is documented in the provenance fields of every
record, not truncated by the spatial filter.

## Data Sources
| Source | What | Notebook |
|---|---|---|
| USGS MRDS WFS | ~847 mine records, Black Hills NF | 01 |
| BLM LR2000 | 58,581 SD mining claims | 01 |
| USGS WBD | HUC-8/10/12 watersheds | 02 |
| USGS NHD | Stream network | 02 |
| USGS 3DEP | Elevation / terrain | 02 |
| USGS National Geologic Map | Geologic units | 02 |
| Claude API | Structured extraction from USGS bulletins | 03 |
| USGS NLCD/LCMAP | Land cover change | 04 |

## Quick Start
```bash
git clone https://github.com/your-org/black_hills_mining_twin
cd black_hills_mining_twin

conda env create -f environment.yml
conda activate black-hills-twin
python -m ipykernel install --user --name black-hills-twin \
    --display-name "Python (black-hills-twin)"

# Add your Anthropic API key for notebook 03
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...

jupyter lab notebooks/
```
Run notebooks in order 01-06.

## Repository Structure
```
black_hills_mining_twin/
├── notebooks/
│   ├── 01_mine_gazetteer.ipynb
│   ├── 02_environmental_context.ipynb
│   ├── 03_temporal_reconstruction.ipynb
│   ├── 04_disturbance_impact.ipynb
│   ├── 05_governance_layer.ipynb
│   └── 06_interactive_demo_map.ipynb
├── src/
│   ├── constants.py        # Bounding box, CRS, provenance fields
│   ├── loaders.py          # MRDS WFS, BLM, NHD, WBD loaders
│   └── sovereignty.py      # Governance acknowledgment + citations
├── data/
│   └── cache/              # GITIGNORED: downloaded datasets
├── outputs/                # GITIGNORED: analysis products
│   └── figures/
├── docs/
│   └── data_sovereignty.md
├── .env.example
├── .gitignore
├── environment.yml
└── README.md
```

## Governance Frameworks
Every record in this system is governed by:

- **OCAP®** Oceti Sakowin and allied Nations have Ownership,
  Control, Access, and Possession of data describing their territory
- **CARE** Collective Benefit, Authority to Control,
  Responsibility, Ethics
- **FAIR** Findable, Accessible, Interoperable, Reusable
- **IEEE 2890-2025** Provenance of Indigenous Peoples' Data
- **Local Contexts TK Notice** Indigenous interests exist in all
  records describing He Sapa; contact originating communities
  before use

Phase II will add full Tribal data governance with Nation-authorized
TK and BC labels from Local Contexts.

## Citation
Jones, L. (2026). Black Hills Mining Landscape Digital Twin,
Phase I. 
