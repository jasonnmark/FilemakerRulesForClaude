Every web-viewer screen in every FileMaker solution loads through ONE summary read and writes through ONE guarded script — this playbook is the house pattern that makes that true.
Approved 2026-09-24. Read this before building or changing any HTML/JavaScript web-viewer screen. SQL specifics live in SQL_Playbook.md.

# HTML / Web Viewer Playbook

House rules for HTML/JS screens inside FileMaker web viewers, for every client solution. Rule numbers (4b, 4d, 6, 7, 7b, 7c, 8, 9, 9a, 9b, 9c, 10, 11, 15, 16) refer to the `filemaker-conventions` skill; this doc adds what they lack. Rule 16 sets its scope; rule 15 holds the measured feed costs §4 applies.

## 1. Architecture (the house pattern)

| Piece | Where | Rule |
|---|---|---|
| Page | `Settings::<Feature>_HTML` text field | Invariant. One paste. Starts with a `TEMPLATE_VERSION: vX.Y date` line; shows the version tag on screen. |
| Address calc | Web viewer object named `<Feature>WV` | `"data:text/html;charset=utf-8," & Substitute ( html ; "[[BOOT]]" ; bootJSON )`. BOOT = whoAmI, today, sort — nothing from the current record (rule 7). |
| Data in | `<Feature>_GetData` script | `Perform JavaScript in Web Viewer` → `receiveData(json)`. The page never reloads. |
| Data out | `<Feature>_Write` / `<Feature>_WriteList` scripts | Page calls `FileMaker.PerformScript` deferred one tick (`setTimeout 0`), retries every ~100 ms until the `FileMaker` object exists. Answer via `receiveReport(json)`. |
| Page state | `window.name` (namespaced JSON) | Survives the reloads FileMaker forces (record commit, layout switch). Restore in try/catch; garbage → defaults. |

- ❌ Address calc reads a field on the layout's record → reloads on every record switch and every Set Field (rule 7c). (Gradpath, 2026-08-04: beachball on every click.)
- ✅ Address calc reads only `ExecuteSQL ( "SELECT <Feature>_HTML FROM Settings" )` + globals.
- `pagehide` (never `beforeunload`) sets `UNLOADING`, which vetoes every PerformScript (rule 7c).
- One GetData request in flight; never re-fire on a timer — stacked PerformScript calls deadlock FileMaker. Retry from a button only, after 60 s. (2026-09-15: force-quit.)

## 2. Data contract (FM → page)

- GetData stamps `pv` (protocol version). Page holds `EXPECTED_PV` + `EXPECTED_COLS`; mismatch → red `pvBanner` naming the files to re-paste, no rows rendered. (2026-09-04: a partial paste misaligned columns silently.)
- Rows: `Char(30)` between rows, `Char(31)` between columns. Embedded returns → `Char(29)` before splitting. (2026-09-04: a CR inside one title shifted every column after it.)
- A `¶` inside a JSON string arrives in JS as `\r`. `ValueCount`/`FilterValues` split on CR only — an LF-joined list counts as ONE value. Normalise incoming lists: `Substitute ( x ; Char(13)&Char(10) ; ¶ )` then `( Char(10) ; ¶ )`.
- Pipes, not tabs, for hand-packed lists — tabs don't survive the `data:` URL.
- SQL dates arrive `YYYY-MM-DD` (rule 9b); reserved column names such as `Type` need a table alias `FROM <TableOccurrence> T … T.Type` (rule 9); emoji TO names return `?` (rule 9c).
- Value lists arrive as JSON arrays; page keeps a fallback and toasts red when none arrive (§6).

## 3. Writes (page → FM) and verification

Write script skeleton, in order:

1. `Freeze Window` + `Set Error Capture` (rule 7c).
2. Parse param; guard every field (`$$Result` error + Exit on a bad one).
3. `New Window` at 5000/5000 on a blank `<UtilityLayout>` of the target table. Name it `"<Feature>_Work " & Get(UUID)`; verify `Get(LayoutTableName)` before touching anything. (2026-09-04: a leftover work window with a reused name fooled the guard.)
4. Find by `<KeyField>`, step-by-step (rule 10). Found ≠ 1 → refuse with a forensic probe (`pk exists under another <KeyField>` vs `pk not in table`).
5. `Set Field By Name`; commit; re-read.
6. Report `{op, key, field, value, ok, error}` via `receiveReport`; refusal → also a blocking FileMaker dialog. `Close Window` before the report.

