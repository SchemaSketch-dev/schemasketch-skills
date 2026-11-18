# SchemaSketch plugin for Claude Code

Design, edit, validate, import and export database diagrams with
[SchemaSketch](https://schemasketch.dev): SQL DDL for PostgreSQL, MySQL, SQL Server and
Oracle, Laravel migrations and Eloquent models, Mermaid and PlantUML.

Install:

```
/plugin install schemasketch --marketplace SchemaSketch-dev/schemasketch-skills
```

The plugin adds the `schemasketch` skill and connects SchemaSketch's hosted MCP server
(`https://mcp.schemasketch.dev/mcp`). When you enable it, Claude Code asks for your
SchemaSketch token: create one in the app under **Connect AI agent**. Claude Code keeps it
in secure storage and sends it only to the SchemaSketch server.

If you added the SchemaSketch MCP server by hand before, remove that entry so the tools
don't appear twice.

- Docs: https://schemasketch.dev/docs#mcp-docs
- Privacy: https://schemasketch.dev/privacy
- Source and issues: https://github.com/SchemaSketch-dev/schemasketch-skills
- License: MIT (see LICENSE)
