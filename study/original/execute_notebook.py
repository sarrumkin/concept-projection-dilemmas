"""Execute notebooks in fresh kernels using the invoking Python environment."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def execute(path: Path, timeout=1800):
    with tempfile.TemporaryDirectory(prefix="concept-kernels-") as directory:
        kernel_dir = Path(directory) / "concept-research"
        kernel_dir.mkdir()
        (kernel_dir / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Concept Layers Research", "language": "python"}))
        manager = KernelManager(kernel_name="concept-research",
                                kernel_spec_manager=KernelSpecManager(kernel_dirs=[directory]))
        notebook = nbformat.read(path, as_version=4)
        client = NotebookClient(notebook, timeout=timeout, km=manager,
                                resources={"metadata": {"path": str(path.parent)}}, allow_errors=False)
        client.execute()
        nbformat.validate(notebook)
        assert not any(o.output_type == "error" for c in notebook.cells if c.cell_type == "code" for o in c.outputs)
        nbformat.write(notebook, path)
        print(f"Executed {path.name}: {sum(c.cell_type == 'code' for c in notebook.cells)} code cells", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", type=Path)
    args = parser.parse_args()
    files = args.notebooks or [Path(__file__).parent / '09_english_240_triplets.ipynb']
    if not files:
        raise SystemExit("No notebooks found")
    for path in files:
        execute(path.resolve())
