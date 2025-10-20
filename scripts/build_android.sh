#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID_DIR="$ROOT_DIR/android"
RELEASE_DIR="$ROOT_DIR/dist/releases"

if [[ ! -d "$ANDROID_DIR" ]]; then
  echo "Android project not found at $ANDROID_DIR" >&2
  exit 1
fi

mkdir -p "$RELEASE_DIR"

cd "$ANDROID_DIR"

./gradlew --no-daemon clean assembleRelease

APK_PATH="$ANDROID_DIR/app/build/outputs/apk/release/app-release.apk"
if [[ ! -f "$APK_PATH" ]]; then
  echo "Release APK missing at $APK_PATH" >&2
  exit 1
fi

TARGET_APK="$RELEASE_DIR/lockerscl-android-arm64.apk"
cp "$APK_PATH" "$TARGET_APK"

(
  cd "$RELEASE_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS' -print0 |
    sort -z |
    xargs -0 sha256sum > SHA256SUMS
)
