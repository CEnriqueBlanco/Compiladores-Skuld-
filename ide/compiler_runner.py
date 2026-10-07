from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from analizadores.analisis_lexico.skuld_lexer import LexicalError, tokenize_file_with_recovery


@dataclass
class CompilerResult:
    returncode: int
    stdout: str
    stderr: str
    error_line: int | None = None
    error_column: int | None = None
    error_column_end: int | None = None
    # Extra: para la fase semántica, separamos los contenidos del stdout
    semantic_tree: str = ""    # AST anotado (para pestaña Semántico)
    symbol_table: str = ""     # Tabla de símbolos formateada (para pestaña Símbolos)
    symbol_rows: list[list[str]] = field(default_factory=list)


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


def _locate_semantic_errors(source_path: str, errors) -> None:
    """Ajusta la columna de cada error semantico al lexema señalado."""
    try:
        with open(source_path, "r", encoding="utf-8") as source_file:
            source_lines = source_file.readlines()
    except OSError:
        return

    for error in errors:
        if not error.lexeme or not (1 <= error.line <= len(source_lines)):
            continue
        line_text = source_lines[error.line - 1]
        lexeme_column = line_text.find(error.lexeme)
        if lexeme_column >= 0:
            error.column = lexeme_column + 1


def _run_semantic_inline(source_path: str) -> CompilerResult:
    """
    Ejecuta el análisis semántico en proceso (sin subprocess) para poder
    separar el AST anotado de la Tabla de Símbolos y poblar pestañas independientes.
    """
    try:
        from analizadores.analisis_lexico.skuld_lexer import tokenize_file_with_recovery as tokenize
        from analizadores.analisis_sintactico.skuld_parser import SkuldParser
        from analizadores.analisis_semantico import SemanticAnalyzer, print_annotated_tree

        tokens, lex_errors = tokenize(source_path)
        if lex_errors:
            return CompilerResult(returncode=1, stdout="", stderr="\n".join(str(e) for e in lex_errors))

        parser = SkuldParser(tokens)
        ast = parser.parse()
        if parser.errors:
            return CompilerResult(returncode=1, stdout="", stderr="\n".join(str(e) for e in parser.errors))

        analyzer = SemanticAnalyzer()
        annotated_ast, symbol_table, sem_errors = analyzer.analyze(ast)
        _locate_semantic_errors(source_path, sem_errors)

        tree_text = print_annotated_tree(annotated_ast)
        symbols_text = symbol_table.format_table()
        symbol_rows = symbol_table.table_rows()

        errors_text = "\n".join(str(e) for e in sem_errors) if sem_errors else ""
        rc = 1 if sem_errors else 0

        # Extraer línea/columna del primer error semántico para resaltado en el editor
        error_line = None
        error_column = None
        error_column_end = None
        if sem_errors:
            first = sem_errors[0]
            error_line = first.line
            error_column = first.column
            lex_m = re.search(r" -> '(.*)'$", str(first).strip())
            span_len = max(1, len(lex_m.group(1)) if lex_m else 1)
            error_column_end = error_column + span_len - 1

        return CompilerResult(
            returncode=rc,
            stdout=tree_text,
            stderr=errors_text,
            error_line=error_line,
            error_column=error_column,
            error_column_end=error_column_end,
            semantic_tree=tree_text,
            symbol_table=symbols_text,
            symbol_rows=symbol_rows,
        )
    except Exception as exc:
        return CompilerResult(returncode=1, stdout="", stderr=f"Error interno en análisis semántico: {exc}")


def run_compiler(phase: str, source_path: str) -> CompilerResult:
    if phase == "lexico":
        return _format_lex_tokens(source_path)

    if phase == "semantico":
        return _run_semantic_inline(source_path)

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
