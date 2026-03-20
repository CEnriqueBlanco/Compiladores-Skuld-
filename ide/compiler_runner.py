from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import List

from skuld_lexer import LexicalError, tokenize_file


@dataclass
class CompilerResult:
    returncode: int
    stdout: str
    stderr: str
    error_line: int | None = None
    error_column: int | None = None


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


def _format_lex_tokens(source_path: str) -> CompilerResult:
    try:
        tokens = tokenize_file(source_path)
    except OSError as exc:
        return CompilerResult(returncode=1, stdout="", stderr=f"No se pudo leer el archivo: {exc}")
    except LexicalError as exc:
        return CompilerResult(
            returncode=1,
            stdout="",
            stderr=str(exc),
            error_line=exc.line,
            error_column=exc.column,
        )

    lines = [
        f"[{tok.token_type}:{tok.lexeme!r}] @ {tok.line}:{tok.column_start}-{tok.column_end}"
        for tok in tokens
    ]
    return CompilerResult(returncode=0, stdout="\n".join(lines), stderr="")


def run_compiler(phase: str, source_path: str) -> CompilerResult:
    if phase == "lexico":
        return _format_lex_tokens(source_path)

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
