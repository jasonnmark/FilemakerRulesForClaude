---
name: filemaker-conventions
description: FileMaker development conventions and delivery format. Use whenever the task involves FileMaker or FileMaker Pro — building or editing scripts and script steps, producing clipboard XML snippets (fmxmlsnippet), calculations, layouts, value lists, custom functions, portals, ExecuteSQL against a .fmp12 solution, or installing/licensing plugins (BaseElements, MBS) on FileMaker Server.
---

# FileMaker Rules (ALL FileMaker projects)

> Single source of truth for FileMaker work. This skill loads automatically when a session involves FileMaker (a UserPromptSubmit hook detects it). Follow every rule below before delivering anything.

## 0. Refer to everything by NAME, never internal id

The developer works by script/field/layout/table name; internal ids are meaningless to them. An id may appear only as a quiet parenthetical. (Inside clipboard XML, `id=` attributes still belong — that's for the paste.)

Use the FULL exact name — never truncate, abbreviate, or strip emojis; they are part of the name and the developer searches by it. (Real violation: truncated `🌘📅NIGHTLY_REPORT_CompetencyByCycles_Cache🟥🟨🟩`. Don't repeat.)

Field naming — respect the developer's suffix conventions; never invent prefixes. Suffix already encodes type: `_c` = calculation, `_s` = summary, `_a`/`_g` = auto/global markers. Do NOT prepend `CALC`, `CALC_`, or similar — a `_c` field is already known to be a calc. When proposing a new field, lead with the subject noun so it alpha-sorts with siblings (e.g. `ProgramInitials_PowerSchoolExpected_c`, not `PowerSchoolExpected…`). (Real violation: named a file `CALC_…`. Don't repeat.)

Always cite a field with its BASE TABLE. Fields live on base tables (Manage Database → Fields, e.g. `ImportStudent`), NOT on relationship-graph occurrences (e.g. `🧑‍🎓_⬇️Import🧑‍🎓Students`) — the occurrence name won't appear in the Fields table dropdown. Whenever sharing/referencing a field, state which base table it's on so it can be found.

## 0a. Every script instruction carries a LINE NUMBER — no exceptions

Any time the developer must click, edit, delete, paste at, or inspect a step in a script, cite the Script Workspace line number: "double-click line 26 (`Import Records`)", never just "open the Import Records step". Applies to one-off asks in chat, not just delivery docs. DDR step numbering = workspace numbering (comments count); flag which export the numbers come from. Multiple edits in one script: list highest line first so earlier edits don't shift later anchors. (Repeated violation — called out four times on 2026-08-07. Don't repeat.)

## 0b. Assume FileMaker 21+ — client AND server, always

Every solution here runs FileMaker Pro 21 or newer against FileMaker Server 21 or newer. NEVER give instructions, workarounds, or "if you're on an older version…" alternatives for 20 or below, and never ask which version is in use. Use modern steps/functions freely. If a feature requires a version *above* 21, name that version — don't hedge downward.

## 1. First: confirm a recent schema at the project root

Check the project root for a schema snapshot (DDR export / schema dump). None → ask for one before building anything. More than 4 weeks old → flag as possibly stale and ask whether to proceed. Why: without it you're guessing at names and produce snippets referencing objects that don't exist.

## 1b. Project-specific notes live at project ROOT, not in Schema

Each project keeps a `Spec_notes.md` at its project root — confirmed, hard-won facts about *that* solution (color palettes, subject/label mappings, naming quirks, gotchas). Read it at the start of any FileMaker session for that project; append to it when you confirm a new project fact worth persisting.

NEVER put it (or any durable note) inside the `Schema/` folder — `Schema/` is re-exported and replaced wholesale, wiping anything in it. Root is stable; `Schema/` is disposable. (Learned the hard way: a note had wrongly been placed in `Schema/`.)

## 1c. Save deliverable files in a per-feature subfolder at project ROOT — never scratchpad/tmp

Every script XML, calc `.txt`, audit `.md`, or HTML mockup you hand over is a keeper committed to git — save it into a **feature subfolder at the project root**, not the session scratchpad or `/tmp`. (Learned the hard way: a DataPull snippet was wrongly left in scratchpad.)

- Pattern (from `🅿️PowerSchool_Import/`): one folder per feature, emoji-prefixed to match the solution's naming, holding the script `.xml` files + related audits/calcs/mockups.
- Name the `.xml` with the script's EXACT FileMaker name (rule 0), e.g. `DataPull 🟥🟨🟩_CurrentWeekAdditions.xml`. Reuse an existing feature folder if one fits; only create a new one when none does.
- Still fine to draft in scratchpad, but the final artifact lands in the project folder before you report it done.

