"""Tests for the node selection of tlc-exec-log.sh."""

import os
import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "tlc-exec-log.sh"


def fake_node(bin_dir: Path, label: str) -> None:
    """Create a fake `node` that prints its label instead of running anything."""
    bin_dir.mkdir(parents=True)
    node = bin_dir / "node"
    node.write_text(f"#!/usr/bin/env bash\necho {label}\n")
    node.chmod(0o755)


def run_wrapper(tmp_path: Path, extra_env: dict) -> str:
    """Run the wrapper with a fake HOME, an old node on PATH and nvm's node 24.16.0."""
    fake_node(tmp_path / "path-bin", "path-node")
    fake_node(tmp_path / ".nvm/versions/node/v24.16.0/bin", "nvm-node-24")
    bash = shutil.which("bash")
    assert bash, "bash not found on PATH"
    env = {k: v for k, v in os.environ.items() if k != "NODE_VERSION"}
    env |= {
        "HOME": str(tmp_path),
        "CLAUDE_CONFIG_DIR": str(tmp_path / "config"),
        # ext-log.sh needs bash >= 4.2; keep the same bash the real hooks resolve.
        "PATH": f"{tmp_path / 'path-bin'}:{Path(bash).parent}:/usr/bin:/bin",
        **extra_env,
    }
    result = subprocess.run(
        ["bash", str(SCRIPT), "session-start"],
        input="{}",
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout


def test_uses_nvm_node_matching_node_version(tmp_path: Path) -> None:
    """NODE_VERSION installed in nvm wins over the node on PATH."""
    assert run_wrapper(tmp_path, {"NODE_VERSION": "24.16.0"}).strip() == "nvm-node-24"


def test_falls_back_to_path_node_when_version_not_installed(tmp_path: Path) -> None:
    """A NODE_VERSION missing from nvm falls back to the node on PATH."""
    assert run_wrapper(tmp_path, {"NODE_VERSION": "99.0.0"}).strip() == "path-node"


def test_falls_back_to_path_node_without_node_version(tmp_path: Path) -> None:
    """Without NODE_VERSION the node on PATH is used."""
    assert run_wrapper(tmp_path, {}).strip() == "path-node"
