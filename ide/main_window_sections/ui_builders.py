from __future__ import annotations

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QShortcut,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ide.analysis_panel import AnalysisPanel
from ide.code_editor import CodeEditor
from ide.console_panel import ConsolePanel
from ide.file_explorer import FileExplorer
from ide.theme import steins_gate_theme


def build_menu(window) -> None:
    menu_file = window.menuBar().addMenu("Archivo")
    menu_edit = window.menuBar().addMenu("Editar")
    menu_build = window.menuBar().addMenu("Compilar")
    menu_help = window.menuBar().addMenu("Ayuda")

    action_new = QAction("Nuevo", window)
    action_open = QAction("Abrir", window)
    action_open_folder = QAction("Abrir Carpeta", window)
    action_close = QAction("Cerrar", window)
    action_save = QAction("Guardar", window)
    action_save_as = QAction("Guardar Como", window)
    action_find = QAction("Buscar", window)
    action_find_next = QAction("Buscar siguiente", window)
    action_find_prev = QAction("Buscar anterior", window)
    action_go_to_line = QAction("Ir a línea", window)
    action_toggle_analysis = QAction("Alternar Analizadores", window)
    action_toggle_terminal = QAction("Alternar Terminal", window)
    action_toggle_explorer = QAction("Alternar Árbol de archivos", window)
    action_adjust_layout = QAction("Ajustar layout al contenido", window)
    action_themes = QAction("Temas", window)
    action_code_font = QAction("Topografia", window)
    action_undo = QAction("Deshacer", window)
    action_redo = QAction("Rehacer", window)
    action_copy = QAction("Copiar", window)
    action_paste = QAction("Pegar", window)
    action_autosave = QAction("Autoguardado (300s)", window)
    action_zoom_in = QAction("Aumentar texto", window)
    action_zoom_out = QAction("Disminuir texto", window)
    action_exit = QAction("Salir", window)

    action_new.setShortcut(QKeySequence("Ctrl+N"))
    action_open_folder.setShortcut(QKeySequence("Ctrl+O"))
    action_save.setShortcut(QKeySequence("Ctrl+S"))
    action_save.setShortcutContext(Qt.ApplicationShortcut)
    action_save_as.setShortcut(QKeySequence("Ctrl+G"))
    action_save_as.setShortcutContext(Qt.ApplicationShortcut)
    action_find.setShortcut(QKeySequence("Ctrl+F"))
    action_find_next.setShortcut(QKeySequence("F3"))
    action_find_prev.setShortcut(QKeySequence("Shift+F3"))
    action_go_to_line.setShortcut(QKeySequence("Ctrl+4"))
    action_undo.setShortcut(QKeySequence("Ctrl+Z"))
    action_redo.setShortcut(QKeySequence("Ctrl+Y"))
    action_copy.setShortcut(QKeySequence("Ctrl+C"))
    action_paste.setShortcut(QKeySequence("Ctrl+V"))
    action_toggle_analysis.setShortcut(QKeySequence("Ctrl+1"))
    action_toggle_terminal.setShortcut(QKeySequence("Ctrl+2"))
    action_toggle_explorer.setShortcut(QKeySequence("Ctrl+3"))
    action_adjust_layout.setShortcut(QKeySequence("Ctrl+Alt+A"))
    action_zoom_in.setShortcuts([
        QKeySequence("Ctrl++"),
        QKeySequence("Ctrl+="),
        QKeySequence("Ctrl+Shift+="),
    ])
    action_zoom_in.setShortcutContext(Qt.ApplicationShortcut)
    action_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
    action_zoom_out.setShortcutContext(Qt.ApplicationShortcut)
    action_find_next.setShortcutContext(Qt.ApplicationShortcut)
    action_find_prev.setShortcutContext(Qt.ApplicationShortcut)
    action_go_to_line.setShortcutContext(Qt.ApplicationShortcut)
    action_undo.setShortcutContext(Qt.ApplicationShortcut)
    action_redo.setShortcutContext(Qt.ApplicationShortcut)
    action_copy.setShortcutContext(Qt.ApplicationShortcut)
    action_paste.setShortcutContext(Qt.ApplicationShortcut)
    action_autosave.setCheckable(True)
    action_autosave.setChecked(window._autosave_enabled)

    action_new.triggered.connect(window._new_file)
    action_open.triggered.connect(window._open_file)
    action_open_folder.triggered.connect(window._open_folder)
    action_close.triggered.connect(window._close_file)
    action_save.triggered.connect(window._save_file)
    action_save_as.triggered.connect(window._save_file_as)
    action_find.triggered.connect(window._find_in_code)
    action_find_next.triggered.connect(window._find_next)
    action_find_prev.triggered.connect(window._find_previous)
    action_go_to_line.triggered.connect(window._go_to_line)
    action_undo.triggered.connect(window._undo_active_editor)
    action_redo.triggered.connect(window._redo_active_editor)
    action_copy.triggered.connect(window._copy_active_editor)
    action_paste.triggered.connect(window._paste_active_editor)
    action_toggle_analysis.triggered.connect(window._toggle_analysis_panel)
    action_toggle_terminal.triggered.connect(window._toggle_terminal_panel)
    action_toggle_explorer.triggered.connect(window._toggle_explorer_panel)
    action_adjust_layout.triggered.connect(window._fit_editor_to_content)
    action_themes.triggered.connect(window._open_theme_dialog)
    action_code_font.triggered.connect(window._select_code_font)
    action_autosave.triggered.connect(lambda enabled: window._set_autosave_enabled(bool(enabled)))
    action_zoom_in.triggered.connect(lambda: window._change_code_font_size(1))
    action_zoom_out.triggered.connect(lambda: window._change_code_font_size(-1))
    action_exit.triggered.connect(window.close)

    menu_file.addAction(action_new)
    menu_file.addAction(action_open)
    menu_file.addAction(action_open_folder)
    menu_file.addAction(action_close)
    menu_file.addSeparator()
    menu_file.addAction(action_save)
    menu_file.addAction(action_save_as)
    menu_file.addSeparator()
    menu_file.addAction(action_exit)

    menu_edit.addAction(action_undo)
    menu_edit.addAction(action_redo)
    menu_edit.addAction(action_copy)
    menu_edit.addAction(action_paste)
    menu_edit.addSeparator()
    menu_edit.addAction(action_find)
    menu_edit.addAction(action_find_next)
    menu_edit.addAction(action_find_prev)
    menu_edit.addAction(action_go_to_line)
    menu_edit.addAction(action_toggle_analysis)
    menu_edit.addAction(action_toggle_terminal)
    menu_edit.addAction(action_toggle_explorer)
    menu_edit.addAction(action_adjust_layout)
    menu_edit.addAction(action_themes)
    menu_edit.addAction(action_code_font)
    menu_edit.addAction(action_autosave)
    menu_edit.addAction(action_zoom_in)
    menu_edit.addAction(action_zoom_out)

    action_lex = QAction("Análisis Léxico", window)
    action_syn = QAction("Análisis Sintáctico", window)
    action_sem = QAction("Análisis Semántico", window)
    action_inter = QAction("Código Intermedio", window)
    action_exec = QAction("Ejecución", window)
    action_clear = QAction("Limpiar", window)

    action_lex.triggered.connect(lambda: window._run_phase("lexico"))
    action_syn.triggered.connect(lambda: window._run_phase("sintactico"))
    action_sem.triggered.connect(lambda: window._run_phase("semantico"))
    action_inter.triggered.connect(lambda: window._run_phase("intermedio"))
    action_exec.triggered.connect(lambda: window._run_phase("ejecucion"))
    action_clear.triggered.connect(window._clear_outputs)

    menu_build.addAction(action_lex)
    menu_build.addAction(action_syn)
    menu_build.addAction(action_sem)
    menu_build.addAction(action_inter)
    menu_build.addAction(action_exec)
    menu_build.addSeparator()
    menu_build.addAction(action_clear)

    for label in ["Documentación", "Acerca de"]:
        menu_help.addAction(QAction(label, window))


