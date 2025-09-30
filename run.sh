#! /bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"

if [[ -z "$SCRIPT_DIR" ]]; then
  echo "SCRIPT_DIR was empty, refusing to run, force executing this script may cause major harm."
  exit 1
fi

cd $SCRIPT_DIR

source ./.venv/bin/activate

./src/main.py

cd - > /dev/null
