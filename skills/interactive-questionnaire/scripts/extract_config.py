#!/usr/bin/env python3
"""Read the config back out of a built or published questionnaire page.

    python3 -I extract_config.py PAGE.html [CONFIG.json]

PAGE.html is a page built by build.py, or the published page saved by the
Artifact tool (`action: "read"` with `path: "index.html"`). Writes the config
as indented JSON to CONFIG.json, or prints it.
"""
import json
import re
import sys
from pathlib import Path


def extract(page: str) -> dict:
    m = re.search(r"/\*CONFIG-START\*/(.*?)/\*CONFIG-END\*/", page, re.S)
    if not m:
        raise ValueError("no questionnaire config in this page (was it built by build.py?)")
    cfg = json.loads(m.group(1))
    if not isinstance(cfg, dict):
        raise ValueError("the page holds the empty template, not a built questionnaire")
    return cfg


def main(argv):
    if len(argv) not in (1, 2):
        sys.exit(__doc__)
    try:
        cfg = extract(Path(argv[0]).read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit(str(e))
    text = json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"
    if len(argv) == 2:
        Path(argv[1]).write_text(text, encoding="utf-8")
        print(f"wrote {argv[1]} ({len(cfg.get('questions', []))} questions)")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main(sys.argv[1:])
