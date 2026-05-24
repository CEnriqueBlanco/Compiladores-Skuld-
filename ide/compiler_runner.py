from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import List

from analizadores.analisis_lexico.skuld_lexer import LexicalError, tokenize_file_with_recovery


@dataclass
class CompilerResult:
    returncode: int
    stdout: str
    stderr: str
    error_line: int | None = None
    error_column: int | None = None
    error_column_end: int | None = None


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
    
    # Fallback automático al skuld_compiler.py del proyecto root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compiler_path = os.path.join(root_dir, "skuld_compiler.py")
    if os.path.exists(compiler_path):
        return [sys.executable, compiler_path]
    return None


def _format_lex_tokens(source_path: str) -> CompilerResult:
    try:
        tokens, errors = tokenize_file_with_recovery(source_path)
    except OSError as exc:
        return CompilerResult(returncode=1, stdout="", stderr=f"No se pudo leer el archivo: {exc}")

    # Si hay errores, reportar el primero
    if errors:
        exc = errors[0]
        raw_lexeme = exc.lexeme or ""
        # Highlight up to the first line of the invalid lexeme; fallback to one character.
        first_line_lexeme = raw_lexeme.splitlines()[0] if raw_lexeme else ""
        span_len = max(1, len(first_line_lexeme))
        return CompilerResult(
            returncode=1,
            stdout="",
            stderr=str(exc),
            error_line=exc.line,
            error_column=exc.column,
            error_column_end=exc.column + span_len - 1,
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

    import re
    phase_arg = PHASE_ARGS.get(phase, "")
    full_command = [*command, phase_arg, source_path] if phase_arg else [*command, source_path]
    result = subprocess.run(
        full_command,
        capture_output=True,
        check=False,
    )

    # Decodificar de forma robusta con fallback en caso de error
    stdout_decoded = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr_decoded = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    error_line = None
    error_column = None
    error_column_end = None

    if result.returncode != 0 and stderr_decoded:
        match = re.search(r"ERROR_SINTACTICO\((\d+),\s*(\d+)\): (.*)", stderr_decoded)
        if match:
            error_line = int(match.group(1))
            error_column = int(match.group(2))
            
            lex_match = re.search(r" -> '(.*)'$", stderr_decoded.strip())
            span_len = 1
            if lex_match:
                span_len = max(1, len(lex_match.group(1).splitlines()[0] if lex_match.group(1) else ""))
            error_column_end = error_column + span_len - 1

    return CompilerResult(
        result.returncode,
        stdout_decoded,
        stderr_decoded,
        error_line=error_line,
        error_column=error_column,
        error_column_end=error_column_end,
    )
