#!/bin/bash

# run the tiled server

CONDA_ENV=tiled
MY_DIR=$(realpath $(dirname $0))
LOG_FILE="${MY_DIR}/logfile.txt"
HOST=0.0.0.0
PORT=8000

# export CONDA_BASE=/APSshare/miniconda/x86_64
# source "${CONDA_BASE}/etc/profile.d/conda.sh"

# eval "$(micromamba shell hook --shell=)"
# micromamba activate "${CONDA_ENV}"

tiled serve config \
    --port ${PORT} \
    --host ${HOST} \
    --public \
    "${MY_DIR}/config.yml" \
    2>&1 | tee "${LOG_FILE}"
