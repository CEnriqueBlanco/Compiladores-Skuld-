from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget


class AnalysisPanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        self._tokens = self._make_output("Tokens léxicos aparecerán aquí.")
        self._syntax = self._make_output("Árbol sintáctico / salida estructurada.")
        self._semantic = self._make_output("Resultados semánticos y validaciones.")
        self._intermediate = self._make_output("Código intermedio (tres direcciones, etc.).")
        self._symbols = self._make_output("Tabla de símbolos.")

        self.addTab(self._tokens, "Tokens")
        self.addTab(self._syntax, "Sintáctico")
        self.addTab(self._semantic, "Semántico")
        self.addTab(self._intermediate, "Intermedio")
        self.addTab(self._symbols, "Símbolos")

    def set_tokens(self, text: str) -> None:
        self._tokens.setPlainText(text)

    def set_syntax(self, text: str) -> None:
        self._syntax.setPlainText(text)

    def set_semantic(self, text: str) -> None:
        self._semantic.setPlainText(text)

    def set_intermediate(self, text: str) -> None:
        self._intermediate.setPlainText(text)

    def set_symbols(self, text: str) -> None:
        self._symbols.setPlainText(text)

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output
