#!/usr/bin/env python3
import sys
import os

from analizadores.analisis_lexico.skuld_lexer import tokenize_file_with_recovery, LexicalError
from analizadores.analisis_sintactico.skuld_parser import SkuldParser, print_tree_graphical, SyntaxError


def print_usage():
    print("Uso: python skuld_compiler.py [FASE] <archivo_fuente>")
    print("Fases:")
    print("  --lexico       Ejecuta la fase de análisis léxico")
    print("  --sintactico   Ejecuta la fase de análisis sintáctico")
    sys.exit(1)


def run_lexical(source_path: str):
    if not os.path.exists(source_path):
        print(f"Error: El archivo no existe: {source_path}", file=sys.stderr)
        sys.exit(1)

    tokens, errors = tokenize_file_with_recovery(source_path)

    if errors:
        for err in errors:
            print(str(err), file=sys.stderr)
        sys.exit(1)

    for tok in tokens:
        if tok.token_type != "ENDFILE":
            print(f"[{tok.token_type}:{tok.lexeme!r}] @ {tok.line}:{tok.column_start}-{tok.column_end}")
    sys.exit(0)


def try_parse_token_file(file_path: str) -> list[Token] | None:
    import re
    # Formato esperado: [TIPO_TOKEN:'lexema'] @ linea:col_inicio-col_fin
    token_re = re.compile(r"^\[(?P<type>[A-Z_0-9]+):(?P<lex>.*)\] @ (?P<line>\d+):(?P<col_start>\d+)-(?P<col_end>\d+)$")
    tokens = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            return None
            
        has_token_format = False
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str == "TOKENS RECONOCIDOS:" or line_str.startswith("ERRORES LEXICOS:") or line_str.startswith("ERRORES LEXICOS:"):
                has_token_format = True
                continue
            match = token_re.match(line_str)
            if match:
                has_token_format = True
                
        if not has_token_format:
            return None
            
        from analizadores.analisis_lexico.skuld_lexer import Token
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str == "TOKENS RECONOCIDOS:" or line_str.startswith("ERRORES LEXICOS:") or line_str.startswith("(ninguno)"):
                continue
            match = token_re.match(line_str)
            if match:
                ttype = match.group("type")
                lex = match.group("lex")
                
                # Quitar comillas exteriores
                if (lex.startswith("'") and lex.endswith("'")) or (lex.startswith('"') and lex.endswith('"')):
                    lex = lex[1:-1]
                
                # Desescapar secuencias unicode como \n, \t
                try:
                    lex = bytes(lex, "utf-8").decode("unicode_escape")
                except Exception:
                    pass
                    
                tokens.append(Token(
                    token_type=ttype,
                    lexeme=lex,
                    line=int(match.group("line")),
                    column_start=int(match.group("col_start")),
                    column_end=int(match.group("col_end"))
                ))
        if tokens:
            last = tokens[-1]
            tokens.append(Token("ENDFILE", "", last.line, last.column_end, last.column_end))
        return tokens
    except Exception:
        return None


def run_syntax(source_path: str):
    if not os.path.exists(source_path):
        print(f"Error: El archivo no existe: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Requisito 1: Intentar leer directamente desde un archivo de tokens
    tokens = try_parse_token_file(source_path)
    
    if tokens is None:
        # Si no tiene el formato de tokens, asumimos que es código fuente y lo tokenizamos sobre la marcha
        tokens, lex_errors = tokenize_file_with_recovery(source_path)
        if lex_errors:
            for err in lex_errors:
                print(str(err), file=sys.stderr)
            sys.exit(1)

    # 2. Analizar sintácticamente los tokens (Requisito 2: Construir el AST)
    parser = SkuldParser(tokens)
    ast = parser.parse()

    # 3. Reportar cualquier error sintáctico (Requisito 4)
    if parser.errors:
        for err in parser.errors:
            print(str(err), file=sys.stderr)
        sys.exit(1)

    # 4. Imprimir la visualización gráfica de carpeta del AST (Requisito 3)
    ast_tree_visual = print_tree_graphical(ast)
    print(ast_tree_visual)
    sys.exit(0)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for Python versions where reconfigure is not available
        pass

    if len(sys.argv) < 3:
        print_usage()

    phase = sys.argv[1]
    source_path = sys.argv[2]

    if phase == "--lexico":
        run_lexical(source_path)
    elif phase == "--sintactico":
        run_syntax(source_path)
    else:
        # Fallback to standard CLI parameters or single file
        # If they just pass a file without arguments, default to syntactic
        if os.path.exists(phase):
            run_syntax(phase)
        else:
            print(f"Error: Argumento o fase no reconocida: {phase}", file=sys.stderr)
            print_usage()


if __name__ == "__main__":
    main()
