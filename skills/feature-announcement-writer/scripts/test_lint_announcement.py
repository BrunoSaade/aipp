"""Tests for lint_announcement.py (deterministic checks on a generated announcement)."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "lint_announcement.py"

CLEAN = """🚀 Exportação de pedidos em CSV

Pessoal, agora é possível exportar os pedidos do mês em uma planilha pelo painel administrativo.

✨ O que mudou?
📝 O administrador escolhe o período e o sistema gera o arquivo automaticamente.
🧪 Foram adicionados testes automatizados para as colunas da planilha.

Caso encontrem qualquer comportamento inesperado, reportem no canal da squad. 🙌
"""


def _lint(text, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=text,
        capture_output=True,
        text=True,
        check=False,
    )


def test_clean_announcement_passes():
    result = _lint(CLEAN)
    assert result.returncode == 0, result.stdout


def test_leaked_file_path_fails():
    result = _lint(CLEAN + "\nAlterado em src/lib/order-export.ts para gerar o arquivo.\n")
    assert result.returncode == 1
    assert "path" in result.stdout


def test_jira_link_fails():
    result = _lint(CLEAN + "\nDetalhes: https://empresa.atlassian.net/browse/PROJ-123\n")
    assert result.returncode == 1
    assert "jira" in result.stdout


def test_bare_jira_key_fails():
    result = _lint(CLEAN + "\nRelacionado à PROJ-123.\n")
    assert result.returncode == 1
    assert "jira" in result.stdout


def test_english_sentence_fails():
    result = _lint(CLEAN + "\nThis feature is now available for all the users with a new flow.\n")
    assert result.returncode == 1
    assert "english" in result.stdout


def test_common_tech_loanwords_do_not_trigger_english():
    text = CLEAN + "\n🔄 O deploy do dashboard foi feito e o login continua igual.\n"
    assert _lint(text).returncode == 0


def test_too_long_fails_and_limit_is_configurable():
    assert _lint(CLEAN, "--max-chars", "100").returncode == 1
    assert "length" in _lint(CLEAN, "--max-chars", "100").stdout
    assert _lint(CLEAN, "--max-chars", "5000").returncode == 0


def test_double_asterisk_bold_fails_on_every_channel():
    text = CLEAN + "\n✨ **O que mudou?**\n"
    for channel in ("slack", "whatsapp", "gchat", "teams"):
        result = _lint(text, "--channel", channel)
        assert result.returncode == 1, channel
        assert "format" in result.stdout


def test_single_asterisk_bold_fails_only_on_slack():
    # Slack composer keeps pasted text plain, so markers show up literally.
    text = CLEAN + "\n✨ *O que mudou?*\n"
    assert "format" in _lint(text, "--channel", "slack").stdout
    for channel in ("whatsapp", "gchat", "teams"):
        assert _lint(text, "--channel", channel).returncode == 0, channel


def test_heading_allowed_only_on_teams():
    text = CLEAN + "\n# Novidade\n"
    assert _lint(text, "--channel", "teams").returncode == 0
    assert "format" in _lint(text, "--channel", "slack").stdout


def test_markdown_link_allowed_only_on_teams():
    text = CLEAN + "\nVeja [o guia](https://exemplo.com.br/guia).\n"
    assert _lint(text, "--channel", "teams").returncode == 0
    assert "format" in _lint(text, "--channel", "whatsapp").stdout


def test_reads_file_argument(tmp_path):
    msg = tmp_path / "msg.md"
    msg.write_text(CLEAN, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(msg)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout
