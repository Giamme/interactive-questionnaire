#!/usr/bin/env python3
"""Build an interactive questionnaire page from a config.

    python3 -I build.py CONFIG.json OUT.html [--preview | --standalone]

Checks the config, fills the template, and checks the page's script with
`node --check` when node is installed.

OUT.html is the page to publish as a claude.ai Artifact. --preview also writes
OUT.preview.html, wrapped in a full document, for a local look; publish
OUT.html, never the preview.

--standalone writes OUT.html as one complete HTML file to share instead, for
people who don't use claude.ai. Opened in any browser, it keeps each person's
answers in their browser and saves copies of itself with everyone's answers.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
CONFIG_SLOT = "/*CONFIG-START*/null/*CONFIG-END*/"
DATA_SLOT = "/*DATA-START*/null/*DATA-END*/"
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,39}$")
KEY_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
KINDS = {"decision", "choice", "open"}
RESERVED_KEYS = {"yes", "other", "unsure", "answer"}
CONTENT_FIELDS = {"heading", "lede", "purpose", "from", "to", "used", "context", "how"}


def builtin_ui(template: str) -> dict:
    m = re.search(r"/\*UI-START\*/(.*?)/\*UI-END\*/", template, re.S)
    if not m:
        sys.exit("template.html has no UI block")
    return json.loads(m.group(1))


def check(cfg: dict, ui: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    err = errors.append

    if not isinstance(cfg.get("title"), str) or not cfg["title"].strip():
        err("title: a short page name is required (2 to 4 words)")
    elif len(cfg["title"].split()) > 5:
        warnings.append(f"title: '{cfg['title']}' is long; the gallery shows it as the page's name")
    if not isinstance(cfg.get("id"), str) or not KEY_RE.match(cfg["id"]):
        err("id: a slug such as 'team-offsite-2026' is required (letters, digits, - and _)")
    legacy = cfg.get("legacyLocalKey")
    if legacy is not None and (not isinstance(legacy, str) or not legacy.strip() or len(legacy) > 100):
        err("legacyLocalKey: the browser storage key an older version of this page kept answers under (a string)")

    langs = cfg.get("languages")
    if not isinstance(langs, list) or not langs or not all(isinstance(l, str) and l for l in langs):
        err("languages: a list of language codes is required; the first is the default")
        langs = []
    if len(set(langs)) != len(langs):
        err("languages: a language is listed twice")

    own_ui = cfg.get("ui") or {}
    required_ui = set(ui["en"])
    for l in langs:
        have = set(ui.get(l, {})) | set(own_ui.get(l, {}))
        missing = sorted(required_ui - have)
        if missing:
            err(f"ui.{l}: the template has no '{l}' strings; add these keys under ui.{l}: {', '.join(missing)}")
    for l, strings in own_ui.items():
        unknown = sorted(set(strings) - required_ui)
        if unknown:
            warnings.append(f"ui.{l}: unknown keys {', '.join(unknown)}")

    content = cfg.get("content") or {}
    for l in langs:
        if l not in content:
            warnings.append(f"content.{l}: missing; the page falls back to {langs[0]}")
    for l, fields in content.items():
        unknown = sorted(set(fields) - CONTENT_FIELDS)
        if unknown:
            err(f"content.{l}: unknown fields {', '.join(unknown)} (allowed: {', '.join(sorted(CONTENT_FIELDS))})")

    groups = cfg.get("groups") or []
    group_keys = []
    for i, g in enumerate(groups):
        if not isinstance(g, dict) or not isinstance(g.get("key"), str) or not KEY_RE.match(g["key"]):
            err(f"groups[{i}]: needs a 'key' (letters, digits, - and _)")
            continue
        group_keys.append(g["key"])
        check_label(g.get("label"), langs, f"groups[{i}].label", err)
    if len(set(group_keys)) != len(group_keys):
        err("groups: a key is used twice")

    qs = cfg.get("questions")
    if not isinstance(qs, list) or not qs:
        err("questions: at least one question is required")
        qs = []
    seen, order = set(), []
    for i, q in enumerate(qs):
        where = f"questions[{i}]"
        if not isinstance(q, dict):
            err(f"{where}: must be an object")
            continue
        qid = q.get("id")
        if not isinstance(qid, str) or not ID_RE.match(qid):
            err(f"{where}: 'id' must start with a letter and use letters, digits, - and _ (such as Q1)")
        elif qid in seen:
            err(f"{where}: id {qid} is used twice")
        else:
            seen.add(qid)
            where = qid
        kind = q.get("kind") or ("choice" if "options" in q else "decision")
        if kind not in KINDS:
            err(f"{where}: kind must be one of {', '.join(sorted(KINDS))}")
        if groups:
            if q.get("group") not in group_keys:
                err(f"{where}: group '{q.get('group')}' is not in groups")
            else:
                order.append(q["group"])
        elif q.get("group"):
            err(f"{where}: has a group but the config has no groups list")
        for l in langs:
            w = q.get(l)
            if not isinstance(w, dict):
                err(f"{where}.{l}: needs {{title, body}}")
                continue
            if not str(w.get("title", "")).strip():
                err(f"{where}.{l}.title: required")
            if not str(w.get("body", "")).strip():
                warnings.append(f"{where}.{l}.body: empty")
            if kind == "decision" and not str(w.get("rec", "")).strip():
                err(f"{where}.{l}.rec: a decision question needs its recommended answer")
            if kind == "open" and w.get("rec"):
                warnings.append(f"{where}.{l}.rec: an open question shows its recommendation as a hint only")
        if kind == "choice":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 2:
                err(f"{where}.options: a choice question needs at least two options")
                opts = []
            keys = []
            for j, o in enumerate(opts):
                if not isinstance(o, dict) or not isinstance(o.get("key"), str) or not KEY_RE.match(o["key"]):
                    err(f"{where}.options[{j}]: needs a 'key' (letters, digits, - and _)")
                    continue
                if o["key"] in RESERVED_KEYS:
                    err(f"{where}.options[{j}]: key '{o['key']}' is reserved")
                keys.append(o["key"])
                check_label(o.get("label"), langs, f"{where}.options[{j}].label", err)
                if "short" in o:
                    check_label(o["short"], langs, f"{where}.options[{j}].short", err)
            if len(set(keys)) != len(keys):
                err(f"{where}.options: a key is used twice")
        elif "options" in q:
            err(f"{where}: only a choice question takes options")

    # Questions of one group should sit together, or the group heading repeats.
    runs = [g for k, g in enumerate(order) if k == 0 or order[k - 1] != g]
    if len(runs) != len(set(runs)):
        warnings.append("questions: a group's questions are split up; its heading will appear more than once")
    return errors, warnings


def check_label(value, langs, where, err):
    if isinstance(value, str):
        if not value.strip():
            err(f"{where}: empty")
        elif len(langs) > 1:
            err(f"{where}: give one text per language, such as {{\"{langs[0]}\": \"…\"}}")
        return
    if not isinstance(value, dict):
        err(f"{where}: required")
        return
    for l in langs:
        if not str(value.get(l, "")).strip():
            err(f"{where}.{l}: required")


def node_check(page: str) -> str | None:
    node = shutil.which("node")
    if not node:
        return None
    script = page[page.index("<script>") + 8 : page.rindex("</script>")]
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(script)
        path = f.name
    try:
        r = subprocess.run([node, "--check", path], capture_output=True, text=True)
        return None if r.returncode == 0 else (r.stderr or r.stdout).strip()
    finally:
        Path(path).unlink(missing_ok=True)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    cfg_path, out_path = Path(args[0]), Path(args[1])
    template = TEMPLATE.read_text(encoding="utf-8")
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{cfg_path}: not valid JSON: {e}")

    errors, warnings = check(cfg, builtin_ui(template))
    for w in warnings:
        print("warning:", w)
    if errors:
        for e in errors:
            print("error:", e)
        sys.exit(f"{len(errors)} error(s); nothing written")

    data = json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    page = template.replace("__TITLE__", html.escape(cfg["title"]), 1)
    if CONFIG_SLOT not in page:
        sys.exit("template.html has no config slot")
    page = page.replace(CONFIG_SLOT, "/*CONFIG-START*/" + data + "/*CONFIG-END*/", 1)

    if DATA_SLOT not in page:
        sys.exit("template.html has no data slot")
    if page.lower().count("</script") != 1:
        sys.exit("the page's script holds a closing script tag, which would end it early in a browser")

    problem = node_check(page)
    if problem:
        sys.exit("the page's script does not parse:\n" + problem)

    summary = f"{len(cfg['questions'])} questions, languages {', '.join(cfg['languages'])}"
    if "--standalone" in argv:
        doc = document(page, cfg["languages"][0])
        out_path.write_text(doc, encoding="utf-8")
        print(f"wrote {out_path} ({len(doc.encode())} bytes, {summary}): one file to share; it works opened in any browser")
        return
    out_path.write_text(page, encoding="utf-8")
    print(f"wrote {out_path} ({len(page.encode())} bytes, {summary})")
    if "--preview" in argv:
        preview = out_path.with_suffix(".preview.html")
        preview.write_text(document(page, cfg["languages"][0]), encoding="utf-8")
        print(f"wrote {preview} (for a local look only; publish {out_path.name})")


def document(page: str, lang: str) -> str:
    """The page as a complete HTML file: its title, font links and styles in the head, the rest in the body."""
    cut = page.index("</style>") + len("</style>")
    return ('<!doctype html>\n<html lang="' + html.escape(lang) + '">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            + page[:cut] + "\n</head>\n<body>\n" + page[cut:] + "\n</body>\n</html>\n")


if __name__ == "__main__":
    main(sys.argv[1:])
