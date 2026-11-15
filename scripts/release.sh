#!/usr/bin/env bash
# Releases a new version of the SchemaSketch skills, in two steps with a
# review in between (same flow as the schemasketch/laravel package):
#
#   scripts/release.sh patch     # 1.0.0 -> 1.0.1   wording or link fixes
#   scripts/release.sh minor     # 1.0.1 -> 1.1.0   new guidance (new tools, workflows)
#   scripts/release.sh major     # 1.1.0 -> 2.0.0   changes that break old setups
#       Prepares the release on dev: runs the checks, bumps the version in
#       .claude-plugin/plugin.json and marketplace.json, dates the changelog,
#       commits "Release X.Y.Z", pushes dev and opens a pull request to main.
#
#   scripts/release.sh tag
#       After that pull request is merged: tags vX.Y.Z on main and pushes the
#       tag (GitHub then checks it and publishes the release), and brings dev
#       up to date with main.
#
#   add --dry-run to see what would happen without changing anything
set -euo pipefail

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

mode="" dry=0
for arg in "$@"; do
  case "$arg" in
    patch|minor|major|tag) mode="$arg" ;;
    --dry-run) dry=1 ;;
    *) usage ;;
  esac
done
[ -n "$mode" ] || usage

cd "$(git rev-parse --show-toplevel)"
fail() { echo "release: $*" >&2; exit 1; }
run() { if [ "$dry" = 1 ]; then echo "  would run: $*"; else "$@"; fi; }

[ -z "$(git status --porcelain)" ] || fail "commit or stash your changes first."
git fetch --quiet --tags origin
latest=$(git tag --list 'v[0-9]*.[0-9]*.[0-9]*' --sort=-v:refname | head -n1)
above() { [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -n1)" = "$2" ] && [ "$1" != "$2" ]; }
current=$(python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["version"])')

# ---------------------------------------------------------------------------
# Step 2: tag the merged release on main.
# ---------------------------------------------------------------------------
if [ "$mode" = tag ]; then
  version=$(git show origin/main:.claude-plugin/plugin.json | python3 -c 'import json,sys;print(json.load(sys.stdin)["version"])')
  git rev-parse -q --verify "refs/tags/v$version" >/dev/null && fail "main is at $version, which is already tagged. Merge the release pull request first."
  [ -z "$latest" ] || above "${latest#v}" "$version" || fail "v$version is not above $latest."
  git show origin/main:CHANGELOG.md | grep -q "^## $version (" || fail "main's CHANGELOG.md has no dated $version section."

  echo "Tagging v$version on main ($(git rev-parse --short origin/main))"
  run git tag -a "v$version" -m "$version" origin/main
  run git push --quiet origin "v$version"

  start=$(git rev-parse --abbrev-ref HEAD)
  run git checkout --quiet dev
  run git merge --quiet --ff-only origin/main
  run git push --quiet origin dev
  [ "$dry" = 1 ] || [ "$start" = dev ] || git checkout --quiet "$start"

  [ "$dry" = 1 ] && echo "Dry run: nothing changed." \
    || echo "Tagged v$version. GitHub checks the tag and publishes the release."
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 1: prepare the release on dev and open the pull request.
# ---------------------------------------------------------------------------
[ "$(git rev-parse --abbrev-ref HEAD)" = dev ] || fail "switch to the dev branch first."
[ "$(git rev-parse dev)" = "$(git rev-parse origin/dev)" ] || fail "dev differs from origin/dev; pull or push it first."
git merge-base --is-ancestor origin/main dev || fail "main has commits dev doesn't. Run: git merge origin/main (on dev) first."

IFS=. read -r major minor patch <<<"$current"
case "$mode" in
  patch) patch=$((patch + 1)) ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  major) major=$((major + 1)); minor=0; patch=0 ;;
esac
next="$major.$minor.$patch"
git rev-parse -q --verify "refs/tags/v$next" >/dev/null && fail "v$next already exists."

notes=$(awk '/^## Unreleased/{f=1;next} /^## /{f=0} f' CHANGELOG.md | sed '/^[[:space:]]*$/d')
[ -n "$notes" ] || fail 'the "## Unreleased" section in CHANGELOG.md is empty. Say what changed.'

echo "Preparing $current -> $next ($mode)"
echo "$notes" | sed 's/^/  /'

if [ "$dry" = 1 ]; then
  echo "  would set version $next in .claude-plugin/plugin.json and marketplace.json"
  echo "  would rename \"## Unreleased\" to \"## $next ($(date +%F))\" in CHANGELOG.md"
else
  python3 - "$next" <<'PY'
import json, sys
version = sys.argv[1]
for path in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
    data = json.load(open(path))
    if "plugins" in data:
        for plugin in data["plugins"]:
            plugin["version"] = version
    else:
        data["version"] = version
    open(path, "w").write(json.dumps(data, indent=2) + "\n")
PY
  awk -v heading="## $next ($(date +%F))" \
    '/^## Unreleased/ && !done {print "## Unreleased\n\n" heading; done=1; next} {print}' \
    CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
fi
run python3 scripts/check.py
run git commit --quiet -am "Release $next"
run git push --quiet origin dev

body="Release $next. Merge with a merge commit (not squash), then run \`scripts/release.sh tag\`.

$notes"
if [ "$dry" = 1 ]; then
  echo "  would open a pull request dev -> main titled \"Release $next\""
  echo "Dry run: nothing changed."
else
  existing=$(gh pr list --base main --head dev --state open --json number --jq '.[0].number' 2>/dev/null || true)
  if [ -n "$existing" ]; then
    gh api -X PATCH "repos/{owner}/{repo}/pulls/$existing" -f title="Release $next" -f body="$body" >/dev/null
    url=$(gh pr view "$existing" --json url --jq .url)
  else
    url=$(gh pr create --base main --head dev --title "Release $next" --body "$body")
  fi
  echo "Pull request ready: $url"
  echo "Review and merge it (merge commit, not squash), then run: scripts/release.sh tag"
fi
