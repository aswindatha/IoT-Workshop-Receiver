#!/usr/bin/env bash
# Build script for the IoT Workshop Receiver (Linux / macOS / WSL)
set -euo pipefail

echo "==> Installing dependencies"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

if [ "${1:-}" = "--clean" ]; then
  echo "==> Cleaning previous build artifacts"
  rm -rf build dist
fi

echo "==> Building executable with PyInstaller"
pyinstaller --noconfirm receiver.spec

echo "==> Done. Output: dist/IoT-Workshop-Receiver/"
