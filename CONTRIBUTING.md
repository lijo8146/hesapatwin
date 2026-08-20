# Contributing

Open an issue before changing territorial language, governance fields, or
data-use rules. Those changes require review by authorized Lakota collaborators;
a code review alone is insufficient.

Create the environment with `conda env create -f environment.yml`, run `pytest`,
and run `python scripts/check_notebooks.py`. Do not commit credentials, caches,
generated outputs, or sensitive Tribal data. Release artifacts must pass
`src.validation.validate_gazetteer` and include a checksum-bearing manifest.
