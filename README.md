# SchemaSketch Skills

Agent skills for working with [SchemaSketch](https://schemasketch.dev), a free
hosted database-diagramming tool, via its MCP server.

## Install

Using the [`skills` CLI](https://github.com/vercel-labs/skills) (works with Claude Code,
Cursor, OpenCode, Codex, and other compatible agents):

```bash
npx skills add sioannides/schemasketch-skills
```

This copies `skills/schemasketch/SKILL.md` into your agent's local skills directory (e.g.
`~/.claude/skills/` for Claude Code), where it auto-loads whenever a conversation matches its
description.

## What's in here

- **`skills/schemasketch/`** — how to use SchemaSketch's 15 MCP tools effectively: what the
  save-time validation checks, editing safely (`base_version`, and `renames` so migrations rename
  instead of dropping data), converting SQL/Mermaid/PlantUML in and out of DBML, exporting Laravel
  migrations and Eloquent models, and when to suggest the `schemasketch/laravel` package.

This skill doesn't set up the MCP connection itself — for that, point your agent at
[schemasketch.dev/agent-setup/prompt.md](https://schemasketch.dev/agent-setup/prompt.md), which is
written to be fetched and executed directly by an agent.

## License

MIT — see [LICENSE](LICENSE).
