# FileMaker Rules — Claude Code plugin + marketplace

Ships a battle-tested FileMaker ruleset to any machine running Claude Code, and — crucially — **makes it fire automatically** whenever a session involves FileMaker.

- **Skill** (`filemaker-conventions`) — the full ruleset. Claude can load it on its own when a task matches its description.
- **Hook** (`UserPromptSubmit`) — the deterministic backstop. On every prompt it runs [`filemaker-detect.sh`](filemaker-rules-plugin/scripts/filemaker-detect.sh), and if the turn is FileMaker work it injects the non-negotiable rules into context and tells Claude to load the full skill. This is what guarantees the rules apply — a plain CLAUDE.md line can't do this.

The hook counts a turn as FileMaker work when **any** of these is true:
1. The prompt mentions `filemaker`, `fmp12`, `fmxmlsnippet`, or `clipboard xml`.
2. The project root has `Spec_notes.md`, `Schema/01_SCHEMA.md`, or a `.filemaker-project` marker file.

---

## Client setup (one time)

Run these two commands in a terminal (works from anywhere):

```bash
claude plugin marketplace add YOUR-GH-USER/filemaker-claude
```

```bash
claude plugin install filemaker-rules@jason-filemaker
```

> Replace `YOUR-GH-USER/filemaker-claude` with wherever this repo is pushed. The second command never changes — `jason-filemaker` is the marketplace name defined in `.claude-plugin/marketplace.json`, not the repo name.

If the first command clones over SSH and that isn't set up, prefer HTTPS:

```bash
CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 claude plugin marketplace add YOUR-GH-USER/filemaker-claude
```

Restart Claude Code (or run `/reload-plugins`) and it's live. Test it: start a session and type a prompt containing "FileMaker" — the rules should take effect.

## Getting updates ("match Jason's latest")

When the ruleset changes upstream, the client runs:

```bash
claude plugin marketplace update jason-filemaker
```

```bash
claude plugin update filemaker-rules
```

(Claude Code also background-refreshes marketplaces, so most of the time updates arrive on their own at session start. The two commands force it immediately.)

## Per-solution setup (the client's own schema)

The rules are universal; the **schema is per-solution**. For each FileMaker project the client works on, at the project root:

1. Create a `Schema/` folder holding the DDR export (the `01_SCHEMA.md … 10_SUMMARY.md` split). ⚠️ `Schema/` is disposable — it gets re-exported and overwritten wholesale, so nothing durable goes inside it.
2. Create a `Spec_notes.md` at the root for confirmed, solution-specific facts (naming quirks, color palettes, gotchas). This survives schema re-exports.

Having either file present also makes the hook auto-fire in that folder even if the word "FileMaker" never appears in the prompt. To force detection in a folder that has neither yet, `touch .filemaker-project` at its root.

---

## Maintaining this (for the author)

**This plugin's `SKILL.md` is the canonical ruleset.** To change a rule:

1. Edit [`filemaker-rules-plugin/skills/filemaker-conventions/SKILL.md`](filemaker-rules-plugin/skills/filemaker-conventions/SKILL.md).
2. `git commit` + `git push`.

That's it. `plugin.json` has no `version` field, so every pushed commit is treated as a new version — clients pick it up via the update commands above (or automatically at session start). No version bumping required.

To keep your own machine on the same source of truth, install the plugin on yours too (`claude plugin install filemaker-rules@jason-filemaker`) and drop the old `~/.claude/FileMakerRules.md` pointer from your CLAUDE.md — otherwise the two can drift.

### Layout

```
filemaker-claude/                              ← repo root = the marketplace
├── .claude-plugin/
│   └── marketplace.json                       ← catalog (marketplace name: jason-filemaker)
├── filemaker-rules-plugin/                    ← the plugin
│   ├── .claude-plugin/plugin.json
│   ├── skills/filemaker-conventions/SKILL.md  ← the ruleset (edit this)
│   ├── hooks/hooks.json                        ← registers the UserPromptSubmit hook
│   └── scripts/filemaker-detect.sh             ← deterministic FileMaker detector
└── README.md
```
