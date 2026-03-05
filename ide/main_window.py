from __future__ import annotations

import datetime
import importlib
from pathlib import Path

from PyQt5.QtCore import QFileSystemWatcher, QSettings, QSize, Qt, QTimer
from PyQt5.QtGui import QCloseEvent, QFont, QFontDatabase, QFontMetrics, QIcon, QKeySequence, QTextCursor, QTextDocument
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QMainWindow,
    QPlainTextEdit,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QShortcut,
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
from ide.main_window_sections import (
    apply_code_font_to_open_editors,
    apply_theme,
    auto_save_open_files,
    build_find_bar,
    build_layout,
    build_menu,
    build_toolbar,
    change_code_font_size,
    clear_outputs,
    close_file,
    close_file_from_explorer,
    close_tab,
    collect_unsaved_tab_indexes,
    confirm_all_unsaved_before_exit,
    confirm_unsaved_for_tab,
    create_themed_file_dialog,
    current_tab_title,
    get_active_editor,
    get_active_file_path,
    new_file,
    normalize_settings_list,
    on_path_deleted,
    on_path_renamed,
    on_tab_changed,
    on_watched_file_changed,
    open_file,
    open_file_from_explorer,
    open_file_path,
    open_folder,
    open_theme_dialog,
    reload_editor_from_disk,
    restore_layout_state,
    restore_session,
    run_phase,
    save_editor,
    save_editor_as,
    save_file,
    save_file_as,
    save_session,
    set_autosave_enabled,
    select_code_font,
    unwatch_file_if_unused,
    watch_file,
    write_editor_to_path,
)
from ide.theme import steins_gate_theme

try:
    qta = importlib.import_module("qtawesome")
except ImportError:
    qta = None


