#!/usr/bin/env bash
# Build the Setu image on the deploy box (arm64). Run from the repo root:  setu/deploy/build.sh 2.44.0-s1
set -euo pipefail
TAG=${1:?usage: build.sh <tag>}
cd "$(dirname "$0")/../.."
python3 setu/rebrand.py --check   # refuse to build an un-rebranded tree
echo "=== setu $(date -u +%T)"
docker buildx build --load --target twenty -f packages/twenty-docker/twenty/Dockerfile \
  --build-arg APP_VERSION="$TAG" -t "setu:$TAG" .
echo "=== done $(date -u +%T)"; docker images setu --format '{{.Repository}}:{{.Tag}} {{.Size}}'
