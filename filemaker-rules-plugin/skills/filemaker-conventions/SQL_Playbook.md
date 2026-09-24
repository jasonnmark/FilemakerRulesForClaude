Every `ExecuteSQL` in every FileMaker solution hits ONE indexed predicate on a plain-named table occurrence, guards its result for `?`, and never runs from a layout object — this playbook is the whole house SQL rulebook.

# ExecuteSQL Playbook

Cross-client. Replaces the SQL parts of skill rules 4d, 7c, 9, 9b, 9c, 15 and HTML playbook §4; a project appears only as a dated one-line example.

## 1. Syntax

| Element | Rule |
|---|---|
| Identifiers | Plain. Never `\"`-quoted — a name that needs quoting gets renamed. |
| String literals | Single quotes: `WHERE Status_Code = 'Active'`. |
| Parameters | `?` bound arguments after the two separators: `ExecuteSQL ( sql ; "" ; "" ; $a ; $b )`. |
| `FROM` | The TABLE OCCURRENCE name, not the base table. `SQLGetTableName ( Table::Field )` returns it. |
| Emoji / spaces in a TO name | Fail with `?`. Keep ONE plain-named TO per table for SQL. (2026-07-31: adding a plain `SpeedTests` TO beside `⏱️SpeedTests` was the entire fix.) |
| Reserved column | Alias the table and qualify: `FROM MicroCredits M WHERE M.Type = 'Future'`. |
| Dates in the string | A FileMaker date binds fine through `?`. Concatenated into the string it must be `YYYY-MM-DD` — `Date_FM_to_SQL ( date )`. |

```
❌ SUM ( \"MicroCredits\".\"CreditsMastery\" )      ❌ FROM ⭐️MicroCredits
✅ SUM ( MicroCredits.CreditsMastery )              ✅ FROM MicroCredits
❌ WHERE Type = 'Plato'                              ❌ "… WHERE StartDate >= '" & $d & "'"
✅ FROM MicroCredits M WHERE M.Type = 'Plato'        ✅ "… WHERE StartDate >= ?" ; "" ; "" ; $d
```