## 2. Deliverables are paste-ready — never pseudo-syntax

Exactly two forms:

1. Script step(s) → clipboard XML with the full envelope (rule 3).
2. Standalone calculation → raw calc text.

Never bracketed pseudo-syntax like `Set Field [ Table::field ; <calc> ]` — it pastes nowhere. This includes proposed, illustrative, and diagnostic steps, not just final answers. If a step references an object that doesn't exist yet, describe it in prose instead. Before sending any FileMaker reply, scan it: `[ ` step brackets outside a code block → convert to XML or prose. (Real violation. Don't repeat.)

## 2b. Long code: deliver the WHOLE artifact

Anything over ~20 lines: hand back the complete updated calc/script in one paste, never "replace this block" fragments — a mis-spliced manual edit breaks the calc; re-pasting the whole thing is free. Explaining what changed in prose alongside is fine. Under ~20 lines, standalone fragments are fine.

## 2c. Editing ONE existing step's calculation → bare calc text only

Changing the calc inside a step that already exists is NOT "delivering a step."
Give exactly what gets pasted into that calculation box: no XML, no wrapper.

- ❌ Clipboard XML for the whole step — forces a step-delete-and-paste for a one-field edit.
- ❌ `If ( DayOfWeek ( Get(CurrentDate) ) = 2 )` for an `If` step's condition — the `If ( )` is the STEP, not the calc. The box holds only the boolean.
- ✅ `DayOfWeek ( Get(CurrentDate) ) = 2 or DayOfWeek ( Get(CurrentDate) ) = 4`

Same for `Exit Loop If`, `Show Custom Dialog` message, portal filters, hide conditions, `Set Field` targets: hand over the expression that lives in the box, nothing around it.

Say which step (name + number) in prose, then the bare calc in its own code block.

(Repeated violation — cost round trips 2026-08-24 on `🌘📅🌐Morning8AM` step 5. Reach for XML only when a step is being ADDED, REPLACED wholesale, or REORDERED.)

## 2d. Whole-script deliveries: ship them CLEAN

When handing back a complete script (rule 2b):

- **Drop disabled steps and the comments that describe them** — a rewrite is the moment dead code dies. Keep a disabled step only if the user says to.
- Keep/add ~10-word section dividers (rule 4b) so long scripts scan.
- A script pushing past ~150 live steps: propose splitting into subscripts in one line — don't just deliver the monolith silently.

## 2e. The copyable block holds ONLY the code

Whatever is being copied — calc text, XML, SQL — the code block or delivered file contains nothing but the paste itself. No header notes, no "replaces the calc of…", no deploy caveats inside the block. All explanation lives in chat prose around it. (Real violation 2026-08-27: calc .txt files shipped with 3-line preambles the user had to strip before pasting.)

## 3. Clipboard XML envelope — required every time

```
<?xml version="1.0" encoding="UTF-8"?>
<fmxmlsnippet type="FMObjectList">
  …<Step>…</Step>…
</fmxmlsnippet>
```

A bare `<Step>` without the envelope silently fails to paste — even for a single step. Multiple inserts for different locations → each gets its own complete envelope. This is the most common screwup; verify before sending.

## 4. Blank `# (comment)` STEP above every section heading

FileMaker IGNORES blank lines in pasted XML — a literal empty line renders NO gap in the script editor. The only thing that creates visual separation is an actual **empty `# (comment)` step** (id 89, no `<Text>`). Put one above every section-heading comment step (except the very first). Applies to the whole artifact; scan the finished snippet and confirm before sending. (Repeated violation: shipped scripts with only XML blank lines / sections run together and had to be fixed by hand. A blank XML line ≠ a blank comment step.)

```
  </Step>

  <Step enable="True" id="89" name="# (comment)">
    <DisableStepCollapsed state="False"/>
    <Restore state="False"/>
  </Step>
  <Step enable="True" id="89" name="# (comment)">
    <Text>=== SECTION 2 ===</Text>
  </Step>
```

(Keep the blank XML line too for source readability, but the empty comment STEP is what renders in the editor.)

## 4b. Comment steps: section dividers YES, essays NO — 10 words each

Section-divider comments between groups of steps are wanted — they make a long script scannable. What is NOT wanted is a long block inside any one of them.

- **Cap every `# (comment)` step at ~10 words.** No rationale paragraphs, no "why this idiom", no restating values the Set Fields below already show, no install prerequisites, no cross-references to other scripts.
- **Throwaway / run-once scripts get exactly ONE comment**: what it is and what replaces it. Nothing else.
- Explanation belongs in the deliverable's README, or in runtime text (`$$Result`, an abort message) — never in the step list.