Page side:

| Rule | Why |
|---|---|
| Mark the row `.busy`; unlock after 12 s with a red "nothing is confirmed saved" toast | A silent hang looked like success |
| ONE write at a time (queue); a late report must not release the next write | Rapid clicks stacked PerformScript (2026-09-15) |
| Navigation / refresh / row clicks wait while saving | Record switch mid-write hung the client |
| Toasts show verified re-read values, never intent | "Saved" lied when the write was refused |
| Red toasts are sticky; refusals never auto-refresh | Auto-refresh re-blanked the list (2026-09-04) |

- ❌ `blur` as the only save path (rule 7c). ✅ Debounced `input` + deferred blur. Never add `Commit Records` to "fix" a blank field (rule 8).

## 4. Performance

Every ExecuteSQL rule and the full measured table live in `SQL_Playbook.md` — read it before writing a query. The web-viewer-specific points:

Rule 15 holds the measured feed costs. The table below is one screen's rebuild, before → after, every `IN` list and the found-set walk replaced. (Future View, 2026-09-24: 147 rows, WAN: 11,020 ms → 1,410 ms.)

| Operation | Before | After |
|---|---|---|
| Found-set rows | Walk with `Go to Record`, reading related fields: ~3.5 s | ONE "List of" summary read over the found set: 1–2 ms |
| Per-key lookups | `ExecuteSQL … WHERE key IN ( 147 literals )`: 3.4–4.0 s per query (~24 ms per literal — each value is its own server find) | `ExecuteSQL` with ONE indexed predicate: 20–60 ms |
| Small related tables | One `IN` query each | Whole-table `SELECT`, joined by key in the page: ~1 ms for a tiny table, ~500 ms for a few hundred rows |
| Large ledger table | Bounded by the found set (`IN`) | Bounded by ONE indexed flag: ~800 ms |
| **Whole screen load** | **11,020 ms** | **1,410 ms** |

Rules:

- Never `IN ( … )` with many literals. Never walk a found set to build a payload.
- Pack columns into ONE stored calc `<Feature>_Row_c` on the base table: columns joined by `Char(31)`, every text column `Substitute`-stripped of `Char(31)`, `Char(30)` and `¶`, local stored fields only (so it can be stored). Read ONE summary `<Feature>_Rows_List_s` (List of the row calc); found-set order = record numbers. The row calc must never be blank — List-of skips blanks and shifts record numbers.
- Small related tables: pull whole, join by key in JS. Big tables: bound by ONE indexed field, never by the found set.
- A calc used in a SQL `WHERE` must be stored AND indexed — "Do not store calculation results" OFF, Indexing All. Two different checkboxes.
- Loops flush Defer, not Always. Jump with `Go to Record [ByCalculation]` from `Get(RecordNumber)` + key verify; walk only if stale.
- No aggregates, JOINs or table-wide SQL in layout-object calcs (rules 4d, 7c); per-row counts come from cached fields. (CourseScreen v4, 2026-08: hang.)

## 5. Popups, overlays and focus

- Every popup is a card: full-screen `.ov` backdrop (`position:fixed; inset:0`), click on backdrop closes AND stops propagation. `Escape` closes (`closeAll()`).
- Active row keeps an `.active` class driven by state, so a re-render keeps the highlight.
- Floating dropdowns (autocomplete) are `position:fixed` at body level, placed from `getBoundingClientRect()`. A scrolling ancestor clips them invisibly. (2026-09-15: shipped broken twice.)
- Native `<datalist>` does not render in FileMaker's WebKit — build your own.
- `[hidden]{display:none!important}` in every template. (2026-09-11: menus rendered open without it.)
- Verify by screenshot + `document.elementFromPoint`, never by DOM presence.

## 6. Reusable script blocks (copy-paste candidates)

