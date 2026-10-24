#!/usr/bin/env bash
# Rebuild the lan branch from scratch: the upstream release tag in lan.json
# with each listed fork branch merged onto it, in order. lan is never edited
# by hand -- change lan.json instead -- so the fix branches stay clean for
# their upstream PRs. Run from a full-history clone whose origin is the fork.
#
# Prints sha=<commit> and unchanged=true|false (to $GITHUB_OUTPUT in CI).
# When the rebuilt tree matches origin/lan, lan stays at origin/lan, so an
# unchanged rebuild never makes the server reinstall the same code.
set -euo pipefail

config=${1:?usage: rebuild-lan.sh <lan.json>}
out=${GITHUB_OUTPUT:-/dev/stdout}

field() {
  python3 - "$config" "$1" <<'EOF'
import json, sys
config = json.load(open(sys.argv[1]))
value = config[sys.argv[2]]
print("\n".join(b["name"] for b in value) if sys.argv[2] == "branches" else value)
EOF
}

upstream=$(field upstream)
base=$(field base)

git remote get-url upstream >/dev/null 2>&1 || git remote add upstream "$upstream"
git fetch -q upstream "+refs/tags/$base:refs/tags/$base"
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*'

git checkout -q --detach "refs/tags/$base"
while read -r branch; do
  [ -n "$branch" ] || continue
  if ! git merge -q --no-ff --no-edit -m "lan: merge $branch" "origin/$branch"; then
    git merge --abort
    echo "::error::$branch does not merge cleanly onto $base and the branches listed before it." >&2
    exit 1
  fi
done < <(field branches)
git checkout -q -B lan

unchanged=false
if git rev-parse -q --verify refs/remotes/origin/lan >/dev/null \
  && [ "$(git rev-parse 'origin/lan^{tree}')" = "$(git rev-parse 'HEAD^{tree}')" ]; then
  git checkout -q -B lan origin/lan
  unchanged=true
fi

{
  echo "sha=$(git rev-parse HEAD)"
  echo "unchanged=$unchanged"
} >> "$out"
