#!/usr/bin/env bash
set -euo pipefail

if ! command -v briefcase >/dev/null 2>&1; then
  echo "Installing briefcase..."
  python -m pip install --upgrade briefcase
fi

echo "Ensuring Android build prerequisites are installed"
briefcase create android || true

echo "Building Android APK"
briefcase build android

echo "Packaging Android APK"
briefcase package android
