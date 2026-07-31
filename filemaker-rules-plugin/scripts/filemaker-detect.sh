#!/usr/bin/env bash
# UserPromptSubmit hook for the filemaker-rules plugin.
#
# UserPromptSubmit fires on EVERY prompt (no matcher support), so this script
# decides whether the current turn is FileMaker work. If it is, whatever we
# print to stdout is injected into Claude's context — we use that to force the
# non-negotiable rules in and tell Claude to load the full skill.
#
# Detection is deterministic: an explicit FileMaker keyword in the prompt, OR
# the project folder following the Schema/ + Spec_notes.md convention, OR an
# explicit .filemaker-project marker file. No match -> print nothing -> no-op.

set -uo pipefail

payload="$(cat)"                       # UserPromptSubmit event JSON on stdin
proj="${CLAUDE_PROJECT_DIR:-$PWD}"     # exported to hook processes by Claude Code

matched=0

# 1) Prompt mentions FileMaker explicitly. Tight keyword set = few false positives.
if printf '%s' "$payload" | grep -qiE 'filemaker|fmp12|fmxmlsnippet|clipboard xml'; then
  matched=1
fi

# 2) The project looks like a FileMaker solution folder.
if [ "$matched" -eq 0 ]; then
  if [ -f "$proj/Spec_notes.md" ] || [ -f "$proj/Schema/01_SCHEMA.md" ] || [ -f "$proj/.filemaker-project" ]; then
    matched=1
  fi
fi

if [ "$matched" -eq 1 ]; then
  cat <<'EOF'
[filemaker-rules] This session involves FileMaker. Before producing ANY FileMaker deliverable, invoke the `filemaker-conventions` skill and follow every rule in it. Non-negotiables even before the skill loads:
- Assume FileMaker 21+ on BOTH client and server. Never give steps, workarounds, or caveats for older versions.
- Refer to every object by its EXACT full name, emojis included — never an internal id, never truncated.
- Deliver script steps as paste-ready clipboard XML wrapped in the full <fmxmlsnippet type="FMObjectList"> envelope. Never bracketed pseudo-syntax like Set Field [ ... ].
- Put an empty `# (comment)` step (id 89, no Text) above each section-heading comment — blank XML lines render no gap.
- Read the project's Schema/ folder and Spec_notes.md before building anything.
EOF

  # Throttled freshness nudge: at most once every ~3 days, and only on FileMaker
  # work, ask Claude to silently refresh schema + rules via the filemaker-update
  # skill. Touch the stamp first so a failed refresh can't nag every prompt.
  stamp="$HOME/.claude/.filemaker-update-check"
  stale=0
  if [ ! -f "$stamp" ]; then
    stale=1
  elif [ -n "$(find "$stamp" -mtime +2 2>/dev/null)" ]; then
    stale=1
  fi
  if [ "$stale" -eq 1 ]; then
    mkdir -p "$(dirname "$stamp")" 2>/dev/null
    touch "$stamp" 2>/dev/null
    cat <<'EOF'
[filemaker-rules] It has been a few days since the last FileMaker refresh. Silently run the `filemaker-update` skill now — pull this project's latest schema (it improves the current task) and check for a rules-plugin update. Do this without derailing the user's request: if nothing changed, don't mention it; if the schema updated, use the fresh version; if the plugin updated, note in one line that a restart applies it, then continue.
EOF
  fi
fi

exit 0
