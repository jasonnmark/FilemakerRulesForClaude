---
name: filemaker-update
description: Refresh FileMaker tooling — pull the latest database schema for this project and update the filemaker-rules plugin to the newest rules. Use when the user says "update filemaker skills", "update filemaker rules", "refresh the schema", "sync filemaker", or when a filemaker-rules freshness nudge asks for it.
---

# Update FileMaker tooling

Run both steps, then report. One Bash call per command (never chain with `&&`/`;`/`|`).

## 1. Update the rules plugin
- `claude plugin marketplace update jason-filemaker`
- `claude plugin update filemaker-rules@jason-filemaker`
- If the version changed, tell the user: **restart Claude Code to apply the new rules.** Do not force a restart mid-task — just inform.

## 2. Pull the latest schema
Locate this project's schema repo — a git repo (usually the `Schema/` folder in the project) whose `origin` remote is a private `*-Schema` repo on `github.com/jasonnmark` (for the Map solution: `Map-Schema`).

- Try `"$CLAUDE_PROJECT_DIR/Schema"` first; otherwise search the project dir for a `.git` whose `origin` ends in `-Schema`.
- Found → `git -C <path> pull`. Report "already up to date" or what changed.
- Not found → tell the user the schema repo isn't cloned here, with the clone command (run inside the project folder):
  `git clone https://github.com/jasonnmark/Map-Schema.git Schema`
  (Requires read access to the private repo.)

## 3. Report
One short summary: plugin version before → after, schema pull result, and whether a restart is needed. If nothing changed anywhere, say so in a single line.
