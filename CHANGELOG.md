# Changelog

Versions follow [Semantic Versioning](https://semver.org): a major release
changes what the skill tells agents to do in a way that breaks old setups,
a minor release adds guidance (new tools, new workflows), and a patch fixes
wording or links. Work happens on the `dev` branch: add changes under
"Unreleased" as you make them. `scripts/release.sh patch|minor|major` dates
that section, bumps the version in `.claude-plugin/` and opens a pull request
to `main`; once it is merged, `scripts/release.sh tag` tags the release.

## Unreleased

- The repository moved to the SchemaSketch organization on GitHub:
  https://github.com/SchemaSketch-dev/schemasketch-skills (old links and existing installs
  keep working through GitHub's redirect). Install commands now use the new path. No change
  to the skill itself.

## 1.1.0 (2026-11-16)

- Installable as a Gemini CLI extension (`gemini extensions install
  https://github.com/sioannides/schemasketch-skills`) and an Antigravity plugin
  (`agy plugin install …`). Both also connect the hosted MCP server, asking for
  the SchemaSketch token on install or enable.
- Checks and the release script cover the new manifests.

## 1.0.3 (2026-11-16)

- CI: `actions/setup-python` v5 → v7 (#7). No change to the skill itself.

## 1.0.2 (2026-11-16)

- CI: `actions/setup-node` v4 → v7 (#6). No change to the skill itself.

## 1.0.1 (2026-11-16)

- CI: `actions/checkout` v4 → v7 (#5). No change to the skill itself.

## 1.0.0 (2026-11-15)

First versioned release.

- Covers all 15 MCP tools, including `export_laravel_models`.
- Explains the save-time validation in `create_diagram` / `update_diagram`.
- Safe edits: `base_version`, and `renames` so generated migrations rename
  columns instead of dropping them.
- Saved diagrams return a `url` to give the user.
- Points Laravel projects to the `schemasketch/laravel` package.
- Installable as a Claude Code plugin (`/plugin marketplace add
  sioannides/schemasketch-skills`) as well as with `npx skills add`.
