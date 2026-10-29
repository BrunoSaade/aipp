"""Tests for fetch_pr_context.py pure helpers (no network, gh is never called)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import fetch_pr_context
import pytest
from fetch_pr_context import build_source_pack, classify_files, parse_repo, select_docs

FILES = [
    {"path": "docs/features/order-export/tasks.md", "additions": 580, "deletions": 0},
    {"path": "docs/features/order-export/spec.md", "additions": 150, "deletions": 0},
    {"path": "docs/features/order-export/PRD.md", "additions": 60, "deletions": 0},
    {"path": "docs/features/order-export/validation.md", "additions": 250, "deletions": 0},
    {"path": "package-lock.json", "additions": 773, "deletions": 0},
    {"path": "src/services/order-export.service.ts", "additions": 253, "deletions": 2},
    {"path": "tests/order-export.test.ts", "additions": 377, "deletions": 0},
    {"path": "src/lib/csv.spec.ts", "additions": 40, "deletions": 0},
]

PR = {
    "number": 22,
    "title": "Feat/exportar pedidos em CSV",
    "body": "",
    "url": "https://github.com/acme/app/pull/22",
    "headRefOid": "abc123",
    "additions": 1933,
    "deletions": 2,
    "files": FILES,
    "commits": [
        {"messageHeadline": "feat(orders): add csv export endpoint"},
        {"messageHeadline": "test(orders): cover csv columns"},
    ],
}


def test_select_docs_prefers_product_docs_in_priority_order():
    assert select_docs(FILES) == ["docs/features/order-export/PRD.md", "docs/features/order-export/spec.md"]


def test_select_docs_ignores_execution_artifacts():
    files = [{"path": "docs/x/tasks.md"}, {"path": "docs/x/validation.md"}]
    assert select_docs(files) == []


def test_classify_files_counts_tests_and_skips_generated():
    summary = classify_files(FILES)
    assert summary["tests"] == ["tests/order-export.test.ts", "src/lib/csv.spec.ts"]
    assert summary["source"] == ["src/services/order-export.service.ts"]
    assert "package-lock.json" in summary["generated"]


@pytest.mark.parametrize(
    "path",
    [
        "yarn.lock",
        "pnpm-lock.yaml",
        "package-lock.json",
        "dist/app.js",
        "build/index.html",
        "prisma/migrations/20260101_init/migration.sql",
        "src/__snapshots__/view.test.ts.snap",
        "src/api/client.generated.ts",
        "public/app.min.js",
        "vendor/lib/x.go",
    ],
)
def test_classify_file_detects_common_generated_files(path):
    assert fetch_pr_context.classify_file(path) == "generated"


def test_parse_repo_from_pr_url():
    assert parse_repo("https://github.com/acme/app/pull/22") == "acme/app"


def test_source_pack_flags_empty_body_and_lists_evidence():
    pack = build_source_pack(PR, {"docs/features/order-export/spec.md": "# Spec\nAdmin exporta pedidos."})
    assert "PR #22: Feat/exportar pedidos em CSV" in pack
    assert "(vazia)" in pack
    assert "Admin exporta pedidos." in pack
    assert "feat(orders): add csv export endpoint" in pack
    assert "tests: 2" in pack


def test_source_pack_truncates_long_docs():
    pack = build_source_pack(PR, {"spec.md": "x" * 20_000})
    assert "[truncado]" in pack
    assert len(pack) < 15_000


def test_source_pack_notes_missing_docs():
    assert "(nenhum PRD/spec/requirements no PR)" in build_source_pack(PR, {})


def test_build_packs_keeps_going_when_one_pr_fails(monkeypatch):
    def fake_fetch_pr(ref, repo):
        if ref == "99":
            raise fetch_pr_context.GhError("gh pr view 99 failed: not found")
        return PR

    monkeypatch.setattr(fetch_pr_context, "fetch_pr", fake_fetch_pr)
    monkeypatch.setattr(fetch_pr_context, "fetch_doc", lambda repo, path, ref: "# Doc")
    packs, errors = fetch_pr_context.build_packs(["22", "99"], None)
    assert len(packs) == 1
    assert errors == ["gh pr view 99 failed: not found"]


def test_build_packs_rejects_flag_like_ref(monkeypatch):
    monkeypatch.setattr(fetch_pr_context, "fetch_pr", lambda ref, repo: pytest.fail("gh called"))
    packs, errors = fetch_pr_context.build_packs(["--web"], None)
    assert packs == []
    assert "--web" in errors[0]


def test_build_packs_reports_non_github_url(monkeypatch):
    monkeypatch.setattr(fetch_pr_context, "fetch_pr", lambda ref, repo: {**PR, "url": "https://gitlab.com/a/b/-/merge_requests/1"})
    packs, errors = fetch_pr_context.build_packs(["1"], None)
    assert packs == []
    assert "GitHub" in errors[0]
