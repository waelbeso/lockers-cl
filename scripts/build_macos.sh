#!/usr/bin/env bash
set -euo pipefail

if ! command -v briefcase >/dev/null 2>&1; then
  echo "Installing Briefcase with macOS support..."
  python -m pip install --upgrade "briefcase[macOS]"
fi

echo "Creating Briefcase macOS project"
briefcase create macOS || true

echo "Building macOS app"
briefcase build macOS

echo "Packaging macOS app"
briefcase package macOS

echo "Collecting distributable artefacts"
mkdir -p dist/releases
find build/lockers/macos -maxdepth 2 -type f \( -name "*.dmg" -o -name "*.zip" -o -name "*.pkg" \) -exec cp {} dist/releases/ \;
