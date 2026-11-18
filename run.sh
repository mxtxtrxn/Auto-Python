#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m labelprint
