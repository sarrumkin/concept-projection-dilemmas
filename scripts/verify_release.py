"""Check the explicit release inventory, hashes, notebook and local doc links."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".venv", "artifacts", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"}


def verify():
    manifest = json.loads((ROOT / "release-manifest.json").read_text())
    allowlist = set((ROOT / "release-allowlist.txt").read_text().splitlines())
    assert allowlist == set(manifest["files"]) | {"release-manifest.json"}, "allowlist and manifest differ"
    for name, info in manifest["files"].items():
        path = ROOT / name
        assert path.is_file() and not path.is_symlink(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"], name
    found = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED for part in relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_file() or path.is_symlink():
            assert not path.is_symlink(), str(relative)
            found.add(relative.as_posix())
    assert found == allowlist, f"unlisted files: {sorted(found - allowlist)}; missing: {sorted(allowlist - found)}"

    notebook = json.loads((ROOT / "notebooks/research.ipynb").read_text())
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code) == 5 and all(cell["execution_count"] is not None for cell in code)
    assert not any(out["output_type"] == "error" for cell in code for out in cell["outputs"])
    assert sum("image/png" in out.get("data", {}) for cell in code for out in cell["outputs"]) == 3
    markdown = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "markdown")
    assert "Primary hypothesis H1:** Concept207" in markdown
    assert "Secondary hypothesis H2:** Hybrid50" in markdown

    for path in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]:
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            assert target.is_relative_to(ROOT) and target.exists(), f"broken local link in {path.name}: {link}"
    print(f"Release inventory verified: {len(allowlist)} files; hashes, executed notebook and local documentation links match.")


if __name__ == "__main__":
    verify()