| Block | Shape |
|---|---|
| **ValueList → JSON** | `Let ( [ ~v = ValueListItems ( Get ( FileName ) ; "<list>" ) ; ~n = ValueCount ( ~v ) ] ; While ( [ i = 1 ; j = "[]" ] ; i ≤ ~n ; [ j = JSONSetElement ( j ; "[" & ( i - 1 ) & "]" ; GetValue ( ~v ; i ) ; JSONString ) ; i = i + 1 ] ; j ) )` — page keeps a fallback array; empty → red toast naming the list. |
| **GetData skeleton** | Freeze → busy guard (`$$<Feature>_GetData_Running` under 90 s → Exit) → pulls (summary read, whole small tables, one bounded query per big table) → `?` guard per query (push an error JSON and Exit) → JSON assemble → push → `$$Result` with stage ms. |
| **Write skeleton** | §3 steps 1–6. |
| **WriteList skeleton** | `<ChildTable>` rows: `{kind, op:add\|edit\|del, key, pk, value}` by PrimaryKey → re-read the parent's child rows → report `op:"list"` with the rows. |
| **OpenDetail** | `Go to Record [rec]` → key verify → walk fallback → dialog if not found → `Perform Script` the detail. |
| **Client stub / server worker** | `<Feature>_onServer` stub: dialog asks, then PSoS wait-for-completion. Worker is dialog-free, sets `$$Result` before EVERY Exit. |
| **Email sender** | `<EmailScript>` takes `{To, Subject, Body, SendNow}`; Body starting `<!DOCTYPE` passes through. |
| **Decimal format** | `Let ( x = Round ( v ; 2 ) ; If ( Abs ( x ) < 1 and x ≠ 0 ; "0" & x ; x ) )` — leading zero on fractions. |

## 7. Delivery and paste hygiene

- Templates ship as `<Feature>.html.txt` (the app renders `.html`); scripts as clipboard XML with the full fmxmlsnippet envelope (rule 3), pasted via `BE_ClipboardSetText ( $xml ; "XMSS" )` (rule 11).
- `grep -c '[“”]' *.xml` = 0 (rule 9a). No `[` in calc comments (rule 7b). Comments ≤ 10 words (rule 4b).
- pv bump = re-paste GetData AND template from the same delivery; README lists which files changed per rev, paste order, exact script names.
- `<Feature>_PREVIEW.html` (template + FileMaker stub + mock data) sits beside the template for browser tests; never pasted.

## 8. Debugging (for Claude)

- `$$Result` = `OK | Script | detail` or `ERROR | Script | where | why`; load scripts append per-stage ms from `Get(CurrentTimeUTCMilliseconds)` marks.
- `$$<Feature>Debug` global for page-side diagnostics.
- Data Viewer diagnostics: ONE `List ( … )` calc, never several watches (rule 6b).
- Page: `pvBanner` for contract errors, toasts for write errors, `window.__fmCalls` in PREVIEW logs every payload.
- Line numbers in deliveries = Script Workspace lines from the current DDR, cited highest first (comment steps count).
- "Did it paste": duplicate script name → wrong script runs; missing field → `<Field Missing>` or the calc arrives commented out; `Perform Script` targets paste as id 0 → re-select by name; `New Window` may silently match a `Copy` layout → read the step.
- Blank viewer → address `"LEN: " & Length ( <calc> )`; 29 = empty refs (rule 7).
- Order: browser PREVIEW with stub → FileMaker → screenshot every overlay.

## Checklist before shipping a web-viewer screen

1. `TEMPLATE_VERSION` line + on-screen tag updated.
2. Address calc depends on nothing from the current record; no SQL JOIN/aggregate.
3. `pv` / `EXPECTED_PV` / `EXPECTED_COLS` match GetData; banner text names the files.
4. Rows via `<Feature>_Row_c` + `<Feature>_Rows_List_s` summary; no `IN (…)`, no found-set walk; every `WHERE` calc stored + indexed.
5. Every write: Freeze → work window → key find → Set Field By Name → re-read → report; refusal dialog + sticky toast.
6. One write at a time; 12 s unlock; navigation waits while saving.
7. One GetData in flight; no timer re-fire.
8. Overlays: backdrop click stops propagation, Escape closes, `[hidden]` CSS, dropdowns `position:fixed` — verified by screenshot.
9. `grep -c '[“”]'` = 0; no `[` in comments; comments ≤ 10 words; `.html.txt` + XML envelope.
10. PREVIEW passes in a browser; README lists paste order + which files changed this rev.
