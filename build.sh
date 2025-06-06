#! /usr/bin/bash

python -m build --verbose
twine upload dist/* --config-file ./.pypirc --skip-existing --verbose
