#!/bin/bash

set -e

source .venv/bin/activate

rm -rf plots/ csv-calendar/ csv-cyclic/

python3 krupp_validation.py

python3 plot_results.py
