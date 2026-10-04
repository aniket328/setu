#!/usr/bin/env python3
"""Setu rebrand pass over the Twenty source tree. Idempotent: run after every upstream merge.

    python3 setu/rebrand.py            # apply
    python3 setu/rebrand.py --check    # exit 1 if anything would still change

Touches (text only — never identifiers, imports, comments, message IDs or copyright notices):
  1. Lingui catalogs (*.po): "Twenty" -> "Setu" in msgstr only, so message IDs stay intact. The Docker build is
     patched to compile these catalogs without re-extracting (extract would reset English to the source text).
  2. Plain string/JSX text in front, emails, ui and server code that is not wrapped in Lingui.
  3. twenty.com / github.com/twentyhq links -> CWI / our fork.
Never touched: files marked `@license Enterprise` (Twenty's commercial licence), the DPA template (a legal document
naming Twenty, PBC — needs our own text, not a name swap), webhook headers (integration contract), tests, seeds,
migrations, generated code.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://cwistudio.in"
APP = "https://setu.cwistudio.in"
SOURCE = "https://github.com/aniket328/setu"
SALES = "mailto:aniket@cwistudio.in?subject=Setu%20subscription"
SUPPORT = "mailto:hello@cwistudio.in?subject=Setu%20support"

PHRASES = {
    "Felix from Twenty": "Setu by CWI Studio",
    "A modern open-source CRM": "Setu — the CRM that bridges you and your customers",
    "Billing portal session error. Please retry or contact Twenty team": "Billing portal session error. Please retry or contact CWI Studio",
    "Checkout session error. Please retry or contact Twenty team": "Checkout session error. Please retry or contact CWI Studio",
}
URLS = [  # longest first
    ("https://raw.githubusercontent.com/twentyhq/twenty/main/docs/static/img/social-card.png", f"{APP}/images/setu-og.png"),
    ("https://github.com/twentyhq/twenty", SOURCE),
    ("https://twenty.com/pricing", SALES),
    ("https://twenty.com/contact", SALES),
    ("https://twenty.com/legal/terms", SITE),
    ("https://twenty.com/legal/privacy", SITE),
    ("https://twenty.com/developers", SITE),
    ("https://twenty.com/user-guide", SITE),
    ("https://docs.twenty.com", SITE),
    ("https://app.twenty.com", APP),
    ("https://twenty.com", SITE),
    ("mailto:support@twenty.com", SUPPORT),
    ("support@twenty.com", "hello@cwistudio.in"),
    ("contact@twenty.com", "aniket@cwistudio.in"),
    ("https://discord.gg/cx5n4Jzs57", SUPPORT),
    ("https://twentyhq.github.io/placeholder-images/workspaces/twenty-logo.png",
     f"{APP}/images/icons/android/android-launchericon-192-192.png"),
]
WORD = re.compile(r"(?<![A-Za-z0-9_./@<$-])Twenty(?![A-Za-z0-9_(@-]|\.[A-Za-z_])")

PO_DIRS = ["packages/twenty-front/src/locales", "packages/twenty-server/src/engine/core-modules/i18n/locales",
           "packages/twenty-emails/src/locales"]
CODE_DIRS = ["packages/twenty-front/src", "packages/twenty-emails/src", "packages/twenty-ui/src", "packages/twenty-server/src"]
SKIP_PARTS = {"node_modules", "__tests__", "__mocks__", "generated", "testing", "mock-data", "migrations", "seeder",
              "seeders", "seeds", "dev-seeder", "dpa", "webhook", "locales", "__stories__"}
SKIP_SUFFIX = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".stories.tsx", ".d.ts")
COMMENT = re.compile(r"^\s*(//|\*|/\*)")
LINGUI = re.compile(r"(\bt`|\bmsg`|<Trans\b|\bplural\(|\bselect\()")


def fix_text(s):
    for a, b in PHRASES.items():
        s = s.replace(a, b)
    for a, b in URLS:
        s = s.replace(a, b)
    return s


def fix_po(src):
    out, in_msgstr = [], False
    for line in src.splitlines(keepends=True):
        if line.startswith("msgstr"):
            in_msgstr = True
        elif line.startswith(("msgid", "msgctxt", "#")) or not line.strip():
            in_msgstr = False
        out.append(WORD.sub("Setu", fix_text(line)) if in_msgstr else line)
    return "".join(out)


def fix_code(src):
    out = []
    for line in src.splitlines(keepends=True):
        if (COMMENT.match(line) or LINGUI.search(line) or line.lstrip().startswith(("import ", "export * from"))
                or "Twenty, PBC" in line or "Twenty.com, PBC" in line):
            out.append(line)
            continue
        line = fix_text(line)
        out.append(WORD.sub("Setu", line) if "Twenty" in line else line)
    return "".join(out)


def targets():
    for d in PO_DIRS:
        for p in (ROOT / d).glob("*.po"):
            yield p, fix_po
    for d in CODE_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.suffix in (".ts", ".tsx") and p.is_file() and not (SKIP_PARTS & set(p.parts)) \
                    and not p.name.endswith(SKIP_SUFFIX):
                yield p, fix_code
    for f in ["packages/twenty-front/index.html", "packages/twenty-front/public/manifest.json"]:
        yield ROOT / f, lambda s: WORD.sub("Setu", fix_text(s))


def main():
    check = "--check" in sys.argv
    changed = []
    for p, fn in targets():
        if not p.exists():
            continue
        src = p.read_text(encoding="utf-8")
        if p.suffix in (".ts", ".tsx") and "@license Enterprise" in src:
            continue  # Twenty's commercial licence: never modified by us
        out = fn(src)
        if out != src:
            changed.append(p.relative_to(ROOT))
            if not check:
                p.write_text(out, encoding="utf-8")
    print(f"{'would change' if check else 'changed'} {len(changed)} files")
    for c in changed[:40]:
        print("  ", c)
    sys.exit(1 if check and changed else 0)


if __name__ == "__main__":
    main()
