from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def build() -> int:
    project_root = Path(__file__).resolve().parent
    resources_path = project_root / "resources"
    icon_path = resources_path / "icons" / "icon.ico"
    main_path = project_root / "ide" / "main.py"
    spec_path = project_root / "build" / "spec"
    spec_path.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--specpath",
        str(spec_path),
        "--onefile",
        "--windowed",
        "--name",
        "ReadingSteiner",
        "--icon",
        str(icon_path),
        "--add-data",
        f"{resources_path}{os.pathsep}resources",
        "--collect-all",
        "qtawesome",
        "--hidden-import",
        "skuld_compiler",
        str(main_path),
    ]

    print("Ejecutando:", " ".join(command))
    result = subprocess.run(command, cwd=project_root, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(build())