❌ `<Text>Anchors on LearnersImported_Utility and walks every student, creating the related record where none exists — the house idiom (same as …). Sets only the REQUIRED fields to district defaults: 120 total · ELA 20 · …</Text>`
✅ `<Text>=== SEED TARGETS ===</Text>`
✅ `<Text>Temporary — student import will seed these going forward.</Text>`

(Real violation 2026-08-13: a run-once seeder shipped with five paragraph-length preambles. "I'm never going to read them.")

## 4c. Calc comments: 10-word cap, never explain code

Applies to EVERY deliverable calculation — web viewer address calcs included. No header blocks, no "LIVES IN" banners, no rule restatements, no explaining what the next line does. At most one ≤10-word line for a fact the code cannot show. (Real violation 2026-08-28: an address calc shipped with a ~15-line comment stack; the user deletes these by hand every time.)

## 4d. No table-wide SQL in layout-object calcs

A web viewer address / conditional / hide calc re-evaluates constantly, client-side. Any ExecuteSQL in one must hit an indexed column with a selective WHERE (per-student, per-course). NEVER a GROUP BY, aggregate, or unfiltered scan over a large table (ClassList, MicroCredits, Transcript) — it downloads the whole table over WAN and beachballs or hangs the client (confirmed 2026-08-28: enrollment GROUP BY over ClassList in an address calc froze FileMaker, force-quit required). Read nightly-cached fields instead; that is what they exist for.

## 5. Reuse real serialization — don't guess

Copy exact step serialization from XML that is already known-good (previously pasted): step `id`, `<Calculation>`/`<Field>`/`<Layout>`/`<Script>` forms, real internal ids. Flag any uncertain step instead of guessing silently.

| Step           | id  | Step                     | id  |
| -------------- | --- | ------------------------ | --- |
| Set Field      | 76  | Perform Script on Server | 164 |
| Set Variable   | 141 | Go to Layout             | 6   |
| If             | 68  | Show Custom Dialog       | 87  |
| Else           | 69  | Exit Script              | 103 |
| Else If        | 125 | Commit Records/Requests  | 75  |
| End If         | 70  | Import Records           | 35  |
| Perform Script | 1   | # (comment)              | 89  |
| Loop           | 71  | Exit Loop If             | 72  |
| End Loop       | 73  |                          |     |

(Verified against a real DDR export. `Else If` is 125, not 69 — 69 is plain `Else`.)

`Go to Record/Request/Page` is id **16**. Clipboard serialization (verified working — pasted & ran):
```
<Step enable="True" id="16" name="Go to Record/Request/Page"><NoInteract state="False"/><RowPageLocation value="First"/></Step>
<Step enable="True" id="16" name="Go to Record/Request/Page"><NoInteract state="False"/><RowPageLocation value="Next"/><Exit state="True"/></Step>
```
`value` = First | Next | Previous | Last; `<Exit state="True"/>` = "exit after last".

## 6. Output via a `$$global`, never a dialog

Probe/debug/diagnostic scripts: add `Set Variable [ $$Result ]` immediately before `Exit Script`, using the same expression Exit Script returns, so it can be grabbed in the Data Viewer. Dialog text can't be selected/copied — a dialog is optional extra, never the sole output. Scripts that might run on server: return via Exit Script result AND `$$Result` AND a dialog.

```xml
<Step enable="True" id="141" name="Set Variable">
  <Value><Calculation><![CDATA[$msg]]></Calculation></Value>
  <Repetition><Calculation><![CDATA[1]]></Calculation></Repetition>
  <Name>$$Result</Name>
</Step>
```

## 7. Web viewer: render HTML via a `data:` URL

Web Address calc: `"data:text/html;charset=utf-8," & <html>`.

- Pass raw HTML — don't percent-encode. FileMaker encodes the address once; double-encoding leaks literal `%0A`/`%09` into the page. Inject data via `Substitute` and stop.
- Don't use `Base64Encode`/`Base64EncodeRFC` on text for a `;base64,` URL — they return empty for text → blank viewer.
- The address calc evaluates in the layout's context; a field with no reachable related record returns empty and the calc collapses to the 29-char prefix → blank. Read utility-table fields with `ExecuteSQL`. Diagnose with `"LEN: " & Length ( <calc> )` as the address: 29 = empty refs.

## 7b. NEVER put a square bracket inside a calculation comment

