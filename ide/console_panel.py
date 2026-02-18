from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget


class ConsolePanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        self._console = self._make_output("Bienvenido a Reading Steiner IDE\nEl Psy Kongroo\nListo para compilar...")
        self._errors = self._make_output("Errores léxicos, sintácticos y semánticos aparecerán aquí.")
        self._execution = self._make_output("Salida de ejecución del programa compilado.")

        self.addTab(self._console, "Consola")
        self.addTab(self._errors, "Errores")
        self.addTab(self._execution, "Ejecución")

    def append_console(self, text: str) -> None:
        self._console.appendPlainText(text)

    def append_errors(self, text: str) -> None:
        self._errors.appendPlainText(text)

    def append_execution(self, text: str) -> None:
        self._execution.appendPlainText(text)

    def clear_all(self) -> None:
        self._console.clear()
        self._errors.clear()
        self._execution.clear()

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output
