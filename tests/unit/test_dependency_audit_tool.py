"""Tests for the dependency audit agent tool."""

from pathlib import Path

import pytest

from agent.tools.dependency_audit_tool import DependencyAuditTool

pytestmark = pytest.mark.unit
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "dependency_audit"


def test_flags_vite_and_vitest_but_skips_adjacent_major():
    """Reproduce the missed Vite and Vitest findings with fixed current releases."""
    current = {"vite": "8.0.0", "vitest": "5.0.0", "react": "19.0.0"}
    tool = DependencyAuditTool(latest_version=lambda ecosystem, name: current[name])
    result = tool.execute(
        {"manifests": {"frontend/package.json": (FIXTURES / "package.json").read_text()}}
    )

    assert result.success
    assert result.data["warnings"] == []
    assert result.data["findings"] == [
        {
            "ecosystem": "npm",
            "package": "vite",
            "manifest": "frontend/package.json",
            "specifier": "^5.0.0",
            "highest_allowed_major": 5,
            "latest_version": "8.0.0",
            "major_gap": 3,
        },
        {
            "ecosystem": "npm",
            "package": "vitest",
            "manifest": "frontend/package.json",
            "specifier": "^1.0.0",
            "highest_allowed_major": 1,
            "latest_version": "5.0.0",
            "major_gap": 4,
        },
    ]


@pytest.mark.parametrize(
    "declaration, expected_bound",
    [
        ("example[extra]==1.2.3", 1),
        ("example==1.*", 1),
        ("example~=2.4.0", 2),
        ("example>=3,<5", 4),
        ("example>=3,<=5.0", 5),
        ("example>=3", None),
        ("example>=6,<5", None),
    ],
)
def test_python_requirements_use_the_range_ceiling(declaration, expected_bound):
    """Find the highest allowed major for common Python version constraints."""
    tool = DependencyAuditTool(latest_version=lambda ecosystem, name: "8.0.0")
    result = tool.execute({"manifests": {"requirements.txt": f"# deps\n{declaration} # test\n"}})
    assert result.success
    if expected_bound is None:
        assert result.data["findings"] == []
    else:
        [finding] = result.data["findings"]
        assert finding["highest_allowed_major"] == expected_bound
        assert finding["major_gap"] == 8 - expected_bound


def test_pyproject_groups_share_package_lookups():
    """Check direct and optional dependencies and reuse a lookup within a run."""
    calls = []

    def current_version(ecosystem, name):
        calls.append((ecosystem, name))
        return "6.0.0"

    tool = DependencyAuditTool(latest_version=current_version)
    content = """
[project]
dependencies = ["Example_Name>=3,<5", "redis>=5"]
[project.optional-dependencies]
dev = ["example-name==3.0.0"]
"""
    result = tool.execute({"manifests": {"pyproject.toml": content}})

    assert calls == [("pypi", "example-name")]
    assert [finding["major_gap"] for finding in result.data["findings"]] == [2, 3]


def test_registry_failures_and_bad_manifests_preserve_other_results():
    """Return findings alongside warnings when some inputs cannot be checked."""

    def current_version(ecosystem, name):
        if name == "missing":
            return None
        return "4.0.0"

    tool = DependencyAuditTool(latest_version=current_version)
    result = tool.execute(
        {
            "manifests": {
                "bad/package.json": "{",
                "requirements.txt": "missing==1.0\nworking==1.0",
                "frontend/package.json": '{"dependencies":{"@scope/lib":"~1.2.3","x":"file:local"}}',
            }
        }
    )
    assert result.success
    assert [finding["package"] for finding in result.data["findings"]] == ["working", "@scope/lib"]
    assert len(result.data["warnings"]) == 3
    for name in ("bad/package.json", "missing", "x"):
        assert any(name in warning for warning in result.data["warnings"])


def test_registry_lookup_uses_stable_releases(monkeypatch):
    """Use npm latest and skip prereleases and yanked releases on PyPI."""
    import httpx

    def registry_get(url, *, timeout):
        request = httpx.Request("GET", url)
        if request.url.host == "pypi.org":
            assert request.url.path == "/pypi/example/json"
            fixture = "pypi.json"
        else:
            assert request.url.host == "registry.npmjs.org"
            assert request.url.raw_path == b"/%40scope%2Flib/latest"
            fixture = "npm.json"
        return httpx.Response(200, content=(FIXTURES / fixture).read_bytes(), request=request)

    monkeypatch.setattr(httpx, "get", registry_get)
    result = DependencyAuditTool().execute(
        {
            "manifests": {
                "requirements.txt": "example==1.0",
                "package.json": '{"dependencies":{"@scope/lib":"^5.0.0"}}',
            }
        }
    )
    assert result.data["warnings"] == []
    assert [finding["latest_version"] for finding in result.data["findings"]] == [
        "4.3.0",
        "8.0.0",
    ]
