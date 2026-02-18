from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget


class ConsolePanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        console = self._make_output("Bienvenido a Reading Steiner IDE\nEl Psy Kongroo\nListo para compilar...")
        errors = self._make_output("No hay errores.\n")
        ast = self._make_output("AST preview no disponible en esta entrega.")

        self.addTab(console, "Consola")
        self.addTab(errors, "Errores")
        self.addTab(ast, "AST")

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output