def build_toolbar(window) -> None:
    toolbar = QToolBar("Herramientas", window)
    toolbar.setMovable(False)
    toolbar.setIconSize(QSize(20, 20))
    window.addToolBar(Qt.TopToolBarArea, toolbar)

    colors = steins_gate_theme.get_colors()
    warm_color = "#f5b041"
    green_color = "#58d68d"
    blue_color = "#5dade2"
    purple_color = "#af7ac5"

    action_new = QAction(window._toolbar_icon(["fa5s.file-alt", "fa5.file"], QStyle.SP_FileIcon, color=colors.foreground), "Nuevo", window)
    action_open = QAction(window._toolbar_icon(["fa5s.folder-open", "fa5.folder-open"], QStyle.SP_DirOpenIcon, color=warm_color), "Abrir", window)
    action_save = QAction(window._toolbar_icon(["fa5s.save", "fa5.save"], QStyle.SP_DialogSaveButton, color=green_color), "Guardar", window)
    action_save_as = QAction(window._toolbar_icon(["fa5s.file-export", "fa5.copy"], QStyle.SP_DialogSaveButton, color=blue_color), "Guardar como", window)
    action_find = QAction(window._toolbar_icon(["fa5s.search", "fa5.search"], QStyle.SP_FileDialogContentsView, color=purple_color), "Buscar", window)
    action_toggle_analysis = QAction(window._toolbar_icon(["fa5s.chart-bar", "fa5.chart-bar"], QStyle.SP_FileDialogDetailedView, color=colors.accent), "Alternar analizadores", window)
    action_toggle_terminal = QAction(window._toolbar_icon(["fa5s.terminal", "fa5.terminal"], QStyle.SP_ComputerIcon, color=colors.foreground), "Alternar terminal", window)
    action_toggle_explorer = QAction(window._toolbar_icon(["fa5s.sitemap", "fa5.sitemap"], QStyle.SP_DirIcon, color=warm_color), "Alternar árbol", window)
    action_lex = QAction(window._toolbar_icon(["fa5s.font", "fa5.font"], QStyle.SP_FileDialogInfoView, color=blue_color), "Léxico", window)
    action_syn = QAction(window._toolbar_icon(["fa5s.code-branch", "fa5.code-branch"], QStyle.SP_FileDialogContentsView, color=purple_color), "Sintáctico", window)
    action_sem = QAction(window._toolbar_icon(["fa5s.check-circle", "fa5.check-circle"], QStyle.SP_MessageBoxInformation, color=green_color), "Semántico", window)
    action_inter = QAction(window._toolbar_icon(["fa5s.cogs", "fa5.cogs"], QStyle.SP_ComputerIcon, color=warm_color), "Intermedio", window)
    action_exec = QAction(window._toolbar_icon(["fa5s.play-circle", "fa5.play-circle"], QStyle.SP_MediaPlay, color=colors.accent), "Ejecución", window)

    action_new.setToolTip("Nuevo (Ctrl+N)")
    action_open.setToolTip("Abrir archivo")
    action_save.setToolTip("Guardar (Ctrl+S)")
    action_save_as.setToolTip("Guardar como (Ctrl+Shift+S)")
    action_find.setToolTip("Buscar (Ctrl+F)")
    action_toggle_analysis.setToolTip("Alternar analizadores (Ctrl+1)")
    action_toggle_terminal.setToolTip("Alternar terminal (Ctrl+2)")
    action_toggle_explorer.setToolTip("Alternar árbol de archivos (Ctrl+3)")
    action_lex.setToolTip("Análisis léxico")
    action_syn.setToolTip("Análisis sintáctico")
    action_sem.setToolTip("Análisis semántico")
    action_inter.setToolTip("Código intermedio")
    action_exec.setToolTip("Ejecución")

    action_new.triggered.connect(window._new_file)
    action_open.triggered.connect(window._open_file)
    action_save.triggered.connect(window._save_file)
    action_save_as.triggered.connect(window._save_file_as)
    action_find.triggered.connect(window._find_in_code)
    action_toggle_analysis.triggered.connect(window._toggle_analysis_panel)
    action_toggle_terminal.triggered.connect(window._toggle_terminal_panel)
    action_toggle_explorer.triggered.connect(window._toggle_explorer_panel)
    action_lex.triggered.connect(lambda: window._run_phase("lexico"))
    action_syn.triggered.connect(lambda: window._run_phase("sintactico"))
    action_sem.triggered.connect(lambda: window._run_phase("semantico"))
    action_inter.triggered.connect(lambda: window._run_phase("intermedio"))
    action_exec.triggered.connect(lambda: window._run_phase("ejecucion"))

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


