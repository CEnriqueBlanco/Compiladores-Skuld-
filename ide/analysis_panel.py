from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget


class AnalysisPanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        tokens = self._make_output("Tokens léxicos aparecerán aquí.")
        syntax = self._make_output("Árbol sintáctico / salida estructurada.")
        semantic = self._make_output("Resultados semánticos y validaciones.")
        intermediate = self._make_output("Código intermedio (tres direcciones, etc.).")
        symbols = self._make_output("Tabla de símbolos.")

        self.addTab(tokens, "Tokens")
        self.addTab(syntax, "Sintáctico")
        self.addTab(semantic, "Semántico")
        self.addTab(intermediate, "Intermedio")
        self.addTab(symbols, "Símbolos")

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output
