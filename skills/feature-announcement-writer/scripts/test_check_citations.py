"""Tests for check_citations.py (every message line must cite a verbatim quote found in the source pack)."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "check_citations.py"

PACK = """# PR #22 — Criação de devices em lote

## PRD
O operador precisa cadastrar dezenas de devices de uma vez, hoje faz um por um.
O lote gera um ZIP com os QR codes de todos os devices.

## Commits
- add batch device creation form
- add `zip` download of batch QR codes
"""

DRAFT = """🚀 *Criação de dispositivos em lote* [—]

Pessoal, agora dá pra criar vários dispositivos de uma vez [1][2].
📦 O lote gera um ZIP com os QR codes [3].

Reportem no canal da squad. 🙌 [—]
---fontes---
[1] "add batch device creation form"
[2] "cadastrar dezenas de devices de uma vez"
[3] "O lote gera um ZIP com os QR codes"
"""


def _check(tmp_path, draft, pack=PACK, *args):
    pack_file = tmp_path / "pack.md"
    draft_file = tmp_path / "draft.md"
    pack_file.write_text(pack, encoding="utf-8")
    draft_file.write_text(draft, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(pack_file), str(draft_file), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cited_draft_passes(tmp_path):
    result = _check(tmp_path, DRAFT)
    assert result.returncode == 0, result.stdout
    assert result.stdout.startswith("ok")


def test_quote_missing_from_pack_fails(tmp_path):
    draft = DRAFT.replace('"O lote gera um ZIP com os QR codes"', '"exportação 50% mais rápida"')
    result = _check(tmp_path, draft)
    assert result.returncode == 1
    assert "[3]" in result.stdout and "not found" in result.stdout


def test_line_without_marker_fails(tmp_path):
    draft = DRAFT.replace("Reportem no canal da squad. 🙌 [—]", "Reportem no canal da squad. 🙌")
    result = _check(tmp_path, draft)
    assert result.returncode == 1
    assert "no citation" in result.stdout and "line 6" in result.stdout


def test_marker_without_source_entry_fails(tmp_path):
    draft = DRAFT.replace("[3].", "[4].")
    result = _check(tmp_path, draft)
    assert result.returncode == 1
    assert "[4]" in result.stdout


def test_short_quote_fails(tmp_path):
    draft = DRAFT.replace('"O lote gera um ZIP com os QR codes"', '"QR codes"')
    result = _check(tmp_path, draft)
    assert result.returncode == 1
    assert "too short" in result.stdout


def test_missing_sources_section_fails(tmp_path):
    draft = DRAFT.split("---fontes---")[0]
    result = _check(tmp_path, draft)
    assert result.returncode == 1
    assert "---fontes---" in result.stdout


def test_quote_normalizes_case_whitespace_and_markdown(tmp_path):
    draft = DRAFT.replace('"O lote gera um ZIP com os QR codes"', '"ADD  zip download of batch"')
    result = _check(tmp_path, draft)
    assert result.returncode == 0, result.stdout


def test_uncited_lines_are_listed_for_review(tmp_path):
    result = _check(tmp_path, DRAFT)
    assert "no claim: 🚀 *Criação de dispositivos em lote*" in result.stdout
    assert "no claim: Reportem no canal da squad. 🙌" in result.stdout


def test_out_writes_clean_message_without_markers_or_sources(tmp_path):
    out = tmp_path / "message.md"
    result = _check(tmp_path, DRAFT, PACK, "--out", str(out))
    assert result.returncode == 0, result.stdout
    clean = out.read_text(encoding="utf-8")
    assert "[" not in clean and "---fontes---" not in clean
    assert "Pessoal, agora dá pra criar vários dispositivos de uma vez." in clean
    assert clean.startswith("🚀 *Criação de dispositivos em lote*\n")


def test_failure_does_not_write_out(tmp_path):
    out = tmp_path / "message.md"
    draft = DRAFT.replace("[3].", "[4].")
    result = _check(tmp_path, draft, PACK, "--out", str(out))
    assert result.returncode == 1
    assert not out.exists()
