from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget


class ConsolePanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        console = self._make_output("Bienvenido a Reading Steiner IDE\nEl Psy Kongroo\nListo para compilar...")
        errors = self._make_output("Errores léxicos, sintácticos y semánticos aparecerán aquí.")
        execution = self._make_output("Salida de ejecución del programa compilado.")

        self.addTab(console, "Consola")
        self.addTab(errors, "Errores")
        self.addTab(execution, "Ejecución")

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output