Reserved words (Claris list: <https://help.claris.com/en/sql-reference/content/reserved-words.html>): `Type`, `Date`, `Time`, `Timestamp`, `Value`, `Status`, `Row`, `Group`, `Order`, `User`, `Work`, `Level` are reserved. `Resume`, `Age`, `Notes` are not. Check the list before naming a field; alias when the column already exists.

Supported and used in the house: `LOWER()`, `LIKE '%x%'`, `IN`, `GROUP BY`, `COUNT(*)`, `MIN`/`MAX`, `ORDER BY`, `FETCH FIRST n ROWS ONLY`, `ROWID` (record id — documented for SELECT/WHERE; `ORDER BY ROWID` works in practice), `LEFT OUTER JOIN` (works, client-side, slow — §3).

## 2. Results

Everything comes back as text.

| Fact | Handle it |
|---|---|
| Dates arrive `YYYY-MM-DD`, timestamps `YYYY-MM-DD HH:MM:SS`; `GetAsDate`/`GetAsTimestamp` return `?` on a US-locale file | Wrap every date column: `SQL_DateTime_to_Date ( x )` or `Date_SQLToFilemaker ( x )` — both spellings exist across solutions; use whichever the target file defines (`Schema/06_CUSTOM_FUNCS.md`). |
| Error = the single character `?` | Guard every result: `Left ( $r ; 1 ) = "?"` → `$$Result` gets the first 40 chars of the query, Exit. |
| Empty string = zero rows | Not an error; do not `?`-guard for it. |
| `MIN`/`MAX`/`SUM` over zero rows = NULL | Arrives blank; wrap with `If ( IsEmpty ( x ) ; 0 ; x )` before math. |
| Default separators are `,` and `¶` | Never keep them for multi-column data. Use `Char ( 31 )` field / `Char ( 30 )` row so embedded returns survive. |
| Embedded returns inside a value | `Substitute ( $r ; ¶ ; Char ( 29 ) )` BEFORE splitting rows; restore after. (2026-09-04: one CR inside a title shifted every column after it.) |
| `List ()` drops blank values | Diagnostics use `" "` spacers so positions hold. |
| A `¶` carried through JSON arrives as CR (`\r`) | `ValueCount`/`FilterValues` split on CR only — an LF-joined list counts as ONE value. Normalise: `Substitute ( x ; Char ( 13 ) & Char ( 10 ) ; ¶ )` then `( Char ( 10 ) ; ¶ )`. |
| Tabs do not survive a web viewer `data:` URL | Pipes or the control characters above. |

```
✅ Set Variable [ $r ; ExecuteSQL ( "SELECT A, B FROM T WHERE Flag_Active = ?" ; Char ( 31 ) ; Char ( 30 ) ; 1 ) ]
   If [ Left ( $r ; 1 ) = "?" ]
     Set Variable [ $$Result ; "ERROR | " & Get ( ScriptName ) & " | " & Left ( "SELECT A, B FROM T …" ; 40 ) ]
     Exit Script
   End If
```

## 3. Performance

Measured 2026-09-24, 147 rows, hosted file over WAN — the source for every number below:

| Pattern | Cost |
|---|---|
| `WHERE key IN ( 147 literals )` | 3.4–4.0 s per query, ~24 ms per literal — each literal is its own server find |
| Found-set walk with `Go to Record`, reading related fields | ~3.5 s |
| ONE indexed predicate (`WHERE flag = ? AND date >= ?`) | 20–60 ms |
| Whole-table `SELECT`, tiny table | ~1 ms |
| Whole-table `SELECT`, a few hundred rows | ~500 ms |
| A single indexed flag over a large ledger table | ~800 ms |
| Reading a "List of" summary over the found set | 1–2 ms |
| Whole screen load, before → after removing every `IN` list and the walk | 11.0 s → 1.4 s |

Rules that follow:

- Never `IN ( … )` with a key list. Never walk a found set to build a payload.
- Found set → ONE stored packed-row calc on the base table (columns joined by `Char ( 31 )`, text columns stripped of `Char ( 31 )`, `Char ( 30 )`, `¶`; local stored fields only, never blank) + ONE "List of" summary. Read the summary once; found-set order = record numbers.
- Small related tables: `SELECT` whole, join by key in the page. Big tables: bound by ONE indexed field, never by the found set.
- A calc in a `WHERE` must be stored AND indexed — "Do not store calculation results" OFF and Indexing All. Two different switches; the first alone still scans.
- Never a JOIN, `GROUP BY`, aggregate, or unfiltered scan in a layout-object calc (web viewer address, conditional format, hide). Re-evaluates on every record switch, pulls the table over WAN, goes quadratic. (2026-08-28: an enrollment `GROUP BY` in an address calc froze the client, force-quit.) Read nightly-cached fields instead.
- `LEFT OUTER JOIN` runs client-side: two flat indexed single-table queries joined in the page beat it every time.
- Per-record queries with `?` are fine inside a script; N of them in a loop = N round trips — pull the set once and split locally.
- `LOWER ( col ) LIKE '%x%'` cannot use the index. Bound it first with an indexed predicate: `WHERE Flag_Active = ? AND LOWER ( Title ) LIKE ?`.
- Instrument, never guess: `Get ( CurrentTimeUTCMilliseconds )` mark before and after each query, deltas appended to `$$Result`.

## 4. Diagnostics

- Data Viewer diagnostics are ONE `List ( "label: " & expr ; " " ; … )` calc, copied back whole (rule 6b).
- "Did the TO rename happen?": `ExecuteSQL ( "SELECT COUNT(*) FROM <TO>" ; "" ; "" )` → `?` means the TO name is wrong; a number means the name resolves.
- A query returning `?` in a script: run it in the Data Viewer with literals instead of `?` to separate a binding problem from a syntax one.
- Ladder for `?`: TO name plain and spelled exactly → reserved column aliased → identifiers unquoted → string literals single-quoted → date in string via `Date_FM_to_SQL` → field exists on that TO's base table.

## 5. Where SQL is the wrong tool

| Need | Use instead |
|---|---|
| The current record's own fields | The field reference. SQL has no record context and re-fetches. |
| Anything evaluated on a layout object | A nightly-cached field, or a global the load script fills. |
| Writes | None — `ExecuteSQL` is read-only in FileMaker. Writes go through `Set Field` in a work window (HTML playbook §3). |
| Related rows already reachable through the graph | A portal, a "List of" summary, or the relationship. |
| Counting a found set | `Get ( FoundCount )`. |

## Before you ship an ExecuteSQL

1. `FROM` names a plain TO (`SQLGetTableName`), no emoji, no space.
2. No `\"` around any identifier; every string literal single-quoted; no curly quotes (rule 9a).
3. Every reserved column (`Type`, `Date`, `Status`, …) reached through a table alias.
4. Dates: `?`-bound, or `Date_FM_to_SQL` in the string; every date result wrapped in the file's SQL-date function.
5. Separators `Char ( 31 )` / `Char ( 30 )` for multi-column output; `¶` → `Char ( 29 )` before splitting.
6. `Left ( $r ; 1 ) = "?"` guard after every query, first 40 chars into `$$Result`; blank treated as zero rows.
7. No `IN ( … )` key list; no found-set walk; no loop of per-record queries.
8. Every `WHERE` column indexed; a calc there is stored AND indexed; `LIKE` bounded by an indexed predicate.
9. Not in a layout-object calc; no JOIN / `GROUP BY` / aggregate outside a script.
10. Timed with `Get ( CurrentTimeUTCMilliseconds )` marks in `$$Result`, and the number reported.