`[` or `]` anywhere in a `/* */` block or a `//` line makes FileMaker throw **"List usage not allowed."** The parser counts bracket characters before it strips comments. Applies to EVERY calc, not just web viewers — and it is invisible, because the code is fine and the dialog points nowhere useful.

The trap is documenting a token: a web-viewer template placeholder written the doubled-bracket way, or explaining `Substitute`'s or `JSONSetElement`'s `[ old ; new ]` pair form. Scan every comment for `[` before delivering a calc.

```
❌ BAD:   /* substitutes the [[CATALOG]] and [[DATA]] tokens */
❌ BAD:   /* not the [ key ; value ; type ] multi-parameter form */
✅ GOOD:  /* substitutes the CATALOG and DATA tokens */
✅ GOOD:  /* not the multi-parameter pair form */
```

Brackets in *live code* are fine — `Let ( [ … ] ; … )`, `Substitute ( x ; [ a ; b ] )`, and tokens inside string literals all parse. Prefer nested 3-parameter `Substitute` over the bracket-pair form anyway; it removes the last ambiguity for free. (Real violation, 2026-08-04, cost several round trips — Jason spotted it, not me.)

## 7c. Web viewers that WRITE back (`FileMaker.PerformScript`) — two crash traps

Confirmed on FM Pro 26.0.1 (beachball, 2026-08-04):

- **The called script must start with `Freeze Window` (id 79)** whenever it writes fields the viewer's address calc depends on. Without it, EVERY Set Field re-evaluates the address and reloads WebKit — a 10-rep write = ~11 reloads per save; navigating records mid-storm hangs the client.
- **Never put an ExecuteSQL JOIN in a layout-object calc.** Client-side JOINs pull every affected record to the client and go quadratic — the calc re-runs on each record switch and beachballs on data-heavy records (confirmed: Transcript⋈TranscriptAdditional in a web viewer address, FM 26.0.1). Use flat single-table indexed queries and join the rows in the page's JS. Also avoid `beforeunload` listeners in web viewer pages — they can block embedded-WebKit teardown; use `pagehide`.
- **Never fire `PerformScript` from a `blur` handler as the only save path.** Switching records blurs the field and the call lands while FileMaker is tearing the viewer down (WebKit calls into the script engine while FM waits on WebKit → deadlock). Pattern: debounced autosave on `input` (~1s) so blur is normally clean, plus an `UNLOADING` flag set on `pagehide`/`beforeunload` that vetoes every `PerformScript`; a blur-time save defers one tick (`setTimeout 0`) so the flag can catch it.

## 8. Never add `Commit Records/Requests` to "fix" a save