class MainWindow(QMainWindow):
    _MAX_QT_SIZE = 16777215
    _DEFAULT_CODE_FONT_FAMILY = "Consolas"
    _DEFAULT_CODE_FONT_SIZE = 11
    _AUTOSAVE_INTERVAL_MS = 300_000

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reading Steiner IDE v1.0")
        self.resize(1420, 860)
        self.setMinimumWidth(1200)

        self._status = QStatusBar(self)
        self._settings = QSettings("Skuld", "ReadingSteinerIDE")
        self._editor_tabs: QTabWidget | None = None
        self._editor_container: QWidget | None = None
        self._find_bar: QWidget | None = None
        self._find_bar_stack: QStackedWidget | None = None
        self._find_input: QLineEdit | None = None
        self._find_count_label: QLabel | None = None
        self._find_previous_button: QToolButton | None = None
        self._find_next_button: QToolButton | None = None
        self._find_close_button: QToolButton | None = None
        self._go_to_line_input: QSpinBox | None = None
        self._go_to_line_button: QToolButton | None = None
        self._go_to_line_close_button: QToolButton | None = None
        self._find_close_shortcut: QShortcut | None = None
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
        self._code_font = QFont(self._DEFAULT_CODE_FONT_FAMILY, self._DEFAULT_CODE_FONT_SIZE)
        self._search_text = ""
        self._autosave_enabled = bool(self._settings.value("session/autosave_enabled", False, type=bool))
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(self._AUTOSAVE_INTERVAL_MS)
        self._autosave_timer.timeout.connect(self._auto_save_open_files)
        self._file_watcher = QFileSystemWatcher(self)
        self._file_watcher.fileChanged.connect(self._on_watched_file_changed)
        self._watched_files_mtime: dict[str, float] = {}
        self._suppress_file_watch_event: set[str] = set()

        self._restore_code_font_preference()
        self._build_menu()
        self._build_toolbar()
        self._build_status_bar()
        self._restore_theme_preference()
        self._build_layout()
        self._set_autosave_enabled(self._autosave_enabled, persist=False)

    def _build_menu(self) -> None:
        build_menu(self)

    def _build_toolbar(self) -> None:
        build_toolbar(self)

    def _toolbar_icon(
        self,
        awesome_names: str | list[str],
        fallback_standard: QStyle.StandardPixmap,
        *,
        color: str | None = None,
    ) -> QIcon:
        if qta is not None:
            try:
                icon_color = color or steins_gate_theme.get_colors().foreground
                names = [awesome_names] if isinstance(awesome_names, str) else awesome_names
                for icon_name in names:
                    try:
                        return qta.icon(icon_name, color=icon_color)
                    except Exception:
                        continue
            except Exception:
                pass
        return self.style().standardIcon(fallback_standard)

    def _build_status_bar(self) -> None:
        self._status.showMessage(f"{self._current_lab_member_label()} · El Psy Kongroo")
        self.setStatusBar(self._status)

    def _current_lab_member_label(self) -> str:
        theme_key = steins_gate_theme.get_theme_key()
        member_code = theme_key.split("_", 1)[1] if "_" in theme_key else "004"
        if member_code.isdigit():
            return f"Lab Member {int(member_code):03d}"
        return steins_gate_theme.get_theme_name()

    def _build_layout(self) -> None:
        build_layout(self)

    def _build_find_bar(self) -> QWidget:
        return build_find_bar(self)

    def _show_find_bar(self, mode: str = "find") -> None:
        if self._find_bar is None:
            return

        self._find_bar.setVisible(True)

        if mode == "line":
            self._show_go_to_line_bar()
            return

        if self._find_bar_stack is not None:
            self._find_bar_stack.setCurrentIndex(0)

        if self._find_input is not None:
            self._find_input.setFocus()
            self._find_input.selectAll()

        self._update_find_match_label()

    def _show_go_to_line_bar(self) -> None:
        if self._find_bar is None or self._go_to_line_input is None:
            return

        editor = self._get_active_editor()
        if editor is None:
            return

        self._find_bar.setVisible(True)
        if self._find_bar_stack is not None:
            self._find_bar_stack.setCurrentIndex(1)

        max_line = max(1, editor.blockCount())
        current_line = editor.textCursor().blockNumber() + 1
        self._go_to_line_input.setMaximum(max_line)
        self._go_to_line_input.setValue(current_line)
        self._go_to_line_input.setFocus()
        line_edit = self._go_to_line_input.lineEdit()
        if line_edit is not None:
            line_edit.selectAll()

    def _hide_find_bar(self) -> None:
        if self._find_bar is not None:
            self._find_bar.setVisible(False)

        editor = self._get_active_editor()
        if editor is not None:
            editor.setFocus()

    def _on_find_text_changed(self, text: str) -> None:
        self._search_text = text

        if self._editor_tabs is None:
            return

        for index in range(self._editor_tabs.count()):
            editor = self._editor_tabs.widget(index)
            if isinstance(editor, CodeEditor):
                editor.set_search_highlights(self._search_text)

        self._update_find_match_label()

        if not text.strip():
            self._status.showMessage("Búsqueda limpiada", 1200)

    def _update_find_match_label(self) -> None:
        if self._find_count_label is None:
            return

        editor = self._get_active_editor()
        term = self._search_text
        if editor is None or not term.strip():
            self._find_count_label.setText("0/0")
            return

        content = editor.toPlainText()
        if not content:
            self._find_count_label.setText("0/0")
            return

        positions: list[int] = []
        offset = 0
        step = len(term)
        while True:
            index = content.find(term, offset)
            if index == -1:
                break
            positions.append(index)
            offset = index + step

        total = len(positions)
        if total == 0:
            self._find_count_label.setText("0/0")
            return

        cursor = editor.textCursor()
        cursor_position = min(cursor.position(), cursor.anchor())
        current = 1
        for position in positions:
            if position <= cursor_position:
                current += 1
            else:
                break
        current = max(1, min(total, current - 1))

        self._find_count_label.setText(f"{current}/{total}")

    def _bind_editor_events(self, editor: CodeEditor) -> None:
        editor.cursorPositionChanged.connect(self._update_cursor_status)
        editor.textChanged.connect(self._on_text_changed)

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
        if self._editor_container is not None:
            self._editor_container.setMinimumWidth(desired_width)
        else:
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

        selected_text = editor.textCursor().selectedText().replace("\u2029", " ").strip()
        if self._find_input is not None and selected_text and selected_text != self._search_text:
            self._find_input.setText(selected_text)
        elif self._find_input is not None and self._search_text:
            self._find_input.setText(self._search_text)

        self._show_find_bar("find")

    def _find_next(self) -> None:
        editor = self._get_active_editor()
        if editor is None:
            return

        if not self._search_text.strip():
            self._find_in_code()
            return

        if editor.find(self._search_text):
            self._update_find_match_label()
            return

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
        if editor.find(self._search_text):
            self._status.showMessage("Búsqueda reiniciada desde el inicio", 1500)
            self._update_find_match_label()
            return

        self._status.showMessage(f"No se encontró: {self._search_text}", 2000)
        self._update_find_match_label()

    def _find_previous(self) -> None:
        editor = self._get_active_editor()
        if editor is None:
            return

        if not self._search_text.strip():
            self._find_in_code()
            return

        if editor.find(self._search_text, QTextDocument.FindBackward):
            self._update_find_match_label()
            return

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        if editor.find(self._search_text, QTextDocument.FindBackward):
            self._status.showMessage("Búsqueda reiniciada desde el final", 1500)
            self._update_find_match_label()
            return

        self._status.showMessage(f"No se encontró: {self._search_text}", 2000)
        self._update_find_match_label()

    def _go_to_line(self) -> None:
        self._show_find_bar("line")

    def _jump_to_line(self, target_line: int) -> None:
        editor = self._get_active_editor()
        if editor is None:
            return

        max_line = max(1, editor.blockCount())
        final_line = max(1, min(int(target_line), max_line))

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, final_line - 1)
        editor.setTextCursor(cursor)
        editor.setFocus()
        self._update_cursor_status()

    def _undo_active_editor(self) -> None:
        editor = self._get_active_editor()
        if editor is not None:
            editor.undo()

    def _redo_active_editor(self) -> None:
        editor = self._get_active_editor()
        if editor is not None:
            editor.redo()

    def _copy_active_editor(self) -> None:
        editor = self._get_active_editor()
        if editor is not None:
            editor.copy()

    def _paste_active_editor(self) -> None:
        editor = self._get_active_editor()
        if editor is not None:
            editor.paste()

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

    def _restore_theme_preference(self) -> None:
        saved_theme_key = str(self._settings.value("session/theme", steins_gate_theme.get_theme_key()) or "")
        if not saved_theme_key:
            return
        self._apply_theme(saved_theme_key, persist=False, show_status=False)

    def _restore_code_font_preference(self) -> None:
        family = str(self._settings.value("session/code_font_family", self._DEFAULT_CODE_FONT_FAMILY) or self._DEFAULT_CODE_FONT_FAMILY)
        size = int(self._settings.value("session/code_font_size", self._DEFAULT_CODE_FONT_SIZE) or self._DEFAULT_CODE_FONT_SIZE)
        self._code_font = QFont(family, size)

    def _select_code_font(self) -> None:
        select_code_font(self)

    def _apply_code_font_to_open_editors(self) -> None:
        apply_code_font_to_open_editors(self)

    def _change_code_font_size(self, delta: int) -> None:
        change_code_font_size(self, delta)

    def _apply_theme(self, theme_key: str, *, persist: bool = True, show_status: bool = True) -> None:
        apply_theme(self, theme_key, persist=persist, show_status=show_status)

    def _open_theme_dialog(self) -> None:
        open_theme_dialog(self)

    def _on_text_changed(self) -> None:
        editor = self._get_active_editor()
        if editor:
            editor.setProperty("unsaved", True)
            if self._search_text:
                editor.set_search_highlights(self._search_text)
            self._update_find_match_label()
        self._update_cursor_status()

    def _set_autosave_enabled(self, enabled: bool, *, persist: bool = True) -> None:
        set_autosave_enabled(self, enabled, persist=persist)

    def _auto_save_open_files(self) -> None:
        auto_save_open_files(self)

    def _write_editor_to_path(self, editor: CodeEditor, path: Path) -> bool:
        return write_editor_to_path(self, editor, path)

    def _save_editor_as(self, editor: CodeEditor, index: int | None = None) -> bool:
        return save_editor_as(self, editor, index=index)

    def _save_editor(self, editor: CodeEditor, index: int | None = None) -> bool:
        return save_editor(self, editor, index=index)

    def _collect_unsaved_tab_indexes(self) -> list[int]:
        return collect_unsaved_tab_indexes(self)

    def _confirm_unsaved_for_tab(self, index: int) -> bool:
        return confirm_unsaved_for_tab(self, index)

    def _confirm_all_unsaved_before_exit(self) -> bool:
        return confirm_all_unsaved_before_exit(self)

    def _watch_file(self, path: Path) -> None:
        watch_file(self, path)

    def _unwatch_file_if_unused(self, path: Path) -> None:
        unwatch_file_if_unused(self, path)

    def _reload_editor_from_disk(self, editor: CodeEditor, path: Path) -> bool:
        return reload_editor_from_disk(self, editor, path)

    def _on_watched_file_changed(self, file_path: str) -> None:
        on_watched_file_changed(self, file_path)

    def _update_cursor_status(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        current_file = self._get_active_file_path()
        file_label = current_file.name if current_file else self._current_tab_title()
        unsaved = editor.property("unsaved")
        save_indicator = "  ●  Sin guardar" if unsaved else ""
        self._status.showMessage(
            f"{self._current_lab_member_label()} · {file_label} · Línea {line}, Col {column}{save_indicator}"
        )

    def _new_file(self, with_example: bool = False) -> None:
        new_file(self, with_example=with_example)

    def _open_file(self) -> None:
        open_file(self)

    def _open_folder(self) -> None:
        open_folder(self)

    def _create_themed_file_dialog(
        self,
        *,
        title: str,
        accept_mode: QFileDialog.AcceptMode,
        file_mode: QFileDialog.FileMode,
        name_filters: list[str] | None = None,
        selected_filter: str | None = None,
        default_suffix: str | None = None,
    ) -> QFileDialog:
        return create_themed_file_dialog(
            self,
            title=title,
            accept_mode=accept_mode,
            file_mode=file_mode,
            name_filters=name_filters,
            selected_filter=selected_filter,
            default_suffix=default_suffix,
        )

    def _save_file(self) -> None:
        save_file(self)

    def _save_file_as(self) -> None:
        save_file_as(self)

    def _close_file(self) -> None:
        close_file(self)

    def _run_phase(self, phase: str) -> None:
        run_phase(self, phase)

    def _open_file_from_explorer(self, file_path: str) -> None:
        open_file_from_explorer(self, file_path)

    def _close_file_from_explorer(self, file_path: str) -> None:
        close_file_from_explorer(self, file_path)

    def _open_file_path(self, path: Path, log_to_console: bool = True) -> None:
        open_file_path(self, path, log_to_console=log_to_console)

    def _restore_session(self) -> None:
        restore_session(self)

    def _save_session(self) -> None:
        save_session(self)

    def _normalize_settings_list(self, value) -> list[str]:
        return normalize_settings_list(self, value)

    def _restore_layout_state(self) -> None:
        restore_layout_state(self)

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        if not self._confirm_all_unsaved_before_exit():
            event.ignore()
            return
        self._save_session()
        super().closeEvent(event)

    def _close_tab(self, index: int) -> None:
        close_tab(self, index)

    def _on_tab_changed(self, _index: int) -> None:
        on_tab_changed(self, _index)

    def _on_path_renamed(self, old_path_raw: str, new_path_raw: str) -> None:
        on_path_renamed(self, old_path_raw, new_path_raw)

    def _on_path_deleted(self, deleted_path_raw: str) -> None:
        on_path_deleted(self, deleted_path_raw)

    def _get_active_editor(self) -> CodeEditor | None:
        return get_active_editor(self)

    def _get_active_file_path(self) -> Path | None:
        return get_active_file_path(self)

    def _current_tab_title(self) -> str:
        return current_tab_title(self)

    def _clear_outputs(self) -> None:
        clear_outputs(self)
