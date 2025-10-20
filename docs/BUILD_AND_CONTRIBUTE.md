# Build & Contribute Guide

## Architecture Overview

Lockers Control is composed of a small number of cooperating layers:

- **Django backend (`web/`, `cl/`)** – Hosts the QR-code workflow, persists active locker codes in SQLite/PostgreSQL, and exposes the operator dashboard. The backend relies on `web/locker.py` to translate between logical cells and the serial protocol used by the hardware controller.
- **Kiosk launcher (`lockers.py`)** – Boots the Django server in-process, embeds a GTK/WebKit browser where available, and falls back to the system browser when GUI bindings are missing. It exposes `DesktopApp` for orchestration and handles Ctrl+C shutdown.
- **Serial helpers (`web/locker.py`)** – Provide a configurable serial backend that defaults to `pyserial` but can be replaced via `locker.configure_serial_backend()` to support mocks and integration tests.
- **Android WebView (`android/`)** – A minimal Gradle project that wraps the Django UI in a Chromium WebView. It can start a bundled backend (Termux/chaquopy) or direct the kiosk to a LAN instance when local execution is not possible.
- **Automation (`scripts/`, `.github/workflows/release.yml`)** – Cross-platform build scripts plus a GitHub Actions workflow that runs tests, packages installers for the major operating systems, and publishes the vNEXT release.

## Developer Setup

### Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-build.txt  # packaging extras
```

Install the WiX toolset (`choco install wixtoolset --no-progress`) before running `scripts/build_windows.ps1`.

### macOS (Intel & Apple Silicon)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-build.txt
brew install cairo gtk+3 webkit2gtk pkg-config gnu-tar create-dmg
```

The build script `scripts/build_macos.sh` produces both the PyInstaller app bundle and `.dmg`, automatically handling universal2 binaries when Xcode command line tools are installed.

### Ubuntu 22.04/24.04

```bash
sudo apt update
sudo apt install -y build-essential python3.11 python3.11-venv python3-pip libgtk-3-dev libcairo2-dev gir1.2-webkit2-4.0 libssl-dev pkg-config
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-build.txt
```

Run `scripts/build_ubuntu.sh` to create both the `.deb` and `.tar.gz` release artefacts.

### Android

Install Android Studio (or the command-line tools) and ensure `ANDROID_HOME` / `ANDROID_SDK_ROOT` are configured. Then:

```bash
cd android
./gradlew doctor
./gradlew assembleDebug  # first build to warm caches
./gradlew assembleRelease
```

The Gradle project outputs the signed/unsigned APKs in `android/app/build/outputs/apk/` and the CI wrapper copies them into `dist/releases`.

## Running Tests with the Serial Mock

The Python test-suite configures a fake serial backend automatically via `locker.configure_serial_backend()`, so no special hardware setup is required. Execute the full suite with:

```bash
python -m pytest
```

The smoke test located in `tests/test_smoke.py` spins up the Django test client, generates a QR code, posts it to `/`, and ensures the PNG is removed after a mocked unlock succeeds.

For selective checks:

- `python -m pytest tests/test_desktop.py` – GTK/WebKit orchestration and browser fallback.
- `python -m pytest tests/test_smoke.py` – End-to-end QR workflow (skips automatically when Django is unavailable).

## Packaging Commands Used in CI

GitHub Actions mirrors the local scripts:

- **Windows** – `pyinstaller lockers.spec --noconfirm` followed by `scripts/build_windows.ps1`, which invokes WiX to produce `Lockers-Setup-x64.msi` and stages `Lockers-Setup-x64.exe`.
- **macOS** – `scripts/build_macos.sh` builds a universal2 app, runs optional `codesign`/`xcrun notarytool`, and packages a `.dmg` with `create-dmg`.
- **Ubuntu** – `scripts/build_ubuntu.sh` ensures `fpm` is present, invokes PyInstaller, builds `lockerscl_amd64.deb`, and archives the PyInstaller output as `LockersCL-linux-x64.tar.gz`.
- **Android** – `scripts/build_android.sh` wraps `./gradlew clean assembleRelease`, signs the APK when credentials are configured, and copies it into `dist/releases`.

After each build the scripts update `dist/releases/SHA256SUMS` (and optionally `SHA256SUMS.sig`) so the publish job can attach verified artefacts to the GitHub Release.

## FAQ & Troubleshooting

- **Which port does the backend listen on?** – The launcher defaults to `0.0.0.0:8090`. Override with the `DesktopConfig` dataclass or the `LOCKERS_HOST`/`LOCKERS_PORT` environment variables.
- **How do I point the kiosk at an existing server?** – Set `start_url` in `DesktopConfig` or export `LOCKERS_START_URL`. The Android wrapper exposes a settings pane when it cannot reach the local backend.
- **What if GTK/WebKit is missing?** – The launcher catches `DesktopDependencyError` and opens the system browser automatically. Install the packages listed above to restore the embedded kiosk view.
- **How do I specify the serial device?** – Set `LOCKER_SERIAL_PORT` (default `/dev/ttyUSB0`). Tests override the backend entirely via `locker.configure_serial_backend()`.
- **Pycairo or PyGObject build failures on Linux** – Install `build-essential libcairo2-dev gir1.2-webkit2-4.0 gir1.2-gtk-3.0` and retry. On headless CI, rely on the system browser fallback instead of GTK.
- **Unsigned builds on macOS/Windows** – Gatekeeper/SmartScreen will flag unsigned binaries. Control-click → *Open* (macOS) or *More info → Run anyway* (Windows) to approve community builds.

Contributions that improve packaging, documentation, or hardware support are welcome—open a Pull Request once `python -m pytest` passes locally.
