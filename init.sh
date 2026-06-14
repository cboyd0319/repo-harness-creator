#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"
PYTHON_BIN="${PYTHON:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    PYTHON_BIN="python"
  fi
fi

echo "== Doctor =="
"$PYTHON_BIN" -m repo_harness_creator doctor

echo "== Compile =="
"$PYTHON_BIN" -m compileall src tests

echo "== Tests =="
"$PYTHON_BIN" -m unittest discover -s tests

echo "== Pin check =="
"$PYTHON_BIN" scripts/check_pins.py --root .

echo "== Self audit =="
"$PYTHON_BIN" -m repo_harness_creator audit --target . --min-score 85
