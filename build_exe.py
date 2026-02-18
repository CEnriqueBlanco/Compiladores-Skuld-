from __future__ import annotations

import subprocess
from pathlib import Path


def build() -> int:
    project_root = Path(__file__).resolve().parent
    icon_path = project_root / "resources" / "icons" / "logo.ico"
    main_path = project_root / "ide" / "main.py"

    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        "ReadingSteiner",
    ]

    if icon_path.exists():
        command.extend(["--icon", str(icon_path)])

    command.append(str(main_path))

    print("Ejecutando:", " ".join(command))
    result = subprocess.run(command, cwd=project_root, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(build())
