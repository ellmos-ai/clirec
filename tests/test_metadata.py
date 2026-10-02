"""Automated contract tests for repository hygiene, CI/CD, and metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ci_workflows_timeout_guardrails():
    """Every job across all CI workflows must define an explicit timeout-minutes."""
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir()

    expected_workflows = [
        "tests.yml",
        "codeql.yml",
        "stale.yml",
        "welcome.yml",
        "auto-assign.yml",
        "label-sync.yml",
    ]
    for wf_name in expected_workflows:
        wf_path = workflows_dir / wf_name
        assert wf_path.is_file(), f"Missing workflow {wf_name}"
        text = wf_path.read_text(encoding="utf-8")
        assert "timeout-minutes:" in text, f"{wf_name} lacks timeout-minutes guardrail"


def test_stale_workflow_present_and_valid():
    """Stale workflow must have least-privilege permissions and concurrency."""
    stale_path = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_path.is_file()
    text = stale_path.read_text(encoding="utf-8")
    assert "actions/stale@" in text
    assert "issues: write" in text
    assert "pull-requests: write" in text
    assert "timeout-minutes: 10" in text
    assert "cancel-in-progress: true" in text


def test_welcome_workflow_present_and_valid():
    """Welcome workflow must have first-interaction action, concurrency, and timeout."""
    welcome_path = REPO_ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_path.is_file()
    text = welcome_path.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in text
    assert "issues: write" in text
    assert "pull-requests: write" in text
    assert "timeout-minutes: 5" in text
    assert "cancel-in-progress: true" in text


def test_auto_assign_workflow_present_and_valid():
    """Auto-assign workflow uses least-privilege and bounded execution."""
    aa_path = REPO_ROOT / ".github" / "workflows" / "auto-assign.yml"
    assert aa_path.is_file()
    text = aa_path.read_text(encoding="utf-8")
    assert "actions/github-script@" in text
    assert "issues: write" in text
    assert "pull-requests: write" in text
    assert "timeout-minutes: 5" in text
    assert "cancel-in-progress: true" in text


def test_label_sync_workflow_and_labels_present():
    """Label-sync workflow and labels.yml must define standard 11 governance labels."""
    ls_path = REPO_ROOT / ".github" / "workflows" / "label-sync.yml"
    labels_path = REPO_ROOT / ".github" / "labels.yml"
    assert ls_path.is_file()
    assert labels_path.is_file()

    ls_text = ls_path.read_text(encoding="utf-8")
    assert "EndBug/label-sync@v2" in ls_text
    assert "issues: write" in ls_text
    assert "timeout-minutes: 5" in ls_text
    assert "cancel-in-progress: true" in ls_text

    labels_text = labels_path.read_text(encoding="utf-8")
    for lbl in [
        "bug",
        "enhancement",
        "good first issue",
        "help wanted",
        "documentation",
        "duplicate",
        "wontfix",
        "priority: high",
        "priority: low",
        "needs-triage",
        "stale",
    ]:
        assert f"name: {lbl}" in labels_text or f"name: '{lbl}'" in labels_text


def test_gitignore_multihost_and_lock_defense():
    """Gitignore must protect against multi-host conflict files, locks, and caches."""
    gi_path = REPO_ROOT / ".gitignore"
    assert gi_path.is_file()
    text = gi_path.read_text(encoding="utf-8")

    required_patterns = [
        "Desktop.ini",
        "desktop.ini",
        "Thumbs.db",
        "ehthumbs.db",
        "*.swo",
        "* (kopie)*",
        "* (copy)*",
        "*conflicted copy*",
        "*.sync-conflict-*",
        "*.conflict",
        "*-WORKSTATION*",
        "*-WORKSTATION.*",
        "*-ASUS*",
        "*-IDEAPAD*",
        "*-MacBook*",
        "LOCK",
        "LOCK.*",
        "LOCK.txt",
        "LOCK.user.*",
        "LOCK.until.*",
        "LOCK.condition.*",
        "LOCK.dev.*",
        "LOCK.antigravity.*",
        "LOCK.bugsearch.*",
        ".automation-lock",
        "LOCK.permissions.json",
        "uv.lock",
        "!package-lock.json",
        "TASKPLAN_*.md",
        "/MARKETING-LOG.txt",
        ".tox/",
        ".turbo/",
        ".hypothesis/",
        ".nyc_output/",
        ".coverage*",
    ]
    for pattern in required_patterns:
        assert pattern in text, f"Missing pattern in .gitignore: {pattern}"


def test_notice_attribution_file_present():
    """Canonical NOTICE attribution file must exist with ecosystem references."""
    notice_path = REPO_ROOT / "NOTICE"
    assert notice_path.is_file()
    text = notice_path.read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Lukas Geiger" in text
    assert "ellmos-ai" in text
    assert "open-bricks" in text
    assert "THIRD_PARTY_LICENSES.md" in text
    assert "THIRD_PARTY_LICENSES.txt" in text


def test_pep621_license_and_urls():
    """pyproject.toml must conform to PEP 621 standards with license-files and URLs."""
    toml_path = REPO_ROOT / "pyproject.toml"
    assert toml_path.is_file()
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    expected_license_files = [
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_LICENSES.md",
        "THIRD_PARTY_LICENSES.txt",
    ]
    assert project.get("license-files") == expected_license_files

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Changelog" in urls
    assert "Contributing" in urls
    assert "Issues" in urls
    assert "LLM Context" in urls
    assert "Third-Party Licenses" in urls
    assert "Third-Party Licenses (Text)" in urls
    assert "Plain-Text License" in urls
    assert "Dependency License Information" in urls
    assert "Notice" in urls

    keywords = project.get("keywords", [])
    required_kws = [
        "local-first",
        "desktop-capture",
        "open-bricks",
        "ellmos-ai",
        "computer-use",
        "clirec",
    ]
    for req_kw in required_kws:
        assert req_kw in keywords, f"Missing required keyword: {req_kw}"

    pytest_cfg = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "-ra" in pytest_cfg.get("addopts", "")
    assert "--basetemp=.pytest_temp" in pytest_cfg.get("addopts", "")
    assert pytest_cfg.get("minversion") == "7.0"
    assert "build" in pytest_cfg.get("norecursedirs", [])
    assert ".pytest_temp" in pytest_cfg.get("norecursedirs", [])
    assert ".pytest_tmp*" in pytest_cfg.get("norecursedirs", [])
    assert ".hypothesis" in pytest_cfg.get("norecursedirs", [])
    assert ".turbo" in pytest_cfg.get("norecursedirs", [])

    ruff_lint = data.get("tool", {}).get("ruff", {}).get("lint", {})
    select = ruff_lint.get("select", [])
    for rule in ["E", "F", "W", "B", "C4"]:
        assert rule in select, f"Missing ruff lint rule: {rule}"


def test_version_parity():
    """Package version must match across pyproject.toml, clirec, and manifests."""
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


def test_llms_txt_references():
    """llms.txt must list current project references."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.is_file()
    text = llms_path.read_text(encoding="utf-8")
    assert "tests/" in text
    assert "NOTICE" in text
    assert "welcome.yml" in text
    assert "auto-assign.yml" in text
    assert "label-sync.yml" in text
    assert "THIRD_PARTY_LICENSES.md" in text
    assert "THIRD_PARTY_LICENSES.txt" in text
    assert "CONTRIBUTING.md" in text
    assert "[PERSONA-01]" in text


