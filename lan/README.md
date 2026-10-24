# LAN build

The LAN Zotero MCP server (`zotero-mcp.localdomain`) runs the `lan` branch:
the upstream release named in `lan.json` with this fork's pending fix
branches merged onto it. This tooling lives on the fork's `main`, which is
upstream `main` plus this one commit; scheduled and manual workflows only run
from the default branch.

- **Change what the server runs** by editing `lan.json`: add a fix branch
  while its upstream PR is pending, remove it once an upstream release
  includes it, and move `base` to that release.
- **`lan` is rebuilt, never edited.** The `LAN build` workflow
  (`.github/workflows/lan.yml`) recreates it from `base` and the listed
  branches, runs the tests, and only then pushes it and marks the commit
  with a `lan/tests` success status. A branch that no longer merges cleanly
  fails the build and leaves `lan` where it was.
- **Deploy** from the concept-clusters checkout with
  `npm run zotero:deploy`. It runs this workflow, waits for it, installs
  the tested `lan` commit into the server's venv, restarts the service,
  health-checks it, and reinstalls the previous commit if the check fails.

Upstream's `release.yml` and `docker.yml` are removed here (and disabled in
the fork's Actions settings) so the fork never tries to publish to PyPI or
GHCR.
