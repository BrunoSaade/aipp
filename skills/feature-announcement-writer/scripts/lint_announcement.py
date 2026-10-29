#!/usr/bin/env python3
"""Deterministic checks for a generated feature announcement.

Usage:
    python lint_announcement.py [FILE] [--max-chars N] [--channel slack|whatsapp|gchat|teams]

Reads the announcement from FILE (or stdin). Prints one finding per line as
`<check> line <n>: <snippet>` and exits 1 when any finding exists, 0 otherwise.
Checks: leaked file paths, Jira links/keys, English sentences, channel formatting, total length.
"""

import argparse
import re
import sys

DEFAULT_MAX_CHARS = 3000
MIN_ENGLISH_STOPWORDS = 3

CODE_EXTENSIONS = "ts|tsx|js|jsx|mjs|py|go|java|kt|rb|php|cs|sql|css|scss|html|vue|json|ya?ml|toml|md|sh"
PATH_PATTERN = re.compile(rf"\b[\w./-]*[\w-]+\.(?:{CODE_EXTENSIONS})\b")
JIRA_LINK_PATTERN = re.compile(r"atlassian\.net|/browse/[A-Z]")
JIRA_KEY_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-\d+\b")
# ponytail: tiny allowlist of standard-name prefixes, extend when a real false positive shows up
NON_TICKET_PREFIXES = {"UTF", "SHA", "ISO", "RFC", "COVID", "MP3", "MP4", "H264"}

# No channel documents **double** bold. Headings and [text](url) links render only on Teams.
# Slack keeps pasted text plain, so even *single* markers show literally there. See references/channels.md.
CHANNELS = ("slack", "whatsapp", "gchat", "teams")
DEFAULT_CHANNEL = "slack"
FORMAT_PATTERNS = {
    "double-asterisk bold": re.compile(r"\*\*[^*]+\*\*"),
    "asterisk marker": re.compile(r"(?<!\*)\*[^*\s][^*]*\*(?!\*)"),
    "heading": re.compile(r"^#{1,6}\s"),
    "markdown link": re.compile(r"\[[^\]]+\]\(\S+\)"),
}
ALLOWED_FORMATS = {
    "slack": set(),
    "whatsapp": {"asterisk marker"},
    "gchat": {"asterisk marker"},
    "teams": {"asterisk marker", "heading", "markdown link"},
}

WORD_PATTERN = re.compile(r"[a-zà-ú']+")
# Stopwords only: tech loanwords (deploy, login, dashboard) must not count as English.
ENGLISH_STOPWORDS = {
    "the", "is", "are", "was", "were", "this", "that", "these", "those", "with",
    "for", "and", "now", "will", "has", "have", "been", "all", "you", "your",
    "we", "our", "it", "its", "of", "to", "in", "on", "be", "can", "new",
}
PORTUGUESE_STOPWORDS = {
    "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "e", "é",
    "em", "no", "na", "para", "com", "que", "foi", "foram", "agora", "não",
    "por", "se", "ao", "mais", "seu", "sua", "pessoal",
}


def find_paths(line):
    return [match.group(0) for match in PATH_PATTERN.finditer(line)]


def find_jira_refs(line):
    if JIRA_LINK_PATTERN.search(line):
        return [line.strip()]
    keys = JIRA_KEY_PATTERN.finditer(line)
    return [key.group(0) for key in keys if key.group(1) not in NON_TICKET_PREFIXES]


def find_english(line):
    words = WORD_PATTERN.findall(line.lower())
    english_count = sum(word in ENGLISH_STOPWORDS for word in words)
    portuguese_count = sum(word in PORTUGUESE_STOPWORDS for word in words)
    if english_count >= MIN_ENGLISH_STOPWORDS and english_count > portuguese_count:
        return [line.strip()]
    return []


def find_format_issues(line, channel):
    allowed = ALLOWED_FORMATS[channel]
    return [name for name, pattern in FORMAT_PATTERNS.items() if name not in allowed and pattern.search(line)]


LINE_CHECKS = {"path": find_paths, "jira": find_jira_refs, "english": find_english}


def lint(text, max_chars, channel=DEFAULT_CHANNEL):
    checks = {**LINE_CHECKS, "format": lambda line: find_format_issues(line, channel)}
    findings = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for check_name, check in checks.items():
            findings += [f"{check_name} line {line_number}: {hit}" for hit in check(line)]
    if len(text) > max_chars:
        findings.append(f"length: {len(text)} chars > max {max_chars}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", type=argparse.FileType("r", encoding="utf-8"), default=sys.stdin)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--channel", choices=CHANNELS, default=DEFAULT_CHANNEL)
    args = parser.parse_args()
    findings = lint(args.file.read(), args.max_chars, args.channel)
    print("\n".join(findings) if findings else "ok")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
