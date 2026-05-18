#!/bin/bash
set -euo pipefail

# Build mobile app with Expo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MOBILE_DIR="$PROJECT_DIR/mobile"

cd "$MOBILE_DIR"

if ! command -v npx &> /dev/null; then
    echo "ERROR: Node.js / npm not found. Install from https://nodejs.org/"
    exit 1
fi

echo "Installing dependencies..."
npm install

echo ""
echo "Running linter..."
npx eslint . --ext .js,.jsx

echo ""
echo "Running tests..."
npx jest --coverage

echo ""
echo "Building preview APK..."
npx eas build --platform android --profile preview

echo "✓ Mobile build complete"
