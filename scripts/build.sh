#!/usr/bin/env bash
# The one build, locally (`npm run check`) and on Netlify (netlify.toml). Fails the deploy if any gate fails.
#
#   1. Tailwind classes in canonical order
#   2. Clean Hugo build (no stale files survive in public/)
#   3. Every legacy URL resolves, simulating Netlify's redirect rules against public/_redirects
#   4. SEO audit: one <h1>, title, description, canonical, og:image, valid JSON-LD, alt text (production only)
#
# Netlify sets CONTEXT (production | deploy-preview | branch-deploy) and DEPLOY_PRIME_URL.
# Previews build with --environment preview: noindex on every page and a robots.txt that disallows all.
set -euo pipefail
cd "$(dirname "$0")/.."

context="${CONTEXT:-production}"
args=(--gc --minify --cleanDestinationDir)
if [[ "$context" != production ]]; then
  args+=(--environment preview --baseURL "${DEPLOY_PRIME_URL:-http://localhost:1313}/")
fi

echo "▸ context: $context"
hugo version
node scripts/tailwind/sort-classes.mjs --check
hugo "${args[@]}"
node scripts/migration/linkcheck.mjs public scripts/migration/legacy-urls.txt
if [[ "$context" == production ]]; then
  python3 -I scripts/migration/audit.py public scripts/migration/legacy-urls.txt public/_redirects
fi
