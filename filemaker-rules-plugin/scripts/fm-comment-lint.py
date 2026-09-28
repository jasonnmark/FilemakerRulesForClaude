#!/usr/bin/env python3
"""PostToolUse hook: flag wordy comment steps in the clipboard XML just written.

Rule 4b of filemaker-conventions. Exit 2 + stderr feeds violations back to Claude.
"""
import json, os, re, stat, sys, time
import xml.etree.ElementTree as ET

MAX_WORDS = 10
MAX_DIVIDER_WORDS = 4
MAX_BYTES = 2_000_000
MAX_LINES = 15
FRESH = 120  # seconds; Bash writes are matched by path in the command
CLAUSE = re.compile(r"\s[—–]\s|;|,|→|\(|\bvia\b", re.I)
EXEMPT = re.compile(r"^\s*(sample\b|params?\b|param json\b|script param|\{|JSONSetElement\s*\()", re.I)
XML_PATH = re.compile(r"""(?:"([^"]+\.xml)"|'([^']+\.xml)'|(\S+\.xml))""", re.I)


def targets(payload):
    tin = payload.get("tool_input") or {}
    if not isinstance(tin, dict):
        return []
    if payload.get("tool_name") == "Bash":
        cmd = tin.get("command") or ""
        cwd = payload.get("cwd") or os.getcwd()
        out = []
        for m in XML_PATH.finditer(cmd):
            p = next(g for g in m.groups() if g)
            p = os.path.expanduser(p)
            if not os.path.isabs(p):
                p = os.path.join(cwd, p)
            out.append(p)
        return [p for p in dict.fromkeys(out) if fresh(p)]
    p = tin.get("file_path") or ""
    return [p] if p.lower().endswith(".xml") else []


def fresh(p):
    try:
        return time.time() - os.stat(p).st_mtime < FRESH
    except OSError:
        return False


def steps_by_script(root):
    """Yield (step, line) with line numbers restarting inside each Script."""
    def walk(node, counter):
        for child in node:
            if child.tag == "Script":
                yield from walk(child, [0])
            elif child.tag == "Step":
                counter[0] += 1
                yield child, counter[0]
            else:
                yield from walk(child, counter)
    yield from walk(root, [0])


def lint(path):
    try:
        st = os.stat(path)
        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_BYTES:
            return []
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return []
    if "<fmxmlsnippet" not in text:
        return []
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError as e:
        return [f"- {os.path.basename(path)}: XML does not parse ({e})"]
    found = []
    for step, line in steps_by_script(root):
        if step.get("name") != "# (comment)":
            continue
        t = step.find("Text")
        if t is None or not (t.text or "").strip():
            continue
        body = " ".join((t.text or "").split())
        if EXEMPT.match(body):
            continue
        is_div = body.startswith("===")
        label = body.strip("= ")
        words = label.split()
        why = []
        if is_div and len(words) > MAX_DIVIDER_WORDS:
            why.append(f"divider {len(words)} words, max {MAX_DIVIDER_WORDS}")
        if not is_div and len(words) > MAX_WORDS:
            why.append(f"{len(words)} words, max {MAX_WORDS}")
        if CLAUSE.search(label):
            why.append("second clause")
        if why:
            found.append(f"- {os.path.basename(path)} line {line}: \"{body[:80]}\" ({'; '.join(why)})")
    return found


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    found = []
    for p in targets(payload):
        found += lint(p)
    if not found:
        return 0
    extra = len(found) - MAX_LINES
    shown = found[:MAX_LINES] + ([f"- …and {extra} more"] if extra > 0 else [])
    sys.stderr.write(
        "[fm-comment-lint] Rule 4b: comment steps are labels, not descriptions.\n"
        "Dividers: 1-4 word noun label, nothing after it. Other comments: only what the steps "
        "cannot show, 10 words, one clause. Jason's own original comments: keep verbatim.\n"
        + "\n".join(shown) + "\n"
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
