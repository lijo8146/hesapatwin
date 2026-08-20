# He Sapa Mining Landscape Digital Twin Phase I

**Author:** Lilly Jones, PhD

**Territory:** He Sapa (Black Hills), unceded Lakota territory

**Status:** Public-federal-data prototype; no sensitive Tribal data

He Sapa (the Black Hills) was guaranteed to the Lakota and their allies by the 1868 Fort Laramie
Treaty. The taking of the Black Hills was held unconstitutional in *United
States v. Sioux Nation of Indians*, 448 U.S. 371 (1980). The Treaty Nations
have declined compensation and maintain that the land was never legally
transferred. Every published record carries this territorial context.

## What is implemented

- A USGS Mineral Resources Data System (MRDS) mine gazetteer for the study area.
- HUC-8 watershed and NHDPlus HR order-2+ stream context layers.
- A partial temporal reconstruction based on MRDS date fields.
- A distance-to-mapped-stream screening metric. This is **not** evidence of
  contamination, exposure, hydrologic connectivity, or environmental risk.
- Record-level territorial, source, AI-origin, and human-review metadata.
- A Folium demonstration map generated from the public Phase I outputs.

BLM claims, 3DEP terrain, geologic units, NLCD/LCMAP change, and production-scale
USGS bulletin extraction are planned but not implemented yet in Phase I data sources.

## Governance status

The project implements a provenance scaffold informed by CARE, FAIR, OCAP®, Local
Contexts, and IEEE 2890-2025. It does not claim independent certification or
Nation authorization. Phase II governance prerequisites remain open, and no
sensitive Tribal data may enter this repository until they are satisfied. See
[the canonical governance status](docs/data_governance.md).

## Study area

The Phase I bounding box is `(-104.6, 43.4, -103.3, 44.6)` in EPSG:4326. It is
an analytical window around the Black Hills and is not a Treaty boundary. The
1868 Treaty territory extends far beyond it.

## Reproducible setup

```bash
git clone https://github.com/lijo8146/hesapatwin.git
cd hesapatwin
conda env create -f environment.yml
conda activate black-hills-twin
python -m ipykernel install --user --name black-hills-twin \
  --display-name "Python (black-hills-twin)"
jupyter lab Notebooks/
```

For an exact reproduction of the verified Windows environment, use
`conda create -n black-hills-twin --file environment-win-64.lock.txt`.

Run notebooks 01–06 in order. Cached source data and generated outputs are
ignored by default. Published releases should contain selected artifacts plus a
checksum-bearing manifest produced by `src.validation.write_manifest`.

## Verification

```bash
pytest
python scripts/check_notebooks.py
python -m compileall -q src
```

CI runs the same static and unit checks. Network-dependent notebook execution is
kept separate because upstream federal services can be unavailable; release
generation must run the complete notebooks and validate artifacts before
publication.

## Repository layout

```text
Notebooks/              ordered analytical workflow
src/                    loaders, constants, provenance, validation
tests/                  unit and schema tests
scripts/                notebook/release checks
data/cache/             downloaded public source data (generated)
outputs/                generated analysis artifacts
docs/                   governance status and selected public demo
.github/workflows/      continuous integration
```

## Data quality and interpretation

MRDS maintenance and coverage are incomplete, commodity values require parsing,
and date coverage is sparse. Counts describe records returned by the documented
query, not a complete inventory of mines or environmental impacts. Stream
proximity uses only mapped order-2+ flowlines. All public findings must retain
these limitations and identify the source retrieval date and transformation
version.

## Citation and license

Citation metadata are in [CITATION.cff](CITATION.cff). Repository-authored code
and documentation use the MIT License; upstream datasets retain their own terms.
The license does not apply to Indigenous knowledge or future Tribal-governed
data. See [LICENSE](LICENSE) and [CONTRIBUTING.md](CONTRIBUTING.md).
