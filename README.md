# SchemaSketch Skills

[![check](https://github.com/SchemaSketch-dev/schemasketch-skills/actions/workflows/check.yml/badge.svg)](https://github.com/SchemaSketch-dev/schemasketch-skills/actions/workflows/check.yml)
[![release](https://img.shields.io/github/v/release/SchemaSketch-dev/schemasketch-skills?label=release)](https://github.com/SchemaSketch-dev/schemasketch-skills/releases)
[![skills.sh](https://img.shields.io/badge/skills.sh-schemasketch-black)](https://www.skills.sh/sioannides/schemasketch-skills)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-D97757)](#claude-code-plugin)
[![Gemini CLI extension](https://img.shields.io/badge/Gemini%20CLI-extension-4285F4)](#gemini-cli-extension)
[![Codex plugin](https://img.shields.io/badge/Codex-plugin-000000)](#openai-codex-plugin)
[![Cursor plugin](https://img.shields.io/badge/Cursor-plugin-000000)](#cursor-plugin)
[![license](https://img.shields.io/github/license/SchemaSketch-dev/schemasketch-skills)](LICENSE)

Agent skills for working with [SchemaSketch](https://schemasketch.dev), a free
hosted database-diagramming tool, via its MCP server.

## Install

### Any agent (skills CLI)

Using the [`skills` CLI](https://github.com/vercel-labs/skills) (works with Claude Code,
Cursor, OpenCode, Codex, and other compatible agents):

```bash
npx skills add SchemaSketch-dev/schemasketch-skills
```

This copies `skills/schemasketch/SKILL.md` into your agent's local skills directory (e.g.
`~/.claude/skills/` for Claude Code), where it auto-loads whenever a conversation matches its
description. Update later with `npx skills update`.

### Claude Code plugin

Installs the skill **and** connects the SchemaSketch MCP server:

```
/plugin install schemasketch --marketplace SchemaSketch-dev/schemasketch-skills
```

When you enable it, Claude Code asks for your SchemaSketch token (in the app: **Connect AI
agent**) and keeps it as a secret. If you added the SchemaSketch MCP server by hand before,
remove that entry (`claude mcp remove schemasketch`) so the tools don't show up twice.

Or in two steps on older Claude Code versions:

```
/plugin marketplace add SchemaSketch-dev/schemasketch-skills
/plugin install schemasketch@schemasketch
```

### Gemini CLI extension

Installs the skill **and** connects the SchemaSketch MCP server in one step:

```bash
gemini extensions install https://github.com/SchemaSketch-dev/schemasketch-skills
```

It asks for your SchemaSketch token (get one at [schemasketch.dev/app](https://schemasketch.dev/app):
"Connect AI agent" → Hosted) and keeps it in your system keychain. Change it later with
`gemini extensions config schemasketch`. Update with `gemini extensions update schemasketch`.

### Antigravity plugin

Also installs the skill and connects the MCP server:

```bash
agy plugin install https://github.com/SchemaSketch-dev/schemasketch-skills
agy plugin enable schemasketch
```

Enabling it asks for your SchemaSketch token.

### OpenAI Codex plugin

Installs the skill and connects the MCP server:

```bash
codex plugin marketplace add SchemaSketch-dev/schemasketch-skills
```

Then enter `/plugins` in Codex, install **SchemaSketch**, and paste your SchemaSketch token
when Codex asks for it on connecting.

### Cursor plugin

Installs the skill and connects the MCP server. Add this repository as a plugin
(Settings → Plugins, or a team marketplace) and fill in **SchemaSketch token** when Cursor
asks for it (change it later with **Configure**).

### Devin Desktop / Windsurf plugin

Installs the skill and connects the MCP server:

```bash
devin plugins install SchemaSketch-dev/schemasketch-skills
```

It needs your SchemaSketch token for the `SCHEMASKETCH_TOKEN` placeholder.

### GitHub Copilot CLI and Kiro

Both install the skill from this repository:

```bash
copilot plugin install SchemaSketch-dev/schemasketch-skills
```

In Kiro: Powers → **Add Custom Power** → **Import power from GitHub** → paste
`https://github.com/SchemaSketch-dev/schemasketch-skills`.

Neither can fill a token into a plugin's server settings, so the plugin's `schemasketch`
server can't sign in on its own. Add the token once in the agent's MCP settings (header
`Authorization: Bearer <your token>` for `https://mcp.schemasketch.dev/mcp`), or ask the
agent to follow [schemasketch.dev/agent-setup/prompt.md](https://schemasketch.dev/agent-setup/prompt.md).

### OpenCode

The skills CLI above installs the skill. To connect the server, add this to `opencode.json`
and set `SCHEMASKETCH_TOKEN` in your environment:

```jsonc
{
  "mcp": {
    "servers": {
      "schemasketch": {
        "type": "remote",
        "url": "https://mcp.schemasketch.dev/mcp",
        "oauth": false,
        "headers": { "Authorization": "Bearer {env:SCHEMASKETCH_TOKEN}" }
      }
    }
  }
}
```

## What's in here

- **`skills/schemasketch/`** — how to use SchemaSketch's 15 MCP tools effectively: what the
  save-time validation checks, editing safely (`base_version`, and `renames` so migrations rename
  instead of dropping data), converting SQL/Mermaid/PlantUML in and out of DBML, exporting Laravel
  migrations and Eloquent models, and when to suggest the `schemasketch/laravel` package.

The repository is packaged for each agent:

| File | Read by |
|---|---|
| `.claude-plugin/` | Claude Code marketplace (lists the plugin below) |
| `plugins/schemasketch/` | Claude Code plugin, as submitted to Anthropic's plugin directory (its `SKILL.md` is a copy of `skills/schemasketch/SKILL.md`, checked by `scripts/check.py`) |
| `gemini-extension.json` | Gemini CLI |
| `.antigravity-plugin/`, `mcp_config.json` | Antigravity |
| `plugin.json`, `mcp.json` ([Agent Plugins 1.0](https://agent-plugins.org)) | Codex, GitHub Copilot CLI, Kiro |
| `.agents/plugins/marketplace.json` | Codex marketplace |
| `.cursor-plugin/` | Cursor |
| `.devin-plugin/` | Devin Desktop / Windsurf |

The skills CLI installs the skill only, not the MCP connection
(the Claude Code, Gemini CLI, Antigravity, Codex, Cursor and Devin installs above do both). To connect, point your agent at
[schemasketch.dev/agent-setup/prompt.md](https://schemasketch.dev/agent-setup/prompt.md), which is
written to be fetched and executed directly by an agent.

## Tests

`python3 scripts/check.py` (no dependencies) checks that:

- every skill's frontmatter is valid (name matches its folder, description length);
- the name and version are the same in every manifest and the version has a changelog entry;
- every plugin that connects the server uses the server card's hosted URL with a token the
  user is asked for (and `mcp.json` has no headers, since Copilot CLI would send a
  `${...}` placeholder as text);
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
