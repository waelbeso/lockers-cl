#!/usr/bin/env bash
set -euo pipefail

if ! command -v briefcase >/dev/null 2>&1; then
  echo "Installing Briefcase with Linux support..."
  python -m pip install --upgrade "briefcase[linux]"
fi

echo "Creating Briefcase Linux project"
briefcase create linux || true

echo "Building Linux app"
briefcase build linux

echo "Packaging Linux app"
briefcase package linux

echo "Collecting distributable artefacts"
mkdir -p dist/releases
find build/lockers/linux -maxdepth 1 -type f \( -name "*.AppImage" -o -name "*.deb" \) -exec cp {} dist/releases/ \;