def test_changelog_recent_entry():
    """CHANGELOG.md must document recent maintenance/releases."""
    cl_path = REPO_ROOT / "CHANGELOG.md"
    assert cl_path.is_file()
    text = cl_path.read_text(encoding="utf-8")
    assert "2026-09-13" in text
    assert "2026-09-16" in text
    assert "2026-09-23" in text
    assert "2026-09-26" in text
    assert "2026-09-29" in text


def test_quick_navigation_anchor_parity():
    """README.md and README_de.md must have 18-point quick navigation with parity."""
    en_path = REPO_ROOT / "README.md"
    de_path = REPO_ROOT / "README_de.md"
    assert en_path.is_file()
    assert de_path.is_file()

    en_text = en_path.read_text(encoding="utf-8")
    de_text = de_path.read_text(encoding="utf-8")

    # 18 numbered anchor sections with sec-01..sec-18 dual reciprocal anchors
    for i in range(1, 19):
        sec_tag = f"sec-{i:02d}"
        assert f'id="{sec_tag}"' in en_text, f"Missing {sec_tag} in README.md"
        assert f'id="{sec_tag}"' in de_text, f"Missing {sec_tag} in README_de.md"
        assert f'<a id="{i}-' in en_text or f"## {i}." in en_text, (
            f"Missing section {i} in README.md"
        )
        assert f'<a id="{i}-' in de_text or f"## {i}." in de_text, (
            f"Missing section {i} in README_de.md"
        )

    # Semantic cross-language anchors
    semantic_anchors = [
        "target-personas--discoverability",
        "comparative-matrix-vs-alternatives",
        "governance--runtime-invariants",
        "third-party-licenses--transparency",
    ]
    for anchor in semantic_anchors:
        assert f'id="{anchor}"' in en_text, f"Missing anchor {anchor} in README.md"
        assert f'id="{anchor}"' in de_text, f"Missing anchor {anchor} in README_de.md"


def test_target_personas_definitions():
    """Both READMEs and llms.txt must define all 4 target personas."""
    en_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_text = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    llms_text = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")

    personas = ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]
    for p in personas:
        assert p in en_text, f"Missing {p} in README.md"
        assert p in de_text, f"Missing {p} in README_de.md"
        assert p in llms_text, f"Missing {p} in llms.txt"


def test_declared_dependency_license_notes():
    """Dependency license notes identify declared optional packages."""
    lic_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.is_file()
    text = lic_path.read_text(encoding="utf-8")

    assert "Third-Party License Information" in text
    assert "MIT License" in text
    assert "pynput" in text
    assert "LGPL-3.0" in text
    assert "sounddevice" in text
    assert "uiautomation" in text
    assert "persist=False" in text
    assert "permission from other people" in text


def test_third_party_licenses_plain_text_companion():
    """Plain-text dependency license information lists declared packages."""
    txt_path = REPO_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert txt_path.is_file()
    text = txt_path.read_text(encoding="utf-8")

    assert "Third-Party License Information" in text
    assert "Project license: MIT License" in text
    assert "pynput" in text
    assert "LGPL-3.0" in text
    assert "sounddevice" in text
    assert "uiautomation" in text
    assert "pytest" in text
    assert "ruff" in text


def test_contributing_guidelines_present():
    """CONTRIBUTING.md must state contributor workflow and version metadata."""
    contrib_path = REPO_ROOT / "CONTRIBUTING.md"
    assert contrib_path.is_file()
    text = contrib_path.read_text(encoding="utf-8")

    assert "0.3.0" in text
    assert "pytest" in text
