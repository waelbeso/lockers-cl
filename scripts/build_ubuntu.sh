#!/usr/bin/env bash
set -euo pipefail

if ! command -v briefcase >/dev/null 2>&1; then
  echo "Installing briefcase..."
  python -m pip install --upgrade briefcase
fi

echo "Creating Briefcase Linux project"
briefcase create linux || true

echo "Building Linux app"
briefcase build linux

echo "Packaging Linux app"
briefcase package linux
