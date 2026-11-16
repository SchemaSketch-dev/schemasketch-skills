# SchemaSketch Skills

[![check](https://github.com/sioannides/schemasketch-skills/actions/workflows/check.yml/badge.svg)](https://github.com/sioannides/schemasketch-skills/actions/workflows/check.yml)
[![release](https://img.shields.io/github/v/release/sioannides/schemasketch-skills?label=release)](https://github.com/sioannides/schemasketch-skills/releases)
[![skills.sh](https://img.shields.io/badge/skills.sh-schemasketch-black)](https://www.skills.sh/sioannides/schemasketch-skills)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-D97757)](#claude-code-plugin)
[![Gemini CLI extension](https://img.shields.io/badge/Gemini%20CLI-extension-4285F4)](#gemini-cli-extension)
[![license](https://img.shields.io/github/license/sioannides/schemasketch-skills)](LICENSE)

Agent skills for working with [SchemaSketch](https://schemasketch.dev), a free
hosted database-diagramming tool, via its MCP server.

## Install

### Any agent (skills CLI)

Using the [`skills` CLI](https://github.com/vercel-labs/skills) (works with Claude Code,
Cursor, OpenCode, Codex, and other compatible agents):

```bash
npx skills add sioannides/schemasketch-skills
```

This copies `skills/schemasketch/SKILL.md` into your agent's local skills directory (e.g.
`~/.claude/skills/` for Claude Code), where it auto-loads whenever a conversation matches its
description. Update later with `npx skills update`.

### Claude Code plugin

```
/plugin install schemasketch --marketplace sioannides/schemasketch-skills
```

Or in two steps on older Claude Code versions:

```
/plugin marketplace add sioannides/schemasketch-skills
/plugin install schemasketch@schemasketch
```

### Gemini CLI extension

Installs the skill **and** connects the SchemaSketch MCP server in one step:

```bash
gemini extensions install https://github.com/sioannides/schemasketch-skills
```

It asks for your SchemaSketch token (get one at [schemasketch.dev/app](https://schemasketch.dev/app):
"Connect AI agent" → Hosted) and keeps it in your system keychain. Change it later with
`gemini extensions config schemasketch`. Update with `gemini extensions update schemasketch`.

### Antigravity plugin

Also installs the skill and connects the MCP server:

```bash
agy plugin install https://github.com/sioannides/schemasketch-skills
agy plugin enable schemasketch
```

Enabling it asks for your SchemaSketch token.

## What's in here

- **`skills/schemasketch/`** — how to use SchemaSketch's 15 MCP tools effectively: what the
  save-time validation checks, editing safely (`base_version`, and `renames` so migrations rename
  instead of dropping data), converting SQL/Mermaid/PlantUML in and out of DBML, exporting Laravel
  migrations and Eloquent models, and when to suggest the `schemasketch/laravel` package.

The skills CLI and the Claude Code plugin install the skill only, not the MCP connection
(the Gemini CLI and Antigravity installs above do both). To connect, point your agent at
[schemasketch.dev/agent-setup/prompt.md](https://schemasketch.dev/agent-setup/prompt.md), which is
written to be fetched and executed directly by an agent.

## Tests

`python3 scripts/check.py` (no dependencies) checks that:

- every skill's frontmatter is valid (name matches its folder, description length);
- the version is the same in every manifest (Claude Code, Gemini CLI, Antigravity) and has a
  changelog entry;
- the Gemini CLI and Antigravity manifests connect to the server card's hosted URL, and every
  token in their headers is one the user is asked for;
- the tools the skill names are exactly the tools the live MCP server lists in its
  [server card](https://schemasketch.dev/.well-known/mcp/server-card.json);
- every link answers.

CI runs it on every push and pull request, and **daily**, so a change to the MCP server
that the skill doesn't cover yet turns the check badge red. CI also runs
`claude plugin validate .`.

## Versions and releases

Semantic versioning; see [CHANGELOG.md](CHANGELOG.md). Work happens on `dev`, with
changes noted under "Unreleased". `scripts/release.sh patch|minor|major` bumps the
version, dates the changelog and opens a pull request to `main`; after it is merged,
`scripts/release.sh tag` tags it, and GitHub publishes the release.

## License

MIT — see [LICENSE](LICENSE).
