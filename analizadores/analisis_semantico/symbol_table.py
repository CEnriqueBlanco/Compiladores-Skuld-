from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Symbol:
    """
    Entrada individual en la Tabla de Símbolos.
    Registra toda la información semántica requerida por la Fase 3:
    - Nombre o lexema del identificador
    - Tipo de dato ('worldline', 'divergence', 'reading', 'void', 'string')
    - Ámbito (scope) donde fue declarado (ej. 'global', 'duplicar', 'gate')
    - Desplazamiento o dirección de memoria relativa (offset)
    - Línea de declaración y lista de líneas de aparición (declaración + usos)
    - Atributos adicionales (si es función, sus parámetros, valor constante conocido, etc.)
    """
    name: str
    data_type: str
    scope_name: str
    scope_level: int
    memory_loc: int
    declaration_line: int
    lines: List[int] = field(default_factory=list)
    is_function: bool = False
    param_types: List[str] = field(default_factory=list)
    constant_val: Optional[Any] = None

    def add_reference(self, lineno: int) -> None:
        """Registra una línea donde el símbolo fue utilizado o referenciado."""
        if lineno not in self.lines:
            self.lines.append(lineno)


class Scope:
    """
    Representa un entorno o ámbito léxico concreto (bloque, función o global).
    Permite anidamiento mediante referencia al scope padre (parent).
    """
    def __init__(self, name: str, level: int = 0, parent: Optional[Scope] = None):
        self.name: str = name
        self.level: int = level
        self.parent: Optional[Scope] = parent
        self.symbols: Dict[str, Symbol] = {}

    def insert(self, symbol: Symbol) -> bool:
        """Inserta un símbolo en el ámbito actual. Retorna False si ya existe en este mismo ámbito."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Busca el identificador únicamente en el ámbito actual."""
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca el identificador recursivamente en el ámbito actual y sus ancestros."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


class SymbolTable:
    """
    Tabla de Símbolos jerárquica con soporte de scopes anidados,
    cálculo de desplazamientos de memoria (offsets) y seguimiento de referencias.
    """
    # Mapeo de tamaños en bytes para cada tipo de dato básico
    TYPE_SIZES: Dict[str, int] = {
        "worldline": 4,   # int -> 4 bytes
        "int": 4,
        "divergence": 8,  # float -> 8 bytes
        "float": 8,
        "real": 8,
        "reading": 1,     # bool -> 1 byte
        "bool": 1,
        "string": 16,     # pointer/descriptor -> 16 bytes
        "void": 0
    }

    def __init__(self):
        self.global_scope = Scope("global", level=0)
        self.current_scope: Scope = self.global_scope
        self.all_symbols: List[Symbol] = []
        
        # Desplazamientos de memoria independientes para datos globales y marcos de pila
        self.current_offset: int = 0
        self.scope_level: int = 0

    def enter_scope(self, name: str) -> Scope:
        """Crea y entra a un nuevo ámbito anidado."""
        self.scope_level += 1
        new_scope = Scope(name=name, level=self.scope_level, parent=self.current_scope)
        self.current_scope = new_scope
        return new_scope

    def exit_scope(self) -> Optional[Scope]:
        """Sale del ámbito actual regresando al ámbito padre."""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent
            self.scope_level -= 1
        return self.current_scope

    def insert(
        self,
        name: str,
        data_type: str,
        line: int,
        is_function: bool = False,
        param_types: Optional[List[str]] = None,
        constant_val: Optional[Any] = None
    ) -> tuple[bool, Optional[Symbol]]:
        """
        Inserta un nuevo símbolo en el ámbito actual calculando su offset de memoria.
        Retorna (True, symbol) si se insertó con éxito,
        o (False, existing_symbol) si ya existía duplicado en el mismo ámbito.
        """
        existing = self.current_scope.lookup_current(name)
        if existing is not None:
            return False, existing

        size = self.TYPE_SIZES.get(data_type.lower(), 4)
        mem_loc = self.current_offset
        self.current_offset += size

        symbol = Symbol(
            name=name,
            data_type=data_type,
            scope_name=self.current_scope.name,
            scope_level=self.current_scope.level,
            memory_loc=mem_loc,
            declaration_line=line,
            lines=[line],
            is_function=is_function,
            param_types=param_types or [],
            constant_val=constant_val
        )

        self.current_scope.insert(symbol)
        self.all_symbols.append(symbol)
        return True, symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca el identificador en el scope actual y ámbitos padres."""
        return self.current_scope.lookup(name)

    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Busca el identificador únicamente en el ámbito actual."""
        return self.current_scope.lookup_current(name)

    def format_table(self) -> str:
        """
        Genera una representación tabular estética de la Tabla de Símbolos,
        conforme a las especificaciones requeridas por el proyecto y la docente.
        """
        if not self.all_symbols:
            return "(Tabla de símbolos vacía)"

        headers = ["Nombre", "Tipo", "Ámbito", "Nivel", "Dirección/Offset", "Líneas"]
        rows = []
        for sym in self.all_symbols:
            type_display = sym.data_type
            if sym.is_function:
                params_str = ", ".join(sym.param_types)
                type_display = f"func({params_str}) -> {sym.data_type}"

            lines_str = ", ".join(str(l) for l in sorted(sym.lines))
            rows.append([
                sym.name,
                type_display,
                sym.scope_name,
                str(sym.scope_level),
                f"0x{sym.memory_loc:04X} ({sym.memory_loc})",
                lines_str
            ])

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        sep_line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        header_line = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"

        result = [sep_line, header_line, sep_line]
        for row in rows:
            row_line = "|" + "|".join(f" {row[i].ljust(col_widths[i])} " for i in range(len(row))) + "|"
            result.append(row_line)
        result.append(sep_line)

        return "\n".join(result)
