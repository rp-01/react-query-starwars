#!/bin/bash
set -e

python -m pip install --upgrade pip setuptools wheel
pip install -r ./.github/actions/create-release/requirements.txt
python ./.github/actions/create-release/main.py