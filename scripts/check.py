#!/usr/bin/env python3
"""Checks the skills in this repo. Run from anywhere: python3 scripts/check.py

  --offline   skip the checks that need the network (live tool list, links)

Checks:
  1. Each skills/<name>/SKILL.md has frontmatter with `name` (matching its
     folder, kebab-case, at most 64 characters) and `description` (at most
     1024 characters).
  2. The version in .claude-plugin/plugin.json and marketplace.json match,
     and CHANGELOG.md has a section for it (or it's under "Unreleased").
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
version = plugin.get("version", "")
listed = {p["name"]: p.get("version") for p in market.get("plugins", [])}
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    fail(f"plugin.json version {version!r} is not X.Y.Z")
elif listed.get(plugin["name"]) != version:
    fail(f"marketplace.json lists {plugin['name']} at {listed.get(plugin['name'])!r}, plugin.json says {version}")
else:
    ok(f"plugin.json and marketplace.json both at {version}")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if re.search(rf"^## {re.escape(version)} \(\d{{4}}-\d{{2}}-\d{{2}}\)", changelog, re.M):
    ok(f"CHANGELOG.md has a dated {version} section")
else:
    fail(f"CHANGELOG.md has no '## {version} (YYYY-MM-DD)' section")

skill_path = ROOT / "skills/schemasketch/SKILL.md"
_, skill_text = frontmatter(skill_path)

if offline:
    print("Network checks skipped (--offline)")
else:
    print("Tools match the live MCP server")
    try:
        _, body = fetch(SERVER_CARD)
        live = {t["name"] for t in json.loads(body)["tools"]}
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
