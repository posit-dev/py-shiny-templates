#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname $(dirname "$SCRIPT_DIR"))"

for dir in "$ROOT_DIR"/*/ "$ROOT_DIR"/gen-ai/*/ ; do
  [[ "$(basename "$dir")" == "gen-ai" ]] && continue
  [[ "$(basename "$dir")" == "tests" ]] && continue

  if [ ! -f "$dir/app-core.py" ]; then
    echo "app-core.py must be in each folder, but it's missing in $dir"
    exit 1
  fi
  if [ -f "$dir/app.py" ]; then
    echo "app.py should not be in any folder, but it's found in $dir"
    exit 1
  fi
done
