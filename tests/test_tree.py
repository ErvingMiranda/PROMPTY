import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))

from utils.helpers import generar_arbol


def test_generar_arbol_gitignore(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")

    pkg = root / "pkg"
    pkg.mkdir()
    cache = pkg / "__pycache__"
    cache.mkdir()
    (cache / "mod.pyc").write_text("x", encoding="utf-8")
    (pkg / "main.py").write_text("print('hi')", encoding="utf-8")

    lines = generar_arbol(pkg)
    joined = "\n".join(lines)
    assert "__pycache__" not in joined
    assert "mod.pyc" not in joined
    assert "main.py" in joined
