#!/usr/bin/env bash
set -euo pipefail

if ! command -v briefcase >/dev/null 2>&1; then
  echo "Installing Briefcase with Android support..."
  python -m pip install --upgrade "briefcase[android]"
fi

echo "Ensuring Android build prerequisites are installed"
briefcase create android || true

echo "Building Android APK"
briefcase build android

echo "Packaging Android APK"
briefcase package android

echo "Collecting distributable artefacts"
mkdir -p dist/releases
find build/lockers/android -maxdepth 2 -type f -name "*.apk" -exec cp {} dist/releases/ \;
