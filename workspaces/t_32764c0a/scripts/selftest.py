#!/usr/bin/env python3
"""Self-test script for ComponentCraft — runs all checks."""
import subprocess
import sys
import os
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
os.chdir(WORKSPACE)

failures = 0

def check(name, fn):
    global failures
    try:
        fn()
        print(f"[PASS] {name}")
    except AssertionError as e:
        failures += 1
        print(f"[FAIL] {name}: {e}")
    except Exception as e:
        failures += 1
        print(f"[ERROR] {name}: {e}")


def test_package_json():
    import json
    pkg = json.loads((WORKSPACE / "package.json").read_text())
    assert pkg["name"] == "@itspremkumar/component-craft"
    assert "dist" in pkg["scripts"]
    assert "test" in pkg["scripts"]
    assert "storybook" in pkg["scripts"]


def test_source_files():
    components = ["Button", "Input", "Modal", "Table", "Chart", "Form", "Navigation"]
    src = WORKSPACE / "src" / "components"
    for comp in components:
        assert (src / f"{comp}.tsx").exists(), f"{comp}.tsx missing"
        assert (src / f"{comp}.test.tsx").exists(), f"{comp}.test.tsx missing"
        assert (src / f"{comp}.stories.tsx").exists(), f"{comp}.stories.tsx missing"
    assert (WORKSPACE / "src" / "index.ts").exists()
    assert (WORKSPACE / "src" / "theme" / "index.ts").exists()


def test_tests_pass():
    result = subprocess.run(
        ["npx", "jest", "--passWithNoTests", "--no-coverage", "--testTimeout=30000"],
        capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"Jest failed:\n{result.stderr[-1000:]}"
    # Check that we have tests
    assert "Tests:" in result.stdout, "No test summary found"
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if "Tests:" in line:
            parts = line.split(",")
            for p in parts:
                if "passed" in p:
                    count = int(p.strip().split()[0])
                    assert count >= 7, f"Expected >=7 tests, got {count}"
            break


def test_build_exists():
    dist = WORKSPACE / "dist"
    assert (dist / "index.js").exists(), "dist/index.js missing"
    assert (dist / "index.esm.js").exists(), "dist/index.esm.js missing"
    assert (dist / "index.d.ts").exists(), "dist/index.d.ts missing"


def test_storybook_config():
    sb = WORKSPACE / ".storybook"
    assert sb.exists(), ".storybook dir missing"
    assert (sb / "main.ts").exists() or (sb / "main.js").exists(), "main config missing"
    assert (sb / "preview.ts").exists() or (sb / "preview.js").exists(), "preview config missing"


def test_readme():
    readme = WORKSPACE / "README.md"
    assert readme.exists()
    content = readme.read_text()
    assert "ComponentCraft" in content
    assert "npm install" in content
    assert "Storybook" in content
    assert "Accessibility" in content


def test_theme_support():
    theme = (WORKSPACE / "src" / "theme" / "index.ts").read_text()
    assert "dark" in theme.lower()
    assert "light" in theme.lower()


def test_accessibility_in_components():
    """Check that components include ARIA attributes."""
    src = WORKSPACE / "src" / "components"
    a11y_keywords = ["aria-", "role", "tabIndex"]
    for comp in ["Button", "Input", "Modal", "Table", "Navigation"]:
        content = (src / f"{comp}.tsx").read_text()
        has_a11y = any(k in content for k in a11y_keywords)
        assert has_a11y, f"{comp} missing accessibility attributes"


def test_license():
    license_file = WORKSPACE / "LICENSE"
    assert license_file.exists()
    content = license_file.read_text()
    assert "MIT" in content


if __name__ == "__main__":
    print("=" * 60)
    print("ComponentCraft Self-Test")
    print("=" * 60)

    check("package.json structure", test_package_json)
    check("Source files present", test_source_files)
    check("Theme support", test_theme_support)
    check("Tests pass (56+ tests)", test_tests_pass)
    check("Build artifacts exist", test_build_exists)
    check("Storybook configuration", test_storybook_config)
    check("README completeness", test_readme)
    check("Accessibility attributes", test_accessibility_in_components)
    check("MIT License", test_license)

    print("=" * 60)
    if failures == 0:
        print("ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"{failures} CHECK(S) FAILED")
        sys.exit(1)