FileMaker auto-saves field writes, including in server-side scripts — a commit is never the fix for "the field came up blank." Diagnose instead: stale layout display (write actually succeeded), record lock, `GetFieldName()` returning empty, wrong/duplicate field reference, `Set Error Capture` hiding the error, wrong record or related table. (Commits were once wrongly added to import scripts, then reverted. Don't repeat.)

## 9. ExecuteSQL: identifiers PLAIN — no escaped `\"` quotes

```
❌ BAD:   SUM ( \"MicroCredits\".\"CreditsMastery\" )
✅ GOOD:  SUM ( MicroCredits.CreditsMastery )
```

Same in `FROM`/`WHERE`. String literals keep single quotes (`WHERE Type <> 'Plato'` is fine — the rule is identifiers, not values). If a name isn't SQL-safe unquoted (reserved word like `Type`, `Date`, `Time`, `Timestamp`, `Value`, `Status`, `Row`, `Group`, `Order`, `User`; spaces/special chars; leading non-letter): don't paper over with `\"` quotes — stop, name it, and have the field renamed, then write it plain.

## 9b. SQL dates ≠ FileMaker dates — convert BOTH directions

ExecuteSQL returns dates as `YYYY-MM-DD` text, not a FileMaker date. Never feed a raw SQL result into a date field, `Date` calc, or date math — wrap it. Two custom functions exist; use them, don't hand-roll parsing.

- SQL → FileMaker: `SQL_DateTime_to_Date ( <sql result> )`
- FileMaker → SQL: `Date_FM_to_SQL ( <date> )` — returns `YYYY-MM-DD`

✅ `SQL_DateTime_to_Date ( ExecuteSQL ( "SELECT StartOfYear FROM Settings" ; "" ; "" ) )`

Bound `?` parameters coerce a FileMaker date fine. A date concatenated into the query string does not — run it through `Date_FM_to_SQL` first.

## 9c. SQL `FROM` takes the TABLE OCCURRENCE name, not the base table

The TO name from the relationship graph often differs from the base table in the DDR export — base `a_Settings` is queried as `FROM Settings`. Rule 0's base-table rule governs telling the user where to FIND a field; SQL is the exception. `SQLGetTableName ( field )` returns the correct TO name when unsure. (Real violation 2026-08-27: shipped `FROM a_Settings`; failed.)

## 10. Finds: stored requests CAN hold variables; build finds step-by-step

Fact: a stored request in `Perform Find [Restore]` CAN contain a variable (e.g. `$Cycle`) — it evaluates at runtime. Never reason from "a stored find can't use a variable."

Preference: never deliver a find as a single stored-request `Perform Find [Restore]`. Spell it out: `Enter Find Mode` (no pause, no stored criteria) → one `Set Field` per criterion, `New Record/Request` for additional requests, `Omit Record` for omits → `Perform Find` with no stored requests. Ids for these find steps aren't in the verified table yet — per rule 5, copy from real pasted XML or flag.

## 11. Clipboard XML in/out of Script Workspace — type codes required

FileMaker never reads plain text from the clipboard for schema objects; the entry must carry a 4-char type code: `XMSS` script steps, `XMSC` whole script, `XMTB` table, `XMFD` field, `XMFN` custom function, `XML2` layout objects. Plugins don't hook Cmd-V — write the tagged clipboard explicitly.

- Paste IN: evaluate `BE_ClipboardSetText ( $xml ; "XMSS" )` in the Data Viewer, then Cmd-V into the step list.
- Copy OUT: copy steps in Script Workspace, then `BE_ClipboardGetText ( "XMSS" )`. Empty → evaluate `BE_ClipboardFormats` and use the exact string it reports.
- The Data Viewer truncates long results — a big script looks cut off even when the copy worked. Write to disk with `BE_FileWriteText` before judging.
- Long XML in a calc: park it in a global field rather than inline-escaping every `\"`.

## 12. Plugins on FileMaker Server (macOS) — install AND enable

Install (server stopped) — copy the `.fmplugin` into all three, then per copy `xattr -dr com.apple.quarantine` and `chown -R fmserver:fmsadmin`, then start:

```
/Library/FileMaker Server/Database Server/Extensions
/Library/FileMaker Server/Web Publishing/publishing-engine/cwpc/Plugins
/Library/FileMaker Server/Web Publishing/publishing-engine/wip/Plugins
```

Enable at Admin Console → **Connectors → Plug-ins**: "FileMaker Script Engine Plug-ins" (schedules/PSoS) and "Web Publishing Plug-ins" (WebDirect/Data API). NEVER send anyone to Configuration → Script Settings — that's pre-21 and it isn't there. (Real violation. Don't repeat.) The Connectors → Plug-ins tab lists detected plug-ins — fastest confirmation the server sees the file.

Pasted shell blocks for the server: omit the `#!/bin/bash` shebang — zsh history expansion errors on `!` (`event not found`). Quoted paths need no backslash escaping.

## 13. Server-side plugin diagnostics — in order, via PSoS

Diagnose with a script run through Perform Script on Server, never a local run.

- `Get ( ApplicationVersion )` on FMS returns e.g. `Server 21.0.1` — `= "Server"` is ALWAYS false. Use `PatternCount ( Get ( ApplicationVersion ) ; "Server" )`. (Real violation. Don't repeat.)
- `Get ( InstalledFMPlugins )` is the definitive presence check — it works even when the plugin failed to load. Guard every `MBS()`/`BE_` call behind it so a missing plugin doesn't turn the whole result into `?`.
- Ladder when a function returns `?`: (1) ran on server? (2) `Get ( InstalledFMPlugins )` lists it? (3) enabled at Connectors → Plug-ins? (4) `lipo -archs` shows `arm64` on Apple Silicon? (5) quarantine flag stripped? (6) `StdErrServerScripting.log` / `StdErrDataAPI.log` / `StdErrWeb.log` exist in Logs? Absent = server never attempted the load. Only after all six is it licensing.

## 14. MBS licensing — once, persisted

`MBS ( "StoreRegistration" ; Name ; Component ; Type ; ExpireMonth ; Serial )` writes the license into server prefs permanently; pair with `MBS ( "Register" ; … )` so the current session licenses immediately; `MBS ( "IsRegistered" )` = 1 confirms. All five values verbatim from the purchase email — component, type string, and `YYYYMM` expiry included — or it fails silently. Run once via PSoS from a throwaway hosted file, then remove the file. Never paste a live serial into chat/tickets without flagging it for rotation.
