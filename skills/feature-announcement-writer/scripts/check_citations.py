#!/usr/bin/env python3
"""Verify that every line of an announcement draft cites a verbatim quote from the source pack.

Usage:
    python check_citations.py PACK DRAFT [--out FILE]

DRAFT is the message with markers, then a `---fontes---` line, then one source per line:

    Pessoal, agora dá pra criar vários dispositivos de uma vez [1].
    ---fontes---
    [1] "add batch device creation form"

Every non-empty message line needs `[n]` markers, or `[—]` when it makes no factual claim
(title, section header, closing). Every quote must appear in PACK (case, whitespace, ` and *
ignored) and be at least MIN_QUOTE_CHARS long. Prints findings and exits 1, or prints `ok`
plus the `[—]` lines for human review and writes the marker-free message to --out.
This proves a quote exists in the source, not that it supports the sentence: that stays a human call.
"""

import argparse
import re
import sys

SOURCES_SEPARATOR = "---fontes---"
MIN_QUOTE_CHARS = 15
CITATION_PATTERN = re.compile(r"\[(\d+)\]")
NO_CLAIM_PATTERN = re.compile(r"\[[—-]\]")
MARKER_PATTERN = re.compile(r"\s*\[(?:\d+|[—-])\]")
SOURCE_PATTERN = re.compile(r'^\[(\d+)\]\s*["“](.+)["”]\s*$')


def normalize(text):
    return " ".join(re.sub(r"[`*]", "", text).lower().split())


def parse_sources(lines, findings):
    sources = {}
    for line in lines:
        if not line.strip():
            continue
        match = SOURCE_PATTERN.match(line.strip())
        if match:
            sources[match.group(1)] = match.group(2)
        else:
            findings.append(f'malformed source: {line.strip()} (expected [n] "quote")')
    return sources


def check(pack, draft):
    """Return (findings, no_claim_lines, clean_message)."""
    findings = []
    if SOURCES_SEPARATOR not in draft:
        return [f"missing {SOURCES_SEPARATOR} section"], [], ""
    message, sources_block = draft.split(SOURCES_SEPARATOR, 1)
    sources = parse_sources(sources_block.splitlines(), findings)
    pack_normalized = normalize(pack)

    for number, quote in sources.items():
        if len(normalize(quote)) < MIN_QUOTE_CHARS:
            findings.append(f'[{number}] quote too short (< {MIN_QUOTE_CHARS} chars): "{quote}"')
        elif normalize(quote) not in pack_normalized:
            findings.append(f'[{number}] quote not found in pack: "{quote}"')

    no_claim, clean_lines = [], []
    for line_number, line in enumerate(message.rstrip("\n").splitlines(), start=1):
        clean = MARKER_PATTERN.sub("", line).rstrip()
        clean_lines.append(clean)
        if not line.strip():
            continue
        citations = CITATION_PATTERN.findall(line)
        if not citations and not NO_CLAIM_PATTERN.search(line):
            findings.append(f"line {line_number}: no citation: {line.strip()}")
        findings += [f"line {line_number}: [{n}] has no source entry" for n in citations if n not in sources]
        if not citations and NO_CLAIM_PATTERN.search(line):
            no_claim.append(clean.strip())

    return findings, no_claim, "\n".join(clean_lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pack", type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("draft", type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("--out", help="write the marker-free message here when the check passes")
    args = parser.parse_args()
    findings, no_claim, clean = check(args.pack.read(), args.draft.read())
    if findings:
        print("\n".join(findings))
        return 1
    if args.out:
        with open(args.out, "w", encoding="utf-8") as out:
            out.write(clean)
    print("\n".join(["ok", *(f"no claim: {line}" for line in no_claim)]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
