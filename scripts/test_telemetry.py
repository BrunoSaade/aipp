"""Tests for telemetry.sh (backs the /telemetry command)."""

import json
import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "telemetry.sh"
COMPOSE = Path(__file__).parent.parent / "docker/telemetry/docker-compose.yml"


def setup(tmp_path: Path, enabled: str) -> tuple[Path, Path]:
    """Create a fake config dir and a fake `docker` that logs its arguments.

    Returns:
        The settings file path and the docker call log path.
    """
    config = tmp_path / "config"
    config.mkdir()
    settings = config / "settings.json"
    settings.write_text(json.dumps({"env": {"CLAUDE_CODE_ENABLE_TELEMETRY": enabled, "KEEP": "x"}}))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "docker.log"
    docker = bin_dir / "docker"
    docker.write_text(f'#!/usr/bin/env bash\necho "$*" >> {log}\necho "otel-collector running"\n')
    docker.chmod(0o755)
    return settings, log


def run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run telemetry.sh against the fake config dir and fake docker."""
    env = {
        **os.environ,
        "CLAUDE_CONFIG_DIR": str(tmp_path / "config"),
        "PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}",
    }
    return subprocess.run(
        ["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env, check=False
    )


def test_off_disables_env_and_stops_stack(tmp_path: Path) -> None:
    """`off` flips the env flag to 0, keeps other keys and stops the stack."""
    settings, log = setup(tmp_path, "1")
    result = run(tmp_path, "off")
    assert result.returncode == 0, result.stderr
    env = json.loads(settings.read_text())["env"]
    assert env == {"CLAUDE_CODE_ENABLE_TELEMETRY": "0", "KEEP": "x"}
    assert f"compose -f {COMPOSE} stop" in log.read_text()


def test_on_enables_env_and_starts_stack(tmp_path: Path) -> None:
    """`on` flips the env flag to 1 and brings the stack up."""
    settings, log = setup(tmp_path, "0")
    assert run(tmp_path, "on").returncode == 0
    assert json.loads(settings.read_text())["env"]["CLAUDE_CODE_ENABLE_TELEMETRY"] == "1"
    assert f"compose -f {COMPOSE} up -d" in log.read_text()


def test_status_reports_flag_without_changes(tmp_path: Path) -> None:
    """`status` prints the flag and stack state and edits nothing."""
    settings, _ = setup(tmp_path, "1")
    before = settings.read_text()
    result = run(tmp_path, "status")
    assert result.returncode == 0
    assert "telemetry: ON" in result.stdout
    assert "otel-collector running" in result.stdout
    assert settings.read_text() == before


def test_unknown_argument_fails(tmp_path: Path) -> None:
    """An unknown subcommand exits non-zero with usage."""
    setup(tmp_path, "1")
    result = run(tmp_path, "bogus")
    assert result.returncode != 0
    assert "usage" in result.stderr
