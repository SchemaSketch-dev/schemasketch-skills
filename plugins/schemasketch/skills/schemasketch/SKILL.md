---
name: schemasketch
description: Use when the user wants to design, edit, validate, import, or export a database schema/ER diagram — creates and manages SchemaSketch diagrams via its MCP server, and can convert to/from real SQL DDL, Laravel migrations and Eloquent models, Mermaid erDiagram, or PlantUML entity syntax.
---

# SchemaSketch

SchemaSketch (https://schemasketch.dev) is a free, hosted database diagram
tool. Diagrams are written in a small DBML-like text language, rendered
live, and stored on the user's account. This skill covers working with it
via its MCP server rather than the web UI.

## Setup

The tools below come from the SchemaSketch MCP server. If they aren't
available, the server isn't connected yet: tell the user, and point them to
the setup guide for their client at https://schemasketch.dev/docs#mcp-docs
(it covers getting a token from the app's **Connect AI agent** menu and
connecting Claude Code, Claude Desktop, Cursor and other clients). Token and
auth details: https://schemasketch.dev/auth.md

## Workflow

1. Call `get_dbml_syntax_guide` once per session before writing any DBML —
   it returns the exact syntax (table/column attributes, ref types, enums,
   subject areas) with a full example.
2. Draft the DBML for what the user described — or, if they handed you
   existing SQL DDL, a Mermaid `erDiagram`, or a PlantUML `entity` diagram
   instead, run it through `import_sql`/`import_mermaid`/`import_plantuml`
   first to get DBML back.
3. Optionally check a draft with `validate_dbml`. `create_diagram` and
   `update_diagram` run the same validator before saving: syntax errors or
   relationships to missing tables/columns mean nothing is saved (fix them
   and retry), and warnings (duplicate names, unrecognized types) come back
   with the result — mention any to the user.
4. Save it:
   - New diagram: `create_diagram` (name + dbml_source).
   - Editing an existing one: `get_diagram` first, edit its DBML, then
     `update_diagram` with the full new source and **`base_version`** set
     to the `version` you fetched. If someone else saved in between, the
     update is refused instead of overwriting their change — fetch again
     and reapply your edit.
   - **Renames:** whenever the edit renames a table, column, enum or table
     group, list each one in `renames` (`kind`, `from`, `to`, and `table`
     for a column). Without it a rename looks like a removed column plus a
     new one, and a migration generated from the diagram would drop the
     column and its data instead of renaming it.
   - Saved diagrams come back with a `url`; give it to the user so they can
     open the diagram.
5. On request, convert it back out: `export_sql` (dialect:
   postgres/mysql/mssql/oracle), `export_laravel_migrations`,
   `export_laravel_models` (Eloquent models with fillable, casts and
   inferred relationships, including belongsToMany through plain pivot
   tables; `laravel_version` 10 emits the legacy `$casts` property),
   `export_mermaid`, or `export_plantuml` — all accept either a saved
   `diagram_id` or raw `dbml_source` directly, so a schema doesn't need to
   be saved first just to export it.

## Laravel projects

If the user is working inside a Laravel app and wants the diagram kept in
step with the real database, suggest the `schemasketch/laravel` package
(`composer require schemasketch/laravel --dev`) instead of copying exports
by hand: `php artisan schemasketch:pull` (database → diagram), `diff` (drift
check for CI), `push` (one reviewed migration from diagram changes),
`export` and `status`. Docs: https://schemasketch.dev/laravel-package

## Tools available

`get_dbml_syntax_guide`, `list_diagrams`, `get_diagram`, `validate_dbml`,
`create_diagram`, `update_diagram`, `delete_diagram`, `export_sql`,
`export_laravel_migrations`, `export_laravel_models`, `export_mermaid`,
`export_plantuml`, `import_sql`, `import_mermaid`, `import_plantuml`. Full
parameter reference: https://schemasketch.dev/docs#mcp-docs and
https://schemasketch.dev/.well-known/mcp/server-card.json
