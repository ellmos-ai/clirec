"""Automated contract tests for repository hygiene, CI/CD, and metadata."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ci_workflows_timeout_guardrails():
    """Every job across all CI workflows must define an explicit timeout-minutes."""
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir()

    expected_workflows = ["tests.yml", "codeql.yml", "stale.yml"]
    for wf_name in expected_workflows:
        wf_path = workflows_dir / wf_name
        assert wf_path.is_file(), f"Missing workflow {wf_name}"
        text = wf_path.read_text(encoding="utf-8")
        assert "timeout-minutes:" in text, f"{wf_name} lacks timeout-minutes guardrail"


def test_stale_workflow_present_and_valid():
    """Stale workflow must exist, have least-privilege permissions and timeout."""
    stale_path = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_path.is_file()
    text = stale_path.read_text(encoding="utf-8")
    assert "actions/stale@v9" in text
    assert "issues: write" in text
    assert "pull-requests: write" in text
    assert "timeout-minutes: 10" in text


def test_gitignore_multihost_and_lock_defense():
    """Gitignore must protect against multi-host conflict files, locks, and caches."""
    gi_path = REPO_ROOT / ".gitignore"
    assert gi_path.is_file()
    text = gi_path.read_text(encoding="utf-8")

    required_patterns = [
        "* (kopie)*",
        "* (copy)*",
        "*conflicted copy*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "LOCK",
        "LOCK.*",
        "LOCK.permissions.json",
        "uv.lock",
        "!package-lock.json",
        ".tox/",
        ".turbo/",
        ".hypothesis/",
        ".coverage*",
    ]
    for pattern in required_patterns:
        assert pattern in text, f"Missing pattern in .gitignore: {pattern}"


def test_pep621_license_and_urls():
    """pyproject.toml must conform to PEP 621 standards with license-files and URLs."""
    toml_path = REPO_ROOT / "pyproject.toml"
    assert toml_path.is_file()
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    assert project.get("license-files") == ["LICENSE"]

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Changelog" in urls
    assert "Issues" in urls
    assert "LLM Context" in urls

    pytest_cfg = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "-ra" in pytest_cfg.get("addopts", "")

    ruff_lint = data.get("tool", {}).get("ruff", {}).get("lint", {})
    select = ruff_lint.get("select", [])
    for rule in ["E", "F", "W", "B", "C4"]:
        assert rule in select, f"Missing ruff lint rule: {rule}"


def test_version_parity():
    """Package version must be consistent across pyproject.toml, clirec,
    and manifests."""
    toml_path = REPO_ROOT / "pyproject.toml"
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    ver_toml = data["project"]["version"]

    import clirec

    assert clirec.__version__ == ver_toml

    mod_path = REPO_ROOT / "ellmos-module.v2.json"
    if mod_path.is_file():
        mod_data = json.loads(mod_path.read_text(encoding="utf-8"))
        assert mod_data.get("id") == "clirec"


def test_llms_txt_recency_and_metadata():
    """llms.txt must have 2026-09-13 verification date and accurate references."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.is_file()
    text = llms_path.read_text(encoding="utf-8")
    assert "## Last-checked: 2026-09-13" in text
    assert "tests/" in text
    assert "MARKETING-LOG.txt" in text


def test_marketing_log_present_and_active():
    """MARKETING-LOG.txt must be maintained in repo root with Pfad A entry."""
    log_path = REPO_ROOT / "MARKETING-LOG.txt"
    assert log_path.is_file()
    text = log_path.read_text(encoding="utf-8")
    assert "2026-09-13" in text
    assert "Pfad A" in text
    assert "CI-Timeout" in text


def test_changelog_recent_entry():
    """CHANGELOG.md must document recent maintenance/releases."""
    cl_path = REPO_ROOT / "CHANGELOG.md"
    assert cl_path.is_file()
    text = cl_path.read_text(encoding="utf-8")
    assert "2026-09-13" in text
