#!/usr/bin/env bash
# check_version_doctrine.sh — UDS version-string doctrine check ("make doctrine"-style).
#
# Asserts ONE canonical UDS ecosystem version string (./VERSION, e.g. uds-v0.4.0)
# across user-visible docs/config in this repo. Polices ONLY the `uds-vX.Y.Z` token
# form (ignores bare semver / dependency versions).
#
# FORWARD-ONLY HONESTY (HARD RULE): already-SIGNED / published tags are NEVER renamed.
#   * uds-v0.2.0 — cosign-signed, Rekor-anchored flagship organ images.
#   * uds-v0.3.0 — signed capstone tag (BFT_SINGLE_SIGNER_CAVEAT.md, HONEST_ROLES.md).
#   * uds-v0.1.0 / uds-v1.0.0 — prior signed releases / roadmap quorum tag.
# These historical signed bytes are ALLOWLISTED. We cut NEW versioned releases forward.
#
# SUPERSEDED: the uds-v0.3.1 release plan (docs/UDS_v0.3.1_RELEASE_PLAN.md) and the
# BFT caveat doc retain their historical uds-v0.3.1 strings — allowlisted by path.
#
# Usage: bash scripts/check_version_doctrine.sh   (run from repo root)
# Exit:  0 = no unexpected drift, 1 = drift found.

set -euo pipefail
cd "$(dirname "$0")/.."

CANONICAL="$(tr -d '[:space:]' < VERSION)"
echo "=== UDS version doctrine check (uds-v* ecosystem tokens) ==="
echo "Canonical (VERSION): $CANONICAL"

ALLOWLIST_REGEX='^(uds-v0\.2\.0|uds-v0\.1\.0|uds-v1\.0\.0|uds-v0\.3\.0)$'
SUPERSEDED_PATHS_REGEX='docs/UDS_v0\.3\.1_RELEASE_PLAN\.md|docs/BFT_SINGLE_SIGNER_CAVEAT\.md'

DRIFT=0
while IFS= read -r -d '' f; do
  case "$f" in *.git/*) continue ;; esac
  hits=$(grep -oE 'uds-v[0-9]+\.[0-9]+\.[0-9]+' "$f" 2>/dev/null | sort -u || true)
  [ -z "$hits" ] && continue
  while IFS= read -r tok; do
    [ -z "$tok" ] && continue
    [ "$tok" = "$CANONICAL" ] && continue
    echo "$tok" | grep -qE "$ALLOWLIST_REGEX" && continue
    echo "$f" | grep -qE "$SUPERSEDED_PATHS_REGEX" && continue
    echo "  DRIFT: $f -> $tok (expected $CANONICAL or an allowlisted signed/superseded tag)"
    DRIFT=$((DRIFT+1))
  done <<< "$hits"
done < <(find . \( -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.cff' \) -type f -print0)

echo ""
if [ "$DRIFT" -eq 0 ]; then
  echo "=== RESULT: PASS — no unexpected uds-v* drift (canonical=$CANONICAL) ==="
  exit 0
else
  echo "=== RESULT: FAIL — $DRIFT unexpected uds-v* version disagreement(s) ==="
  echo "Fix: bump stale strings to $CANONICAL (forward-only). NEVER rename signed artifacts."
  exit 1
fi
