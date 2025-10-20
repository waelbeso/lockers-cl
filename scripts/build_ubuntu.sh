#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RELEASE_DIR="$ROOT_DIR/dist/releases"
mkdir -p "$RELEASE_DIR"

SPEC_FILE="${1:-lockers.spec}"
VERSION="${LOCKERS_VERSION:-0.1.0}"

if [[ ! -f "$SPEC_FILE" ]]; then
  echo "Unable to locate spec file: $SPEC_FILE" >&2
  exit 1
fi

echo "Running PyInstaller"
pyinstaller "$SPEC_FILE" --noconfirm

PORTABLE_SRC="$ROOT_DIR/dist/lockers"
if [[ ! -d "$PORTABLE_SRC" ]]; then
  echo "PyInstaller output not found at $PORTABLE_SRC" >&2
  exit 1
fi

PORTABLE_DIR="$RELEASE_DIR/LockersCL-linux-x64"
rm -rf "$PORTABLE_DIR"
cp -R "$PORTABLE_SRC" "$PORTABLE_DIR"

tarball="$RELEASE_DIR/LockersCL-linux-x64.tar.gz"
rm -f "$tarball"
tar -C "$PORTABLE_SRC" -czf "$tarball" .

if ! command -v fpm >/dev/null 2>&1; then
  echo "The fpm tool is required to build Debian packages." >&2
  if command -v gem >/dev/null 2>&1; then
    echo "Installing fpm via RubyGems"
    gem install --user-install fpm
    PATH="$(ruby -e 'print Gem.user_dir')/bin:$PATH"
  else
    echo "Install RubyGems or provide fpm in PATH." >&2
    exit 1
  fi
fi

DEB_PATH="$RELEASE_DIR/lockerscl_amd64.deb"
rm -f "$DEB_PATH"

fpm -s dir -t deb \
  -n lockerscl \
  -v "$VERSION" \
  --architecture amd64 \
  --description "Lockers Control kiosk launcher" \
  --depends python3 \
  --prefix /opt/lockers-cl \
  --package "$DEB_PATH" \
  --chdir "$PORTABLE_SRC" .

find "$RELEASE_DIR" -maxdepth 1 -type f ! -name 'SHA256SUMS' -print0 |
  sort -z |
  xargs -0 sha256sum > "$RELEASE_DIR/SHA256SUMS"
