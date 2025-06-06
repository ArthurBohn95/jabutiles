#! /usr/bin/bash

# Creates the WHEEL
python -m build --verbose

# Uploads the WHEEL to PYPI
twine upload dist/* --config-file ./.pypirc --skip-existing --verbose
