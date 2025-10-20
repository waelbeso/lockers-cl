#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RELEASE_DIR="$ROOT_DIR/dist/releases"
mkdir -p "$RELEASE_DIR"

SPEC_FILE="${1:-lockers.spec}"
TARGET_ARCH="${PYINSTALLER_TARGET_ARCH:-universal2}"

if [[ ! -f "$SPEC_FILE" ]]; then
  echo "Unable to locate spec file: $SPEC_FILE" >&2
  exit 1
fi

echo "Running PyInstaller for macOS ($TARGET_ARCH)"
pyinstaller "$SPEC_FILE" --noconfirm --target-arch "$TARGET_ARCH"

APP_SOURCE="$ROOT_DIR/dist/lockers/lockers.app"
if [[ ! -d "$APP_SOURCE" ]]; then
  echo "PyInstaller app bundle missing at $APP_SOURCE" >&2
  exit 1
fi

APP_TARGET="$RELEASE_DIR/LockersCL.app"
rm -rf "$APP_TARGET"
cp -R "$APP_SOURCE" "$APP_TARGET"

if [[ -n "${MAC_CODESIGN_IDENTITY:-}" ]]; then
  echo "Codesigning app bundle with $MAC_CODESIGN_IDENTITY"
  codesign --force --deep --options runtime --sign "$MAC_CODESIGN_IDENTITY" "$APP_TARGET"
fi

DMG_PATH="$RELEASE_DIR/LockersCL.dmg"
rm -f "$DMG_PATH"

echo "Creating disk image"
create-dmg --overwrite --volname "LockersCL" --app-drop-link 600 185 "$DMG_PATH" "$APP_TARGET"

if [[ -n "${APPLE_NOTARIZE_PROFILE:-}" ]]; then
  echo "Submitting $DMG_PATH for notarization"
  xcrun notarytool submit "$DMG_PATH" --keychain-profile "$APPLE_NOTARIZE_PROFILE" --wait
  xcrun stapler staple "$DMG_PATH"
fi

echo "Updating SHA256SUMS"
(
  cd "$RELEASE_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS' -print0 |
    sort -z |
    xargs -0 shasum -a 256 > SHA256SUMS
)
