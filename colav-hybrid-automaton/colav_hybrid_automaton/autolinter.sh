#!/bin/bash

echo "Autolinting colav_hybrid_eval"
# Fix PEP8 formatting issues
echo "autopep8 linting"
python3 -m autopep8 . --in-place --recursive --aggressive --aggressive
# CHecks unused imports, redefinitions, missing netlines,
# trailiing whitespaces, lines to long, docstring issues
echo "ruff linting"
python3 -m ruff check . --fix
# additional docstring issues
echo "pydocstyle linting"
python3 -m pydocstyle .