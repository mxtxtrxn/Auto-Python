"""Pruebas de los recursos de impresion."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = sorted((ROOT / "templates").glob("*.html"))
STYLES = sorted((ROOT / "styles").glob("*.css"))


def test_templates_exist() -> None:
    names = {path.name for path in TEMPLATES}
    assert "standard_template.html" in names
    assert "compact_template.html" in names
    assert "rack_template.html" in names


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda path: path.name)
def test_templates_include_qr_placeholder(template: Path) -> None:
    content = template.read_text(encoding="utf-8")
    assert "label_tools.qr_code(sample_id)" in content


def test_styles_exist() -> None:
    assert len(STYLES) >= 4
    for style in STYLES:
        assert "@page" in style.read_text(encoding="utf-8")
