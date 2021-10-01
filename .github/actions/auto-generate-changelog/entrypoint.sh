#!/bin/bash
set -e

python -m pip install --upgrade pip setuptools wheel
pwd
find -name "requirements.txt"
pip install -r ./.github/actions/auto-generate-changelog/requirements.txt

python /main.py