def build_layout(window) -> None:
    window._editor_tabs = QTabWidget()
    window._editor_tabs.setFocusPolicy(Qt.StrongFocus)
    window._editor_tabs.setMinimumWidth(420)
    window._editor_tabs.setTabsClosable(True)
    window._editor_tabs.tabCloseRequested.connect(window._close_tab)
    window._editor_tabs.currentChanged.connect(window._on_tab_changed)

    window._editor_container = QWidget(window)
    editor_layout = QVBoxLayout(window._editor_container)
    editor_layout.setContentsMargins(0, 0, 0, 0)
    editor_layout.setSpacing(0)

    window._find_bar = build_find_bar(window)
    editor_layout.addWidget(window._find_bar)
    editor_layout.addWidget(window._editor_tabs, 1)
    window._editor_container.setMinimumWidth(420)

    window._file_explorer = FileExplorer()
    window._file_explorer.file_open_requested.connect(window._open_file_from_explorer)
    window._file_explorer.file_close_requested.connect(window._close_file_from_explorer)
    window._file_explorer.path_renamed.connect(window._on_path_renamed)
    window._file_explorer.path_deleted.connect(window._on_path_deleted)
    window._analysis_panel = AnalysisPanel()
    window._analysis_container = window._create_panel_container(
        "Analizadores",
        window._analysis_panel,
        on_toggle_minimize=window._toggle_analysis_minimize,
        on_close=window._close_analysis_panel,
    )

    window._top_splitter = QSplitter(Qt.Horizontal)
    window._top_splitter.setChildrenCollapsible(True)
    window._top_splitter.addWidget(window._file_explorer)
    window._top_splitter.addWidget(window._editor_container)
    window._top_splitter.addWidget(window._analysis_container)
    window._top_splitter.setStretchFactor(0, 1)
    window._top_splitter.setStretchFactor(1, 3)
    window._top_splitter.setStretchFactor(2, 1)
    window._top_splitter.setSizes([250, 700, 250])
    window._top_sizes_before_analysis_toggle = window._top_splitter.sizes()

    window._console_panel = ConsolePanel()
    window._console_container = window._create_panel_container(
        "Terminal",
        window._console_panel,
        on_toggle_minimize=window._toggle_console_minimize,
        on_close=window._close_console_panel,
    )

    window._main_splitter = QSplitter(Qt.Vertical)
    window._main_splitter.addWidget(window._top_splitter)
    window._main_splitter.addWidget(window._console_container)
    window._main_splitter.setStretchFactor(0, 3)
    window._main_splitter.setStretchFactor(1, 1)
    window._main_splitter.setSizes([620, 180])
    window._main_sizes_before_console_toggle = window._main_splitter.sizes()

    window.setCentralWidget(window._main_splitter)
    window._restore_session()


