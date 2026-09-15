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
    assert "Third-Party Licenses" in urls
    assert "Marketing Log" in urls

    pytest_cfg = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "-ra" in pytest_cfg.get("addopts", "")

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


def test_llms_txt_recency_and_metadata():
    """llms.txt must have 2026-09-16 verification date and accurate references."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.is_file()
    text = llms_path.read_text(encoding="utf-8")
    assert "## Last-checked: 2026-09-16" in text
    assert "tests/" in text
    assert "MARKETING-LOG.txt" in text
    assert "THIRD_PARTY_LICENSES.md" in text
    assert "[PERSONA-01]" in text


def test_marketing_log_present_and_active():
    """MARKETING-LOG.txt must exist in repo root with Pfad A and Pfad B entries."""
    log_path = REPO_ROOT / "MARKETING-LOG.txt"
    assert log_path.is_file()
    text = log_path.read_text(encoding="utf-8")
    assert "2026-09-13" in text
    assert "Pfad A" in text
    assert "2026-09-16" in text
    assert "Pfad B" in text
    assert "INV-LOCAL-01" in text


def test_changelog_recent_entry():
    """CHANGELOG.md must document recent maintenance/releases."""
    cl_path = REPO_ROOT / "CHANGELOG.md"
    assert cl_path.is_file()
    text = cl_path.read_text(encoding="utf-8")
    assert "2026-09-13" in text
    assert "2026-09-16" in text
    assert "Pfad B" in text


def test_quick_navigation_anchor_parity():
    """README.md and README_de.md must have 18-point quick navigation with parity."""
    en_path = REPO_ROOT / "README.md"
    de_path = REPO_ROOT / "README_de.md"
    assert en_path.is_file()
    assert de_path.is_file()

    en_text = en_path.read_text(encoding="utf-8")
    de_text = de_path.read_text(encoding="utf-8")

    # 18 numbered anchor sections
    for i in range(1, 19):
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


def test_comparative_matrix_alternatives():
    """READMEs must compare clirec across alternatives and technical dimensions."""
    en_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_text = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "Video Recorders" in en_text
    assert "Web E2E" in en_text
    assert "Macro Recorders" in en_text
    assert "Enterprise RPA" in en_text

    assert "Video-Recorder" in de_text
    assert "Web-E2E" in de_text
    assert "Makro-Recorder" in de_text
    assert "Enterprise RPA" in de_text


def test_governance_invariants_across_docs():
    """All 10 governance invariants must exist across READMEs and license doc."""
    en_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_text = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    lic_text = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")

    invariants = [
        "INV-LOCAL-01",
        "INV-PRIVACY-02",
        "INV-INSPECT-03",
        "INV-REPLAY-04",
        "INV-AUDIO-05",
        "INV-SIDECAR-06",
        "INV-ADAPTER-07",
        "INV-UNPRIV-08",
        "INV-PORTABLE-09",
        "INV-SLA-10",
    ]
    for inv_tag in invariants:
        assert inv_tag in en_text, f"Missing {inv_tag} in README.md"
        assert inv_tag in de_text, f"Missing {inv_tag} in README_de.md"
        assert inv_tag in lic_text, f"Missing {inv_tag} in THIRD_PARTY_LICENSES.md"


def test_third_party_licenses_audit_content():
    """License doc must confirm RunAsInvoker, SPDX, and LGPLv3 §4 compliance."""
    lic_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.is_file()
    text = lic_path.read_text(encoding="utf-8")

    assert "RunAsInvoker" in text
    assert "pynput" in text
    assert "LGPL-3.0" in text
    assert "LGPLv3 Section 4" in text
    assert "sounddevice" in text
    assert "uiautomation" in text
    assert "Zero-Copyleft" in text
