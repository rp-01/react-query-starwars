#!/bin/bash
set -e

python -m pip install --upgrade pip setuptools wheel
pwd
pip install -r rp-01/react-query-starwars/.github/actions/auto-generate-changelog/requirements.txt

python /main.py