def build_find_bar(window) -> QWidget:
    bar = QWidget(window)
    bar.setObjectName("find_bar")

    layout = QHBoxLayout(bar)
    layout.setContentsMargins(8, 6, 8, 6)
    layout.setSpacing(6)

    stack = QStackedWidget(bar)

    find_page = QWidget(stack)
    find_layout = QHBoxLayout(find_page)
    find_layout.setContentsMargins(0, 0, 0, 0)
    find_layout.setSpacing(6)

    label = QLabel("Buscar:", find_page)
    field = QLineEdit(find_page)
    field.setPlaceholderText("Texto a buscar")
    field.setClearButtonEnabled(True)

    count_label = QLabel("0/0", find_page)
    count_label.setObjectName("find_count")

    previous_button = QToolButton(find_page)
    previous_button.setText("◀")
    previous_button.setToolTip("Coincidencia anterior (Shift+F3)")

    next_button = QToolButton(find_page)
    next_button.setText("▶")
    next_button.setToolTip("Siguiente coincidencia (F3)")

    close_button = QToolButton(find_page)
    close_button.setText("✕")
    close_button.setToolTip("Cerrar búsqueda (Esc)")

    find_layout.addWidget(label)
    find_layout.addWidget(field, 1)
    find_layout.addWidget(count_label)
    find_layout.addWidget(previous_button)
    find_layout.addWidget(next_button)
    find_layout.addWidget(close_button)

    line_page = QWidget(stack)
    line_layout = QHBoxLayout(line_page)
    line_layout.setContentsMargins(0, 0, 0, 0)
    line_layout.setSpacing(6)

    line_label = QLabel("Ir a línea:", line_page)
    line_input = QSpinBox(line_page)
    line_input.setMinimum(1)
    line_input.setMaximum(1)
    line_input.setButtonSymbols(QSpinBox.NoButtons)

    go_button = QToolButton(line_page)
    go_button.setText("Ir")
    go_button.setToolTip("Mover cursor a la línea")

    go_close_button = QToolButton(line_page)
    go_close_button.setText("✕")
    go_close_button.setToolTip("Cerrar (Esc)")

    line_layout.addWidget(line_label)
    line_layout.addWidget(line_input)
    line_layout.addWidget(go_button)
    line_layout.addWidget(go_close_button)
    line_layout.addStretch(1)

    stack.addWidget(find_page)
    stack.addWidget(line_page)
    layout.addWidget(stack, 1)

    field.textChanged.connect(window._on_find_text_changed)
    field.returnPressed.connect(window._find_next)
    previous_button.clicked.connect(window._find_previous)
    next_button.clicked.connect(window._find_next)
    close_button.clicked.connect(window._hide_find_bar)
    line_input.editingFinished.connect(lambda: window._jump_to_line(line_input.value()))
    go_button.clicked.connect(lambda: window._jump_to_line(line_input.value()))
    go_close_button.clicked.connect(window._hide_find_bar)

    window._find_close_shortcut = QShortcut(QKeySequence("Esc"), bar)
    window._find_close_shortcut.activated.connect(window._hide_find_bar)

    window._find_bar_stack = stack
    window._find_input = field
    window._find_count_label = count_label
    window._find_previous_button = previous_button
    window._find_next_button = next_button
    window._find_close_button = close_button
    window._go_to_line_input = line_input
    window._go_to_line_button = go_button
    window._go_to_line_close_button = go_close_button

    bar.setVisible(False)
    return bar
