#!/usr/bin/env python3
"""Checks the skills in this repo. Run from anywhere: python3 scripts/check.py

  --offline   skip the checks that need the network (live tool list, links)

Checks:
  1. Each skills/<name>/SKILL.md has frontmatter with `name` (matching its
     folder, kebab-case, at most 64 characters) and `description` (at most
     1024 characters).
  2. The version is the same in every manifest (.claude-plugin/plugin.json,
     marketplace.json, gemini-extension.json, .antigravity-plugin/plugin.json)
     and CHANGELOG.md has a dated section for it.
  2b. The Gemini CLI and Antigravity manifests connect to the hosted MCP
     server, and every ${VAR} in their headers is declared as a setting /
     variable the user is asked for. Online, the URL must be the server
     card's streamable-http URL.
  3. The tools named in the SchemaSketch skill are exactly the tools the
     live MCP server lists in its server card. Run daily in CI, so a server
     change that makes the skill out of date turns the badge red.
  4. Every https link in the skills and README answers (2xx after redirects).

Exit code 0 when everything passes, 1 otherwise.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_CARD = "https://schemasketch.dev/.well-known/mcp/server-card.json"
USER_AGENT = "schemasketch-skills-check/1.0"
offline = "--offline" in sys.argv[1:]
failures = []


def fail(message):
    failures.append(message)
    print(f"  FAIL  {message}")


def ok(message):
    print(f"  ok    {message}")


def fetch(url, method="GET"):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read() if method == "GET" else b""


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None, text
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("'\"")
    return fields, text


print("Skill frontmatter")
skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
if not skills:
    fail("no skills/<name>/SKILL.md found")
for path in skills:
    folder = path.parent.name
    fields, _ = frontmatter(path)
    if fields is None:
        fail(f"{folder}: SKILL.md has no frontmatter block")
        continue
    name, description = fields.get("name", ""), fields.get("description", "")
    if name != folder:
        fail(f"{folder}: name is {name!r}, must match the folder name")
    elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        fail(f"{folder}: name must be kebab-case and at most 64 characters")
    else:
        ok(f"{folder}: name")
    if not description:
        fail(f"{folder}: description is missing")
    elif len(description) > 1024:
        fail(f"{folder}: description is {len(description)} characters (max 1024)")
    else:
        ok(f"{folder}: description ({len(description)} characters)")

print("Versions")
plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
gemini = json.loads((ROOT / "gemini-extension.json").read_text())
antigravity = json.loads((ROOT / ".antigravity-plugin/plugin.json").read_text())
mcp_config = json.loads((ROOT / "mcp_config.json").read_text())
version = plugin.get("version", "")
listed = {p["name"]: p.get("version") for p in market.get("plugins", [])}
versions = {
    "marketplace.json": listed.get(plugin["name"]),
    "gemini-extension.json": gemini.get("version"),
    ".antigravity-plugin/plugin.json": antigravity.get("version"),
}
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    fail(f"plugin.json version {version!r} is not X.Y.Z")
else:
    wrong = {f: v for f, v in versions.items() if v != version}
    for f, v in wrong.items():
        fail(f"{f} is at {v!r}, .claude-plugin/plugin.json says {version}")
    if not wrong:
        ok(f"all {len(versions) + 1} manifests at {version}")
for f, name in (("gemini-extension.json", gemini.get("name")), (".antigravity-plugin/plugin.json", antigravity.get("name"))):
    if name != plugin["name"]:
        fail(f"{f} name is {name!r}, expected {plugin['name']!r}")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if re.search(rf"^## {re.escape(version)} \(\d{{4}}-\d{{2}}-\d{{2}}\)", changelog, re.M):
    ok(f"CHANGELOG.md has a dated {version} section")
else:
    fail(f"CHANGELOG.md has no '## {version} (YYYY-MM-DD)' section")

print("Gemini CLI and Antigravity connect the MCP server")
placeholder = re.compile(r"\$\{(\w+)\}")
servers = {
    "gemini-extension.json": (
        gemini.get("mcpServers", {}).get("schemasketch", {}),
        "httpUrl",
        {s.get("envVar") for s in gemini.get("settings", [])},
    ),
    "mcp_config.json": (
        mcp_config.get("mcpServers", {}).get("schemasketch", {}),
        "serverUrl",
        {v.get("name") for v in mcp_config.get("mcpServers", {}).get("schemasketch", {}).get("variables", [])},
    ),
}
server_urls = {}
for f, (server, url_key, declared) in servers.items():
    url = server.get(url_key)
    if not url:
        fail(f"{f}: no schemasketch server with {url_key!r}")
        continue
    server_urls[f] = url
    used = set(placeholder.findall(json.dumps(server.get("headers", {}))))
    if not used:
        fail(f"{f}: the server has no ${{...}} token in its headers")
    elif used - declared:
        fail(f"{f}: {', '.join(sorted(used - declared))} used in headers but never asked for")
    else:
        ok(f"{f}: {url}, token from {', '.join(sorted(used))}")

skill_path = ROOT / "skills/schemasketch/SKILL.md"
_, skill_text = frontmatter(skill_path)

if offline:
    print("Network checks skipped (--offline)")
else:
    print("Tools match the live MCP server")
    try:
        _, body = fetch(SERVER_CARD)
        card = json.loads(body)
        live = {t["name"] for t in card["tools"]}
        hosted = {t.get("url") for t in card.get("transport", []) if t.get("type") == "streamable-http"}
        for f, url in server_urls.items():
            if url in hosted:
                ok(f"{f} uses the server card's hosted URL")
            else:
                fail(f"{f} uses {url}, the server card lists {', '.join(sorted(filter(None, hosted))) or 'no hosted URL'}")
        section = skill_text.split("## Tools available", 1)[-1]
        named = set(re.findall(r"`([a-z]+(?:_[a-z]+)+)`", section))
        if named == live:
            ok(f"{len(live)} tools, same as the server card")
        else:
            if live - named:
                fail(f"missing from the skill: {', '.join(sorted(live - named))}")
            if named - live:
                fail(f"no longer on the server: {', '.join(sorted(named - live))}")
        mentioned = set(re.findall(r"`([a-z]+(?:_[a-z]+)+)`", skill_text))
        unknown = {n for n in mentioned - live if n.split("_")[0] in {"get", "list", "create", "update", "delete", "export", "import", "validate"}}
        if unknown:
            fail(f"the skill refers to tools the server doesn't have: {', '.join(sorted(unknown))}")
    except Exception as e:  # network or format problem: report, don't crash
        fail(f"could not read {SERVER_CARD}: {e}")

    print("Links")
    texts = [p.read_text(encoding="utf-8") for p in skills] + [(ROOT / "README.md").read_text(encoding="utf-8")]
    links = sorted({u.rstrip(".,)") for t in texts for u in re.findall(r"https://[^\s)\"'<>`\]]+", t)})
    for url in links:
        if "img.shields.io" in url or "/actions/workflows/" in url:
            continue  # badges: checked by rendering, not here
        try:
            status, _ = fetch(url.split("#")[0])
            ok(f"{status} {url}")
        except Exception as e:
            fail(f"{url}: {e}")

print()
if failures:
    print(f"{len(failures)} check(s) failed.")
    sys.exit(1)
print("All checks passed.")
