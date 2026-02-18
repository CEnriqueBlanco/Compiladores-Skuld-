from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class CompilerResult:
    returncode: int
    stdout: str
    stderr: str


PHASE_ARGS = {
    "lexico": "--lexico",
    "sintactico": "--sintactico",
    "semantico": "--semantico",
    "intermedio": "--intermedio",
    "ejecucion": "--ejecutar",
}


def _get_compiler_command() -> List[str] | None:
    env_command = os.getenv("SKULD_COMPILER_CMD")
    if env_command:
        return shlex.split(env_command)
    return None


def run_compiler(phase: str, source_path: str) -> CompilerResult:
    command = _get_compiler_command()
    if not command:
        return CompilerResult(
            returncode=1,
            stdout="",
            stderr=(
                "No se encontró comando del compilador. "
                "Define la variable de entorno SKULD_COMPILER_CMD."
            ),
        )

    phase_arg = PHASE_ARGS.get(phase, "")
    full_command = [*command, phase_arg, source_path] if phase_arg else [*command, source_path]
    result = subprocess.run(
        full_command,
        capture_output=True,
        text=True,
        check=False,
    )
    return CompilerResult(result.returncode, result.stdout, result.stderr)
