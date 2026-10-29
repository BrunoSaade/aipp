#!/usr/bin/env python3
"""Build a source pack (evidence) for a feature announcement from one or more PRs.

Usage:
    python fetch_pr_context.py PR [PR ...] [--repo OWNER/REPO]

PR is a number or a GitHub PR URL. Requires an authenticated `gh` CLI.
Prints Markdown with, per PR: title, body, product docs added in the PR
(PRD/spec/requirements), commit headlines and a file summary. Never prints the
full diff: large PRs would blow the context and add noise.
"""

import argparse
import json
import re
import subprocess
import sys

PR_FIELDS = "number,title,body,url,headRefOid,additions,deletions,files,commits"
# Product-facing docs first; tasks/validation/design are execution detail, not announcement material.
DOC_PRIORITY = ("prd.md", "spec.md", "requirements.md", "readme.md")
MAX_DOC_CHARS = 6000
MAX_DOCS = 2
TEST_PATTERN = re.compile(r"(^|/)(tests?|__tests__)/|\.(test|spec)\.\w+$")
# Stack-agnostic: build output, vendored deps, lockfiles, migrations, snapshots, codegen, minified assets.
GENERATED_PATTERN = re.compile(
    r"(^|/)(dist|build|out|vendor|node_modules|migrations|__snapshots__)/"
    r"|\.lock$|-lock\.(json|ya?ml)$|\.snap$|snapshot|\.generated\.|\.min\.(js|css)$"
)
DOC_PATTERN = re.compile(r"\.(md|mdx|txt)$")
PR_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/pull/\d+")


def parse_repo(pr_url):
    match = PR_URL_PATTERN.search(pr_url)
    return match.group(1) if match else None


def select_docs(files):
    by_name = {}
    for file in files:
        name = file["path"].rsplit("/", 1)[-1].lower()
        by_name.setdefault(name, file["path"])
    return [by_name[name] for name in DOC_PRIORITY if name in by_name][:MAX_DOCS]


def classify_file(path):
    if GENERATED_PATTERN.search(path):
        return "generated"
    if TEST_PATTERN.search(path):
        return "tests"
    if DOC_PATTERN.search(path):
        return "docs"
    return "source"


def classify_files(files):
    summary = {"source": [], "tests": [], "docs": [], "generated": []}
    for file in files:
        summary[classify_file(file["path"])].append(file["path"])
    return summary


def truncate(text, limit=MAX_DOC_CHARS):
    return text if len(text) <= limit else text[:limit] + "\n[truncado]"


def build_source_pack(pr, docs):
    summary = classify_files(pr["files"])
    lines = [
        f"## PR #{pr['number']}: {pr['title']}",
        f"URL: {pr['url']} | +{pr['additions']}/-{pr['deletions']}",
        "",
        "### Descrição do PR",
        pr["body"].strip() or "(vazia)",
    ]
    for path, content in docs.items():
        lines += ["", f"### Doc: {path}", truncate(content)]
    if not docs:
        lines += ["", "### Docs", "(nenhum PRD/spec/requirements no PR)"]
    lines += ["", "### Commits"] + [f"- {commit['messageHeadline']}" for commit in pr["commits"]]
    lines += ["", "### Arquivos", *[f"- {kind}: {len(paths)}" for kind, paths in summary.items()]]
    lines += [f"  - {path}" for path in summary["source"] + summary["tests"]]
    return "\n".join(lines)


class GhError(Exception):
    pass


def run_gh(args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise GhError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def fetch_pr(ref, repo):
    repo_args = ["-R", repo] if repo else []
    return json.loads(run_gh(["pr", "view", ref, *repo_args, "--json", PR_FIELDS]))


def fetch_doc(repo, path, ref):
    raw_header = "Accept: application/vnd.github.raw"
    return run_gh(["api", "-H", raw_header, f"repos/{repo}/contents/{path}?ref={ref}"])


def build_pack(ref, repo):
    if ref.startswith("-"):
        raise GhError(f"invalid PR reference: {ref}")
    pr = fetch_pr(ref, repo)
    pr_repo = parse_repo(pr["url"])
    if not pr_repo:
        raise GhError(f"PR {ref} is not a GitHub pull request URL: {pr['url']}")
    docs = {path: fetch_doc(pr_repo, path, pr["headRefOid"]) for path in select_docs(pr["files"])}
    return build_source_pack(pr, docs)


def build_packs(refs, repo):
    """Build one pack per PR; a failing PR is reported, not fatal for the others."""
    packs, errors = [], []
    for ref in refs:
        try:
            packs.append(build_pack(ref, repo))
        except GhError as error:
            errors.append(str(error))
    return packs, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prs", nargs="+", help="PR number or URL")
    parser.add_argument("--repo", help="OWNER/REPO when PR is a bare number outside the repo")
    args = parser.parse_args()
    packs, errors = build_packs(args.prs, args.repo)
    print("\n\n---\n\n".join(packs))
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
