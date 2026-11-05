"""Tests for the disabled MCP servers line of statusline-command.sh."""

import json
import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "statusline-command.sh"
LABEL = "mcp/disabled"


def run_statusline(tmp_path: Path, projects: dict) -> str:
    """Run the script against a fake config dir.

    Args:
        tmp_path: Directory that holds the fake config and serves as cwd.
        projects: Value of the `projects` key in the fake .claude.json.

    Returns:
        The stdout of the script.
    """
    config_dir = tmp_path / "config"
    (config_dir / "logs").mkdir(parents=True)
    (config_dir / ".claude.json").write_text(json.dumps({"projects": projects}))
    payload = {"workspace": {"current_dir": "/proj/a", "project_dir": "/proj/a"}}
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={
            **os.environ,
            "CLAUDE_CONFIG_DIR": str(config_dir),
            "CLAUDE_PROJECT_DIR": str(tmp_path),
        },
        check=True,
    )
    return result.stdout


def test_shows_only_total_for_current_project(tmp_path):
    """Only the current project's disabled MCP count is shown, not server names."""
    projects = {"/proj/a": {"disabledMcpServers": ["aipp:sqlite", "claude.ai Gmail"]}}
    output = run_statusline(tmp_path, projects)
    assert f"{LABEL}(2)" in output
    assert "aipp:sqlite" not in output


def test_ignores_other_projects(tmp_path):
    """Disabled servers of other projects are not counted."""
    projects = {
        "/proj/a": {"disabledMcpServers": ["aipp:sqlite"]},
        "/proj/b": {"disabledMcpServers": ["aipp:github", "aipp:notion"]},
    }
    assert f"{LABEL}(1)" in run_statusline(tmp_path, projects)


def test_omits_line_when_nothing_disabled(tmp_path):
    """No segment when the current project has nothing disabled."""
    projects = {"/proj/a": {"disabledMcpServers": []}, "/proj/b": {}}
    assert LABEL not in run_statusline(tmp_path, projects)


def test_omits_line_when_project_is_unknown(tmp_path):
    """No segment when the current project is not in .claude.json."""
    assert LABEL not in run_statusline(tmp_path, {})



def test_weekly_reset_date_from_resets_at(tmp_path):
    """The 7-day reset label is rendered from resets_at on both BSD and GNU date."""
    config_dir = tmp_path / "config"
    (config_dir / "logs").mkdir(parents=True)
    (config_dir / ".claude.json").write_text("{}")
    payload = {
        "workspace": {"current_dir": "/proj/a", "project_dir": "/proj/a"},
        # 2026-11-12 12:00:00 UTC — midday, so the day is the same in any common timezone
        "rate_limits": {"seven_day": {"used_percentage": 10, "resets_at": 1794484800}},
    }
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir), "TZ": "UTC"},
        check=True,
    )
    assert "Nov 12th" in result.stdout
    assert "illegal option" not in result.stderr
