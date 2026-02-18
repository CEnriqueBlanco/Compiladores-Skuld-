from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QCloseEvent, QFont, QKeySequence, QTextCursor
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QTabWidget,
    QToolButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ide.analysis_panel import AnalysisPanel
from ide.code_editor import CodeEditor
from ide.compiler_runner import run_compiler
from ide.console_panel import ConsolePanel
from ide.file_explorer import FileExplorer


class MainWindow(QMainWindow):
    _MAX_QT_SIZE = 16777215

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reading Steiner IDE v1.0")
        self.resize(1200, 800)

        self._status = QStatusBar(self)
        self._settings = QSettings("Skuld", "ReadingSteinerIDE")
        self._editor_tabs: QTabWidget | None = None
        self._analysis_panel: AnalysisPanel | None = None
        self._console_panel: ConsolePanel | None = None
        self._file_explorer: FileExplorer | None = None
        self._analysis_container: QWidget | None = None
        self._console_container: QWidget | None = None
        self._analysis_minimized = False
        self._console_minimized = False
        self._top_splitter: QSplitter | None = None
        self._main_splitter: QSplitter | None = None
        self._top_sizes_before_analysis_toggle: list[int] | None = None
        self._main_sizes_before_console_toggle: list[int] | None = None
        self._top_sizes_before_explorer_toggle: list[int] | None = None
        self._untitled_counter = 1

        self._build_menu()
        self._build_toolbar()
        self._build_status_bar()
        self._build_layout()

    def _build_menu(self) -> None:
        menu_file = self.menuBar().addMenu("Archivo")
        menu_edit = self.menuBar().addMenu("Editar")
        menu_build = self.menuBar().addMenu("Compilar")
        menu_help = self.menuBar().addMenu("Ayuda")

        action_new = QAction("Nuevo", self)
        action_open = QAction("Abrir", self)
        action_open_folder = QAction("Abrir Carpeta", self)
        action_close = QAction("Cerrar", self)
        action_save = QAction("Guardar", self)
        action_save_as = QAction("Guardar Como", self)
        action_find = QAction("Buscar", self)
        action_toggle_analysis = QAction("Alternar Analizadores", self)
        action_toggle_terminal = QAction("Alternar Terminal", self)
        action_toggle_explorer = QAction("Alternar Árbol de archivos", self)
        action_adjust_layout = QAction("Ajustar layout al contenido", self)
        action_exit = QAction("Salir", self)

        action_new.setShortcut(QKeySequence("Ctrl+N"))
        action_open_folder.setShortcut(QKeySequence("Ctrl+O"))
        action_save.setShortcut(QKeySequence("Ctrl+S"))
        action_save_as.setShortcut(QKeySequence("Ctrl+G"))
        action_find.setShortcut(QKeySequence("Ctrl+F"))
        action_toggle_analysis.setShortcut(QKeySequence("Ctrl+1"))
        action_toggle_terminal.setShortcut(QKeySequence("Ctrl+2"))
        action_toggle_explorer.setShortcut(QKeySequence("Ctrl+3"))
        action_adjust_layout.setShortcut(QKeySequence("Ctrl+Alt+A"))

        action_new.triggered.connect(self._new_file)
        action_open.triggered.connect(self._open_file)
        action_open_folder.triggered.connect(self._open_folder)
        action_close.triggered.connect(self._close_file)
        action_save.triggered.connect(self._save_file)
        action_save_as.triggered.connect(self._save_file_as)
        action_find.triggered.connect(self._find_in_code)
        action_toggle_analysis.triggered.connect(self._toggle_analysis_panel)
        action_toggle_terminal.triggered.connect(self._toggle_terminal_panel)
        action_toggle_explorer.triggered.connect(self._toggle_explorer_panel)
        action_adjust_layout.triggered.connect(self._fit_editor_to_content)
        action_exit.triggered.connect(self.close)

        menu_file.addAction(action_new)
        menu_file.addAction(action_open)
        menu_file.addAction(action_open_folder)
        menu_file.addAction(action_close)
        menu_file.addSeparator()
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addSeparator()
        menu_file.addAction(action_exit)

        for label in ["Deshacer", "Rehacer", "Copiar", "Pegar"]:
            menu_edit.addAction(QAction(label, self))
        menu_edit.addSeparator()
        menu_edit.addAction(action_find)
        menu_edit.addAction(action_toggle_analysis)
        menu_edit.addAction(action_toggle_terminal)
        menu_edit.addAction(action_toggle_explorer)
        menu_edit.addAction(action_adjust_layout)

        action_lex = QAction("Análisis Léxico", self)
        action_syn = QAction("Análisis Sintáctico", self)
        action_sem = QAction("Análisis Semántico", self)
        action_inter = QAction("Código Intermedio", self)
        action_exec = QAction("Ejecución", self)
        action_clear = QAction("Limpiar", self)

        action_lex.triggered.connect(lambda: self._run_phase("lexico"))
        action_syn.triggered.connect(lambda: self._run_phase("sintactico"))
        action_sem.triggered.connect(lambda: self._run_phase("semantico"))
        action_inter.triggered.connect(lambda: self._run_phase("intermedio"))
        action_exec.triggered.connect(lambda: self._run_phase("ejecucion"))
        action_clear.triggered.connect(self._clear_outputs)

        menu_build.addAction(action_lex)
        menu_build.addAction(action_syn)
        menu_build.addAction(action_sem)
        menu_build.addAction(action_inter)
        menu_build.addAction(action_exec)
        menu_build.addSeparator()
        menu_build.addAction(action_clear)

        for label in ["Documentación", "Acerca de"]:
            menu_help.addAction(QAction(label, self))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Herramientas", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        action_new = QAction(self.style().standardIcon(QStyle.SP_FileIcon), "Nuevo", self)
        action_open = QAction(self.style().standardIcon(QStyle.SP_DirOpenIcon), "Abrir", self)
        action_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Guardar", self)
        action_save_as = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Guardar como", self)
        action_find = QAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView), "Buscar", self)
        action_toggle_analysis = QAction(self.style().standardIcon(QStyle.SP_FileDialogDetailedView), "Alternar analizadores", self)
        action_toggle_terminal = QAction(self.style().standardIcon(QStyle.SP_ComputerIcon), "Alternar terminal", self)
        action_toggle_explorer = QAction(self.style().standardIcon(QStyle.SP_DirIcon), "Alternar árbol", self)
        action_lex = QAction(self.style().standardIcon(QStyle.SP_FileDialogInfoView), "Léxico", self)
        action_syn = QAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView), "Sintáctico", self)
        action_sem = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), "Semántico", self)
        action_inter = QAction(self.style().standardIcon(QStyle.SP_ComputerIcon), "Intermedio", self)
        action_exec = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Ejecución", self)

        action_new.setToolTip("Nuevo (Ctrl+N)")
        action_open.setToolTip("Abrir archivo")
        action_save.setShortcut(QKeySequence("Ctrl+S"))
        action_save.setToolTip("Guardar (Ctrl+S)")
        action_save_as.setShortcut(QKeySequence("Ctrl+G"))
        action_save_as.setToolTip("Guardar como (Ctrl+G)")
        action_find.setToolTip("Buscar (Ctrl+F)")
        action_toggle_analysis.setToolTip("Alternar analizadores (Ctrl+1)")
        action_toggle_terminal.setToolTip("Alternar terminal (Ctrl+2)")
        action_toggle_explorer.setToolTip("Alternar árbol de archivos (Ctrl+3)")
        action_lex.setToolTip("Análisis léxico")
        action_syn.setToolTip("Análisis sintáctico")
        action_sem.setToolTip("Análisis semántico")
        action_inter.setToolTip("Código intermedio")
        action_exec.setToolTip("Ejecución")

        action_new.triggered.connect(self._new_file)
        action_open.triggered.connect(self._open_file)
        action_save.triggered.connect(self._save_file)
        action_save_as.triggered.connect(self._save_file_as)
        action_find.triggered.connect(self._find_in_code)
        action_toggle_analysis.triggered.connect(self._toggle_analysis_panel)
        action_toggle_terminal.triggered.connect(self._toggle_terminal_panel)
        action_toggle_explorer.triggered.connect(self._toggle_explorer_panel)
        action_lex.triggered.connect(lambda: self._run_phase("lexico"))
        action_syn.triggered.connect(lambda: self._run_phase("sintactico"))
        action_sem.triggered.connect(lambda: self._run_phase("semantico"))
        action_inter.triggered.connect(lambda: self._run_phase("intermedio"))
        action_exec.triggered.connect(lambda: self._run_phase("ejecucion"))

        toolbar.addAction(action_new)
        toolbar.addAction(action_open)
        toolbar.addAction(action_save)
        toolbar.addAction(action_save_as)
        toolbar.addAction(action_find)
        toolbar.addSeparator()
        toolbar.addAction(action_toggle_analysis)
        toolbar.addAction(action_toggle_terminal)
        toolbar.addAction(action_toggle_explorer)
        toolbar.addSeparator()
        toolbar.addAction(action_lex)
        toolbar.addAction(action_syn)
        toolbar.addAction(action_sem)
        toolbar.addAction(action_inter)
        toolbar.addAction(action_exec)

    def _build_status_bar(self) -> None:
        self._status.showMessage("Lab Member 004 · El Psy Kongroo")
        self.setStatusBar(self._status)

    def _build_layout(self) -> None:
        self._editor_tabs = QTabWidget()
        self._editor_tabs.setFocusPolicy(Qt.StrongFocus)
        self._editor_tabs.setMinimumWidth(420)
        self._editor_tabs.setTabsClosable(True)
        self._editor_tabs.tabCloseRequested.connect(self._close_tab)
        self._editor_tabs.currentChanged.connect(self._on_tab_changed)

        self._file_explorer = FileExplorer()
        self._file_explorer.file_open_requested.connect(self._open_file_from_explorer)
        self._analysis_panel = AnalysisPanel()
        self._analysis_container = self._create_panel_container(
            "Analizadores",
            self._analysis_panel,
            on_toggle_minimize=self._toggle_analysis_minimize,
            on_close=self._close_analysis_panel,
        )

        self._top_splitter = QSplitter(Qt.Horizontal)
        self._top_splitter.setChildrenCollapsible(True)
        self._top_splitter.addWidget(self._file_explorer)
        self._top_splitter.addWidget(self._editor_tabs)
        self._top_splitter.addWidget(self._analysis_container)
        self._top_splitter.setStretchFactor(0, 1)
        self._top_splitter.setStretchFactor(1, 3)
        self._top_splitter.setStretchFactor(2, 1)
        self._top_splitter.setSizes([250, 700, 250])
        self._top_sizes_before_analysis_toggle = self._top_splitter.sizes()

        self._console_panel = ConsolePanel()
        self._console_container = self._create_panel_container(
            "Terminal",
            self._console_panel,
            on_toggle_minimize=self._toggle_console_minimize,
            on_close=self._close_console_panel,
        )

        self._main_splitter = QSplitter(Qt.Vertical)
        self._main_splitter.addWidget(self._top_splitter)
        self._main_splitter.addWidget(self._console_container)
        self._main_splitter.setStretchFactor(0, 3)
        self._main_splitter.setStretchFactor(1, 1)
        self._main_splitter.setSizes([620, 180])
        self._main_sizes_before_console_toggle = self._main_splitter.sizes()

        self.setCentralWidget(self._main_splitter)
        self._restore_session()

    def _bind_editor_events(self, editor: CodeEditor) -> None:
        editor.cursorPositionChanged.connect(self._update_cursor_status)

    def _fit_editor_to_content(self) -> None:
        if self._editor_tabs is None:
            return

        desired_width = 420
        for index in range(self._editor_tabs.count()):
            editor = self._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue

            text = editor.toPlainText()
            lines = text.splitlines() if text else [""]
            font_metrics = editor.fontMetrics()
            max_line_pixels = 0
            for line in lines:
                line_pixels = font_metrics.horizontalAdvance(line.expandtabs(4))
                if line_pixels > max_line_pixels:
                    max_line_pixels = line_pixels

            width_for_editor = max_line_pixels + editor.line_number_area_width() + 80
            if width_for_editor > desired_width:
                desired_width = width_for_editor

        desired_width = max(420, min(desired_width, 1600))
        self._editor_tabs.setMinimumWidth(desired_width)

        if self._top_splitter is None:
            return

        if self._analysis_container is not None and self._analysis_container.isVisible():
            self._top_splitter.setSizes([250, max(700, desired_width), 250])
        else:
            self._top_splitter.setSizes([250, max(700, desired_width), 0])

    def _create_panel_container(
        self,
        title: str,
        panel: QWidget,
        *,
        on_toggle_minimize,
        on_close,
    ) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget(container)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(6)

        title_label = QLabel(title)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        minimize_button = QToolButton(header)
        minimize_button.setText("_")
        minimize_button.setToolTip("Minimizar")
        minimize_button.clicked.connect(on_toggle_minimize)

        close_button = QToolButton(header)
        close_button.setText("✕")
        close_button.setToolTip("Cerrar")
        close_button.clicked.connect(on_close)

        header_layout.addWidget(minimize_button)
        header_layout.addWidget(close_button)

        panel.setObjectName(f"{title.lower()}_panel")

        layout.addWidget(header)
        layout.addWidget(panel, 1)
        return container

    def _find_in_code(self) -> None:
        editor = self._get_active_editor()
        if editor is None:
            return

        text, ok = QInputDialog.getText(self, "Buscar", "Texto a buscar:")
        if not ok or not text:
            return

        if editor.find(text):
            return

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
        if not editor.find(text):
            QMessageBox.information(self, "Buscar", f"No se encontró: {text}")

    def _close_console_panel(self) -> None:
        if self._console_container is None:
            return
        if self._main_splitter is not None:
            self._main_sizes_before_console_toggle = self._main_splitter.sizes()
        self._console_minimized = False
        self._console_container.setVisible(False)

    def _close_analysis_panel(self) -> None:
        if self._analysis_container is None:
            return
        if self._top_splitter is not None:
            self._top_sizes_before_analysis_toggle = self._top_splitter.sizes()
        self._analysis_minimized = False
        self._analysis_container.setVisible(False)
        if self._top_splitter is not None:
            current_sizes = self._top_splitter.sizes()
            left = current_sizes[0] if len(current_sizes) > 0 else 250
            center = current_sizes[1] if len(current_sizes) > 1 else 9999
            self._top_splitter.setSizes([left, center, 0])

    def _close_explorer_panel(self) -> None:
        if self._file_explorer is None:
            return
        if self._top_splitter is not None:
            self._top_sizes_before_explorer_toggle = self._top_splitter.sizes()
        self._file_explorer.setVisible(False)
        if self._top_splitter is not None:
            current_sizes = self._top_splitter.sizes()
            center = current_sizes[1] if len(current_sizes) > 1 else 9999
            right = current_sizes[2] if len(current_sizes) > 2 and (self._analysis_container and self._analysis_container.isVisible()) else 0
            self._top_splitter.setSizes([0, center, right])

    def _toggle_console_minimize(self) -> None:
        if self._console_panel is None or self._console_container is None:
            return
        self._console_minimized = not self._console_minimized
        if self._console_minimized:
            if self._main_splitter is not None:
                self._main_sizes_before_console_toggle = self._main_splitter.sizes()
            self._console_container.setVisible(False)
            if self._main_splitter is not None:
                self._main_splitter.setSizes([9999, 0])
        else:
            self._console_container.setVisible(True)
            self._console_container.setMinimumHeight(0)
            self._console_container.setMaximumHeight(self._MAX_QT_SIZE)
            if self._main_splitter is not None:
                if self._main_sizes_before_console_toggle:
                    self._main_splitter.setSizes(self._main_sizes_before_console_toggle)
                else:
                    self._main_splitter.setSizes([620, 180])

    def _toggle_analysis_minimize(self) -> None:
        if self._analysis_panel is None or self._analysis_container is None:
            return
        self._analysis_minimized = not self._analysis_minimized
        if self._analysis_minimized:
            if self._top_splitter is not None:
                self._top_sizes_before_analysis_toggle = self._top_splitter.sizes()
            self._analysis_container.setVisible(False)
            if self._top_splitter is not None:
                self._top_splitter.setSizes([250, 9999, 0])
        else:
            self._analysis_container.setVisible(True)
            self._analysis_container.setMinimumWidth(0)
            self._analysis_container.setMaximumWidth(self._MAX_QT_SIZE)
            if self._top_splitter is not None:
                if self._top_sizes_before_analysis_toggle:
                    self._top_splitter.setSizes(self._top_sizes_before_analysis_toggle)
                else:
                    self._top_splitter.setSizes([250, 700, 250])

    def _show_explorer_panel(self) -> None:
        if self._file_explorer is None:
            return
        self._file_explorer.setVisible(True)
        if self._top_splitter is not None:
            sizes = self._top_sizes_before_explorer_toggle or [250, 700, 250]
            if len(sizes) >= 3 and sizes[0] <= 20:
                sizes = [250, max(700, sizes[1]), sizes[2]]
            self._top_splitter.setSizes(sizes)

    def _toggle_terminal_panel(self) -> None:
        if self._console_container is None:
            return
        if self._console_container.isVisible():
            self._close_console_panel()
        else:
            self._show_terminal_panel()

    def _toggle_analysis_panel(self) -> None:
        if self._analysis_container is None:
            return
        if self._analysis_container.isVisible():
            self._close_analysis_panel()
        else:
            self._show_analysis_panel()

    def _toggle_explorer_panel(self) -> None:
        if self._file_explorer is None:
            return
        if self._file_explorer.isVisible():
            self._close_explorer_panel()
        else:
            self._show_explorer_panel()

    def _show_terminal_panel(self) -> None:
        if self._console_container is None:
            return
        self._console_container.setVisible(True)
        if self._console_panel is not None:
            self._console_minimized = False
            self._console_panel.setVisible(True)
        self._console_container.setMinimumHeight(0)
        self._console_container.setMaximumHeight(self._MAX_QT_SIZE)
        if self._main_splitter is not None:
            sizes = self._main_sizes_before_console_toggle or [620, 180]
            if len(sizes) >= 2 and sizes[1] <= 20:
                sizes = [max(620, sizes[0]), 180]
            self._main_splitter.setSizes(sizes)

    def _show_analysis_panel(self) -> None:
        if self._analysis_container is None:
            return
        self._analysis_container.setVisible(True)
        if self._analysis_panel is not None:
            self._analysis_minimized = False
            self._analysis_panel.setVisible(True)
        self._analysis_container.setMinimumWidth(0)
        self._analysis_container.setMaximumWidth(self._MAX_QT_SIZE)
        if self._top_splitter is not None:
            sizes = self._top_sizes_before_analysis_toggle or [250, 700, 250]
            if len(sizes) >= 3 and sizes[2] <= 20:
                sizes = [max(250, sizes[0]), max(700, sizes[1]), 250]
            self._top_splitter.setSizes(sizes)

    def _load_example_code(self) -> str:
        example_path = Path(__file__).resolve().parent.parent / "examples" / "hello_world.stn"
        if example_path.exists():
            return example_path.read_text(encoding="utf-8")
        return "// Hola mundo Skuld\n\ngate {\n    dmail(\"El Psy Kongroo\");\n}\n"

    def _update_cursor_status(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        current_file = self._get_active_file_path()
        file_label = current_file.name if current_file else self._current_tab_title()
        self._status.showMessage(f"Lab Member 004 · {file_label} · Línea {line}, Col {column}")

    def _new_file(self, with_example: bool = False) -> None:
        if self._editor_tabs is None:
            return

        editor = CodeEditor()
        editor.setReadOnly(False)
        editor.setFocusPolicy(Qt.StrongFocus)
        editor.setFont(QFont("Consolas", 11))
        if with_example:
            editor.setPlainText(self._load_example_code())
        self._bind_editor_events(editor)
        editor.setProperty("file_path", "")

        tab_title = f"Sin título {self._untitled_counter}"
        self._untitled_counter += 1
        tab_index = self._editor_tabs.addTab(editor, tab_title)
        self._editor_tabs.setCurrentIndex(tab_index)

        if self._console_panel is not None:
            self._console_panel.append_console("Nuevo archivo creado.")
        editor.setFocus()
        self._update_cursor_status()

    def _open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            "",
            "Archivos Skuld (*.stn);;Todos los archivos (*.*)",
        )
        if not file_path:
            return
        self._open_file_path(Path(file_path))

    def _open_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if not folder_path:
            return
        if self._file_explorer is not None:
            self._file_explorer.add_root_path(folder_path)
        if self._console_panel is not None:
            self._console_panel.append_console(f"Carpeta agregada: {Path(folder_path).name}")

    def _save_file(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        current_file = self._get_active_file_path()
        if not current_file:
            self._save_file_as()
            return

        current_file.write_text(editor.toPlainText(), encoding="utf-8")
        if self._console_panel is not None:
            self._console_panel.append_console(f"Archivo guardado: {current_file.name}")
        if self._file_explorer is not None:
            self._file_explorer.refresh()

    def _save_file_as(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            "",
            "Archivos Skuld (*.stn);;Todos los archivos (*.*)",
        )
        if not file_path:
            return

        path = Path(file_path)
        path.write_text(editor.toPlainText(), encoding="utf-8")
        editor.setProperty("file_path", str(path))

        if self._editor_tabs is not None:
            current_index = self._editor_tabs.currentIndex()
            if current_index >= 0:
                self._editor_tabs.setTabText(current_index, path.name)
                self._editor_tabs.setTabToolTip(current_index, str(path))

        if self._console_panel is not None:
            self._console_panel.append_console(f"Archivo guardado: {path.name}")
        if self._file_explorer is not None:
            self._file_explorer.refresh()
        self._update_cursor_status()

    def _close_file(self) -> None:
        if self._editor_tabs is None:
            return

        current_index = self._editor_tabs.currentIndex()
        if current_index >= 0:
            self._close_tab(current_index)

        if self._console_panel is not None:
            self._console_panel.append_console("Archivo cerrado.")
        self._update_cursor_status()

    def _run_phase(self, phase: str) -> None:
        editor = self._get_active_editor()
        if not editor:
            return

        current_file = self._get_active_file_path()
        if not current_file:
            self._save_file_as()
            current_file = self._get_active_file_path()
            if not current_file:
                return

        self._save_file()
        result = run_compiler(phase, str(current_file))

        if result.returncode != 0:
            if self._console_panel is not None:
                self._console_panel.append_errors(result.stderr or "Error ejecutando el compilador.")
            return

        output_text = result.stdout or "(sin salida)"
        if phase == "lexico":
            self._analysis_panel.set_tokens(output_text)
        elif phase == "sintactico":
            self._analysis_panel.set_syntax(output_text)
        elif phase == "semantico":
            self._analysis_panel.set_semantic(output_text)
        elif phase == "intermedio":
            self._analysis_panel.set_intermediate(output_text)
        elif phase == "ejecucion":
            if self._console_panel is not None:
                self._console_panel.append_execution(output_text)

        if self._console_panel is not None:
            self._console_panel.append_console(f"Fase ejecutada: {phase}")

    def _open_file_from_explorer(self, file_path: str) -> None:
        if self._console_panel is not None:
            self._console_panel.append_console(f"Solicitud abrir desde explorador: {Path(file_path).name}")
        self._open_file_path(Path(file_path))

    def _open_file_path(self, path: Path, log_to_console: bool = True) -> None:
        if self._editor_tabs is None:
            return

        if not path.exists() or not path.is_file():
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"El archivo no existe o no es valido:\n{path}",
            )
            return

        resolved = path.resolve()
        for index in range(self._editor_tabs.count()):
            editor = self._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            tab_file_raw = editor.property("file_path")
            if not tab_file_raw:
                continue
            tab_file = Path(str(tab_file_raw)).resolve()
            if tab_file == resolved:
                self._editor_tabs.setCurrentIndex(index)
                if log_to_console and self._console_panel is not None:
                    self._console_panel.append_console(f"Archivo abierto: {path.name}")
                active_editor = self._get_active_editor()
                if active_editor:
                    active_editor.setFocus()
                self._update_cursor_status()
                return

        editor = CodeEditor()
        editor.setReadOnly(False)
        editor.setFocusPolicy(Qt.StrongFocus)
        editor.setFont(QFont("Consolas", 11))
        try:
            editor.setPlainText(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"El archivo no esta en UTF-8:\n{path}",
            )
            return
        except OSError as exc:
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"No fue posible abrir el archivo:\n{path}\n\n{exc}",
            )
            return
        self._bind_editor_events(editor)
        editor.setProperty("file_path", str(path))

        tab_index = self._editor_tabs.addTab(editor, path.name)
        self._editor_tabs.setTabToolTip(tab_index, str(path))
        self._editor_tabs.setCurrentIndex(tab_index)
        if log_to_console and self._console_panel is not None:
            self._console_panel.append_console(f"Archivo abierto: {path.name}")
        editor.setFocus()
        self._update_cursor_status()

    def _restore_session(self) -> None:
        if self._file_explorer is None:
            return

        folder_paths = self._normalize_settings_list(self._settings.value("session/folders", []))
        open_files = self._normalize_settings_list(self._settings.value("session/open_files", []))
        active_file = str(self._settings.value("session/active_file", "") or "")

        if folder_paths:
            self._file_explorer.set_root_paths(folder_paths)

        opened_any = False
        for file_path in open_files:
            path = Path(file_path)
            if path.exists() and path.is_file():
                self._open_file_path(path, log_to_console=False)
                opened_any = True

        if not opened_any:
            self._new_file(with_example=True)
            return

        if active_file and self._editor_tabs is not None:
            active_path = Path(active_file)
            for index in range(self._editor_tabs.count()):
                editor = self._editor_tabs.widget(index)
                if not isinstance(editor, CodeEditor):
                    continue
                tab_file_raw = editor.property("file_path")
                if not tab_file_raw:
                    continue
                tab_path = Path(str(tab_file_raw))
                if tab_path == active_path:
                    self._editor_tabs.setCurrentIndex(index)
                    break

            self._restore_layout_state()

    def _save_session(self) -> None:
        folders: list[str] = []
        if self._file_explorer is not None:
            folders = self._file_explorer.get_root_paths()

        open_files: list[str] = []
        if self._editor_tabs is not None:
            for index in range(self._editor_tabs.count()):
                editor = self._editor_tabs.widget(index)
                if not isinstance(editor, CodeEditor):
                    continue
                file_path_raw = editor.property("file_path")
                if not file_path_raw:
                    continue
                file_path = Path(str(file_path_raw))
                if file_path.exists() and file_path.is_file():
                    open_files.append(str(file_path))

        active_file = ""
        active_path = self._get_active_file_path()
        if active_path is not None:
            active_file = str(active_path)

        self._settings.setValue("session/folders", folders)
        self._settings.setValue("session/open_files", open_files)
        self._settings.setValue("session/active_file", active_file)
        self._settings.setValue("session/analysis_visible", self._analysis_container.isVisible() if self._analysis_container is not None else True)
        self._settings.setValue("session/console_visible", self._console_container.isVisible() if self._console_container is not None else True)
        self._settings.setValue("session/explorer_visible", self._file_explorer.isVisible() if self._file_explorer is not None else True)
        self._settings.setValue("session/analysis_minimized", self._analysis_minimized)
        self._settings.setValue("session/console_minimized", self._console_minimized)
        if self._top_splitter is not None:
            self._settings.setValue("session/top_splitter_sizes", self._top_splitter.sizes())
        if self._main_splitter is not None:
            self._settings.setValue("session/main_splitter_sizes", self._main_splitter.sizes())
        self._settings.sync()

    def _normalize_settings_list(self, value) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        text = str(value).strip()
        if not text:
            return []
        return [text]

    def _restore_layout_state(self) -> None:
        analysis_visible = bool(self._settings.value("session/analysis_visible", True, type=bool))
        console_visible = bool(self._settings.value("session/console_visible", True, type=bool))
        explorer_visible = bool(self._settings.value("session/explorer_visible", True, type=bool))
        self._analysis_minimized = bool(self._settings.value("session/analysis_minimized", False, type=bool))
        self._console_minimized = bool(self._settings.value("session/console_minimized", False, type=bool))

        top_sizes = self._normalize_settings_list(self._settings.value("session/top_splitter_sizes", []))
        main_sizes = self._normalize_settings_list(self._settings.value("session/main_splitter_sizes", []))

        if self._analysis_container is not None:
            self._analysis_container.setVisible(analysis_visible)
        if self._console_container is not None:
            self._console_container.setVisible(console_visible)
        if self._file_explorer is not None:
            self._file_explorer.setVisible(explorer_visible)

        if self._analysis_panel is not None:
            self._analysis_panel.setVisible(analysis_visible and not self._analysis_minimized)
        if self._console_panel is not None:
            self._console_panel.setVisible(console_visible and not self._console_minimized)

        if self._top_splitter is not None and top_sizes:
            parsed_top_sizes = [int(value) for value in top_sizes if str(value).strip()]
            if parsed_top_sizes:
                self._top_splitter.setSizes(parsed_top_sizes)
                self._top_sizes_before_analysis_toggle = parsed_top_sizes

        if self._main_splitter is not None and main_sizes:
            parsed_main_sizes = [int(value) for value in main_sizes if str(value).strip()]
            if parsed_main_sizes:
                self._main_splitter.setSizes(parsed_main_sizes)
                self._main_sizes_before_console_toggle = parsed_main_sizes

        if self._analysis_minimized and self._analysis_container is not None:
            self._analysis_container.setVisible(False)
        if self._console_minimized and self._console_container is not None:
            self._console_container.setVisible(False)
        if not explorer_visible and self._file_explorer is not None:
            self._file_explorer.setVisible(False)

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        self._save_session()
        super().closeEvent(event)

    def _close_tab(self, index: int) -> None:
        if self._editor_tabs is None:
            return
        widget = self._editor_tabs.widget(index)
        self._editor_tabs.removeTab(index)
        if widget:
            widget.deleteLater()
        if self._editor_tabs.count() == 0:
            self._new_file()

    def _on_tab_changed(self, _index: int) -> None:
        editor = self._get_active_editor()
        if editor:
            editor.setReadOnly(False)
            editor.setFocus()
        self._update_cursor_status()

    def _get_active_editor(self) -> CodeEditor | None:
        if self._editor_tabs is None:
            return None
        widget = self._editor_tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def _get_active_file_path(self) -> Path | None:
        editor = self._get_active_editor()
        if not editor:
            return None
        file_path_raw = editor.property("file_path")
        if not file_path_raw:
            return None
        return Path(str(file_path_raw))

    def _current_tab_title(self) -> str:
        if self._editor_tabs is None:
            return "Sin archivo"
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return "Sin archivo"
        return self._editor_tabs.tabText(current_index) or "Sin archivo"

    def _clear_outputs(self) -> None:
        if self._analysis_panel is not None:
            self._analysis_panel.set_tokens("")
            self._analysis_panel.set_syntax("")
            self._analysis_panel.set_semantic("")
            self._analysis_panel.set_intermediate("")
            self._analysis_panel.set_symbols("")
        if self._console_panel is not None:
            self._console_panel.clear_all()
