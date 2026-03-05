from __future__ import annotations

import datetime
import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from ide.code_editor import CodeEditor
from ide.compiler_runner import run_compiler
from ide.theme import steins_gate_theme


def set_autosave_enabled(window, enabled: bool, *, persist: bool = True) -> None:
    window._autosave_enabled = enabled
    if window._autosave_enabled:
        window._autosave_timer.start()
    else:
        window._autosave_timer.stop()

    if persist:
        window._settings.setValue("session/autosave_enabled", window._autosave_enabled)


def auto_save_open_files(window) -> None:
    if window._editor_tabs is None:
        return

    saved_count = 0
    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue
        if not bool(editor.property("unsaved")):
            continue

        file_path_raw = editor.property("file_path")
        if not file_path_raw:
            continue

        path = Path(str(file_path_raw))
        if not path.exists() or not path.is_file():
            continue

        if write_editor_to_path(window, editor, path):
            saved_count += 1

    if saved_count > 0 and window._console_panel is not None:
        window._console_panel.append_console(f"Autoguardado: {saved_count} archivo(s).")


def write_editor_to_path(window, editor: CodeEditor, path: Path) -> bool:
    path_key = str(path.resolve())
    window._suppress_file_watch_event.add(path_key)
    try:
        path.write_text(editor.toPlainText(), encoding="utf-8")
    except OSError:
        return False
    finally:
        window._suppress_file_watch_event.discard(path_key)

    editor.setProperty("unsaved", False)
    watch_file(window, path)
    return True


def save_editor_as(window, editor: CodeEditor, index: int | None = None) -> bool:
    dialog = create_themed_file_dialog(
        window,
        title="Guardar archivo",
        accept_mode=QFileDialog.AcceptSave,
        file_mode=QFileDialog.AnyFile,
        name_filters=[
            "Archivos Skuld (*.stn)",
            "Archivos de texto (*.txt)",
            "Todos los archivos (*.*)",
        ],
        selected_filter="Archivos Skuld (*.stn)",
        default_suffix="stn",
    )
    if dialog.exec_() != QDialog.Accepted:
        return False

    selected_files = dialog.selectedFiles()
    if not selected_files:
        return False

    file_path = selected_files[0]

    path = Path(file_path)
    if not write_editor_to_path(window, editor, path):
        QMessageBox.warning(window, "Guardar", f"No fue posible guardar el archivo:\n{path}")
        return False

    editor.setProperty("file_path", str(path))
    tab_index = index if index is not None else (window._editor_tabs.currentIndex() if window._editor_tabs is not None else -1)
    if window._editor_tabs is not None and tab_index >= 0:
        window._editor_tabs.setTabText(tab_index, path.name)
        window._editor_tabs.setTabToolTip(tab_index, str(path))

    if window._file_explorer is not None:
        window._file_explorer.refresh()
        window._file_explorer.add_open_file(str(path))
    return True


def save_editor(window, editor: CodeEditor, index: int | None = None) -> bool:
    file_path_raw = editor.property("file_path")
    if not file_path_raw:
        return save_editor_as(window, editor, index=index)

    path = Path(str(file_path_raw))
    if not write_editor_to_path(window, editor, path):
        QMessageBox.warning(window, "Guardar", f"No fue posible guardar el archivo:\n{path}")
        return False

    if window._file_explorer is not None:
        window._file_explorer.refresh()
    return True


def collect_unsaved_tab_indexes(window) -> list[int]:
    if window._editor_tabs is None:
        return []
    result: list[int] = []
    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if isinstance(editor, CodeEditor) and bool(editor.property("unsaved")):
            result.append(index)
    return result


def confirm_unsaved_for_tab(window, index: int) -> bool:
    if window._editor_tabs is None:
        return True
    editor = window._editor_tabs.widget(index)
    if not isinstance(editor, CodeEditor) or not bool(editor.property("unsaved")):
        return True

    tab_name = window._editor_tabs.tabText(index) or "Sin título"
    choice = QMessageBox.question(
        window,
        "Cambios sin guardar",
        f"El archivo '{tab_name}' tiene cambios sin guardar.\n\n¿Deseas guardar antes de cerrar?",
        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        QMessageBox.Save,
    )
    if choice == QMessageBox.Cancel:
        return False
    if choice == QMessageBox.Discard:
        return True

    if window._editor_tabs.currentIndex() != index:
        window._editor_tabs.setCurrentIndex(index)
    active_editor = get_active_editor(window)
    if active_editor is None:
        return False
    return save_editor(window, active_editor, index=index)


def confirm_all_unsaved_before_exit(window) -> bool:
    for index in sorted(collect_unsaved_tab_indexes(window), reverse=True):
        if not confirm_unsaved_for_tab(window, index):
            return False
    return True


def watch_file(window, path: Path) -> None:
    resolved_str = str(path.resolve())
    if not path.exists() or not path.is_file():
        return
    if resolved_str not in window._file_watcher.files():
        window._file_watcher.addPath(resolved_str)
    window._watched_files_mtime[resolved_str] = path.stat().st_mtime


def unwatch_file_if_unused(window, path: Path) -> None:
    resolved = path.resolve()
    resolved_str = str(resolved)

    if window._editor_tabs is not None:
        for index in range(window._editor_tabs.count()):
            editor = window._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            tab_path_raw = editor.property("file_path")
            if not tab_path_raw:
                continue
            if Path(str(tab_path_raw)).resolve() == resolved:
                return

    if resolved_str in window._file_watcher.files():
        window._file_watcher.removePath(resolved_str)
    window._watched_files_mtime.pop(resolved_str, None)


def reload_editor_from_disk(window, editor: CodeEditor, path: Path) -> bool:
    try:
        content: str | None = None
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                content = path.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        if content is None:
            return False
    except OSError:
        return False

    editor.blockSignals(True)
    editor.setPlainText(content)
    editor.blockSignals(False)
    editor.setProperty("unsaved", False)
    if window._search_text:
        editor.set_search_highlights(window._search_text)
    return True


def on_watched_file_changed(window, file_path: str) -> None:
    if file_path in window._suppress_file_watch_event:
        watch_file(window, Path(file_path))
        return

    changed_path = Path(file_path)
    if not changed_path.exists() or not changed_path.is_file():
        return

    current_mtime = changed_path.stat().st_mtime
    previous_mtime = window._watched_files_mtime.get(file_path)
    if previous_mtime is not None and current_mtime <= previous_mtime:
        watch_file(window, changed_path)
        return

    watch_file(window, changed_path)

    if window._editor_tabs is None:
        return

    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue
        tab_path_raw = editor.property("file_path")
        if not tab_path_raw:
            continue

        tab_path = Path(str(tab_path_raw)).resolve()
        if tab_path != changed_path.resolve():
            continue

        if bool(editor.property("unsaved")):
            QMessageBox.information(
                window,
                "Archivo actualizado externamente",
                f"El archivo cambió fuera de la IDE y esta pestaña tiene cambios sin guardar:\n{tab_path.name}",
            )
            continue

        reload_choice = QMessageBox.question(
            window,
            "Archivo actualizado externamente",
            f"El archivo cambió fuera de la IDE:\n{tab_path.name}\n\n¿Deseas recargarlo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reload_choice == QMessageBox.Yes:
            reload_editor_from_disk(window, editor, tab_path)
            if window._editor_tabs.currentIndex() == index:
                window._update_cursor_status()


def new_file(window, with_example: bool = False) -> None:
    if window._editor_tabs is None:
        return

    editor = CodeEditor()
    editor.setReadOnly(False)
    editor.setFocusPolicy(Qt.StrongFocus)
    editor.setFont(window._code_font)
    if with_example:
        editor.setPlainText(window._load_example_code())
    window._bind_editor_events(editor)
    editor.setProperty("file_path", "")
    editor.set_search_highlights(window._search_text)

    tab_title = f"Sin título {window._untitled_counter}"
    window._untitled_counter += 1
    tab_index = window._editor_tabs.addTab(editor, tab_title)
    window._editor_tabs.setCurrentIndex(tab_index)

    if window._console_panel is not None:
        window._console_panel.append_console("Nuevo archivo creado.")
    editor.setFocus()
    window._update_cursor_status()


def open_file(window) -> None:
    dialog = create_themed_file_dialog(
        window,
        title="Abrir archivo",
        accept_mode=QFileDialog.AcceptOpen,
        file_mode=QFileDialog.ExistingFile,
        name_filters=[
            "Archivos compatibles (*.stn *.txt)",
            "Archivos Skuld (*.stn)",
            "Archivos de texto (*.txt)",
            "Todos los archivos (*.*)",
        ],
        selected_filter="Archivos compatibles (*.stn *.txt)",
    )
    if dialog.exec_() != QDialog.Accepted:
        return

    selected_files = dialog.selectedFiles()
    if not selected_files:
        return

    open_file_path(window, Path(selected_files[0]))


def open_folder(window) -> None:
    dialog = create_themed_file_dialog(
        window,
        title="Seleccionar carpeta",
        accept_mode=QFileDialog.AcceptOpen,
        file_mode=QFileDialog.Directory,
    )
    dialog.setOption(QFileDialog.ShowDirsOnly, True)
    if dialog.exec_() != QDialog.Accepted:
        return

    selected_paths = dialog.selectedFiles()
    if not selected_paths:
        return

    folder_path = selected_paths[0]
    if not folder_path:
        return
    if window._file_explorer is not None:
        window._file_explorer.add_root_path(folder_path)
    if window._console_panel is not None:
        window._console_panel.append_console(f"Carpeta agregada: {Path(folder_path).name}")


def create_themed_file_dialog(
    window,
    *,
    title: str,
    accept_mode: QFileDialog.AcceptMode,
    file_mode: QFileDialog.FileMode,
    name_filters: list[str] | None = None,
    selected_filter: str | None = None,
    default_suffix: str | None = None,
) -> QFileDialog:
    dialog = QFileDialog(window, title)
    dialog.setOption(QFileDialog.DontUseNativeDialog, os.name != "nt")
    dialog.setAcceptMode(accept_mode)
    dialog.setFileMode(file_mode)

    if name_filters:
        dialog.setNameFilters(name_filters)
        if selected_filter:
            dialog.selectNameFilter(selected_filter)

    if default_suffix:
        dialog.setDefaultSuffix(default_suffix)

    if os.name == "nt":
        return dialog

    colors = steins_gate_theme.get_colors()
    dialog.setStyleSheet(
        f"""
        QFileDialog {{
            background-color: {colors.panel_bg};
            color: {colors.foreground};
        }}
        QFileDialog QLabel {{
            color: {colors.foreground};
        }}
        QFileDialog QLineEdit,
        QFileDialog QComboBox,
        QFileDialog QSpinBox {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            selection-background-color: {colors.selection};
        }}
        QFileDialog QToolButton,
        QFileDialog QPushButton {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            padding: 4px 10px;
        }}
        QFileDialog QToolButton:hover,
        QFileDialog QPushButton:hover {{
            background-color: {colors.hover};
        }}
        QFileDialog QTreeView,
        QFileDialog QListView,
        QFileDialog QTableView {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            alternate-background-color: {colors.panel_bg};
            selection-background-color: {colors.selection};
            selection-color: {colors.foreground};
        }}
        QFileDialog QHeaderView::section {{
            background-color: {colors.panel_bg};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            padding: 4px;
        }}
        """
    )
    return dialog


def save_file(window) -> None:
    editor = get_active_editor(window)
    if not editor:
        return
    if not save_editor(window, editor):
        return
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    current_file = get_active_file_path(window)
    if window._console_panel is not None:
        name = current_file.name if current_file is not None else "archivo"
        window._console_panel.append_console(f"Archivo guardado: {name}")
    window._status.showMessage(f"Guardado · {now}")
    window._update_cursor_status()


def save_file_as(window) -> None:
    editor = get_active_editor(window)
    if not editor:
        return
    if not save_editor_as(window, editor):
        return
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    path = get_active_file_path(window)
    if window._console_panel is not None:
        name = path.name if path is not None else "archivo"
        window._console_panel.append_console(f"Archivo guardado: {name}")
    window._status.showMessage(f"Guardado · {now}")
    window._update_cursor_status()


def close_file(window) -> None:
    if window._editor_tabs is None:
        return

    current_index = window._editor_tabs.currentIndex()
    if current_index >= 0:
        close_tab(window, current_index)

    if window._console_panel is not None:
        window._console_panel.append_console("Archivo cerrado.")
    window._update_cursor_status()


def run_phase(window, phase: str) -> None:
    editor = get_active_editor(window)
    if not editor:
        return

    current_file = get_active_file_path(window)
    if not current_file:
        save_file_as(window)
        current_file = get_active_file_path(window)
        if not current_file:
            return

    save_file(window)
    result = run_compiler(phase, str(current_file))

    if result.returncode != 0:
        if window._console_panel is not None:
            window._console_panel.append_errors(result.stderr or "Error ejecutando el compilador.")
        return

    output_text = result.stdout or "(sin salida)"
    if phase == "lexico":
        window._analysis_panel.set_tokens(output_text)
    elif phase == "sintactico":
        window._analysis_panel.set_syntax(output_text)
    elif phase == "semantico":
        window._analysis_panel.set_semantic(output_text)
    elif phase == "intermedio":
        window._analysis_panel.set_intermediate(output_text)
    elif phase == "ejecucion":
        if window._console_panel is not None:
            window._console_panel.append_execution(output_text)

    if window._console_panel is not None:
        window._console_panel.append_console(f"Fase ejecutada: {phase}")


def open_file_from_explorer(window, file_path: str) -> None:
    if window._console_panel is not None:
        window._console_panel.append_console(f"Solicitud abrir desde explorador: {Path(file_path).name}")
    open_file_path(window, Path(file_path))


def close_file_from_explorer(window, file_path: str) -> None:
    if window._editor_tabs is None:
        return
    resolved = Path(file_path).resolve()
    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        tab_file_raw = editor.property("file_path") if editor else None
        if not tab_file_raw:
            continue
        if Path(str(tab_file_raw)).resolve() == resolved:
            close_tab(window, index)
            return
    if window._file_explorer is not None:
        window._file_explorer.remove_open_file(file_path)


def open_file_path(window, path: Path, log_to_console: bool = True) -> None:
    if window._editor_tabs is None:
        return

    if not path.exists() or not path.is_file():
        QMessageBox.warning(
            window,
            "No se puede abrir",
            f"El archivo no existe o no es valido:\n{path}",
        )
        return

    if window._file_explorer is not None:
        window._file_explorer.add_open_file(str(path))

    resolved = path.resolve()
    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue
        tab_file_raw = editor.property("file_path")
        if not tab_file_raw:
            continue
        tab_file = Path(str(tab_file_raw)).resolve()
        if tab_file == resolved:
            window._editor_tabs.setCurrentIndex(index)
            watch_file(window, path)
            if log_to_console and window._console_panel is not None:
                window._console_panel.append_console(f"Archivo abierto: {path.name}")
            active_editor = get_active_editor(window)
            if active_editor:
                active_editor.setFocus()
            window._update_cursor_status()
            return

    editor = CodeEditor()
    editor.setReadOnly(False)
    editor.setFocusPolicy(Qt.StrongFocus)
    editor.setFont(window._code_font)
    try:
        content: str | None = None
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                content = path.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        if content is None:
            QMessageBox.warning(
                window,
                "No se puede abrir",
                f"No se pudo detectar la codificacion del archivo:\n{path}",
            )
            return
        editor.setPlainText(content)
    except OSError as exc:
        QMessageBox.warning(
            window,
            "No se puede abrir",
            f"No fue posible abrir el archivo:\n{path}\n\n{exc}",
        )
        return
    window._bind_editor_events(editor)
    editor.setProperty("file_path", str(path))
    if window._search_text:
        editor.set_search_highlights(window._search_text)

    tab_index = window._editor_tabs.addTab(editor, path.name)
    window._editor_tabs.setTabToolTip(tab_index, str(path))
    window._editor_tabs.setCurrentIndex(tab_index)
    watch_file(window, path)
    if log_to_console and window._console_panel is not None:
        window._console_panel.append_console(f"Archivo abierto: {path.name}")
    editor.setFocus()
    window._update_cursor_status()


def restore_session(window) -> None:
    if window._file_explorer is None:
        return

    folder_paths = normalize_settings_list(window, window._settings.value("session/folders", []))
    open_files = normalize_settings_list(window, window._settings.value("session/open_files", []))
    active_file = str(window._settings.value("session/active_file", "") or "")

    if folder_paths:
        window._file_explorer.set_root_paths(folder_paths)

    opened_any = False
    for file_path in open_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            open_file_path(window, path, log_to_console=False)
            opened_any = True

    if not opened_any:
        new_file(window, with_example=True)
        return

    if active_file and window._editor_tabs is not None:
        active_path = Path(active_file)
        for index in range(window._editor_tabs.count()):
            editor = window._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            tab_file_raw = editor.property("file_path")
            if not tab_file_raw:
                continue
            tab_path = Path(str(tab_file_raw))
            if tab_path == active_path:
                window._editor_tabs.setCurrentIndex(index)
                break

        restore_layout_state(window)


def save_session(window) -> None:
    folders: list[str] = []
    if window._file_explorer is not None:
        folders = window._file_explorer.get_root_paths()

    open_files: list[str] = []
    if window._editor_tabs is not None:
        for index in range(window._editor_tabs.count()):
            editor = window._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            file_path_raw = editor.property("file_path")
            if not file_path_raw:
                continue
            file_path = Path(str(file_path_raw))
            if file_path.exists() and file_path.is_file():
                open_files.append(str(file_path))

    active_file = ""
    active_path = get_active_file_path(window)
    if active_path is not None:
        active_file = str(active_path)

    window._settings.setValue("session/folders", folders)
    window._settings.setValue("session/open_files", open_files)
    window._settings.setValue("session/active_file", active_file)
    window._settings.setValue("session/theme", steins_gate_theme.get_theme_key())
    window._settings.setValue("session/autosave_enabled", window._autosave_enabled)
    window._settings.setValue("session/code_font_family", window._code_font.family())
    window._settings.setValue("session/code_font_size", window._code_font.pointSize())
    window._settings.setValue("session/analysis_visible", window._analysis_container.isVisible() if window._analysis_container is not None else True)
    window._settings.setValue("session/console_visible", window._console_container.isVisible() if window._console_container is not None else True)
    window._settings.setValue("session/explorer_visible", window._file_explorer.isVisible() if window._file_explorer is not None else True)
    window._settings.setValue("session/analysis_minimized", window._analysis_minimized)
    window._settings.setValue("session/console_minimized", window._console_minimized)
    if window._top_splitter is not None:
        window._settings.setValue("session/top_splitter_sizes", window._top_splitter.sizes())
    if window._main_splitter is not None:
        window._settings.setValue("session/main_splitter_sizes", window._main_splitter.sizes())
    window._settings.sync()


def normalize_settings_list(window, value) -> list[str]:
    del window
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [text]


def restore_layout_state(window) -> None:
    analysis_visible = bool(window._settings.value("session/analysis_visible", True, type=bool))
    console_visible = bool(window._settings.value("session/console_visible", True, type=bool))
    explorer_visible = bool(window._settings.value("session/explorer_visible", True, type=bool))
    window._analysis_minimized = bool(window._settings.value("session/analysis_minimized", False, type=bool))
    window._console_minimized = bool(window._settings.value("session/console_minimized", False, type=bool))

    top_sizes = normalize_settings_list(window, window._settings.value("session/top_splitter_sizes", []))
    main_sizes = normalize_settings_list(window, window._settings.value("session/main_splitter_sizes", []))

    if window._analysis_container is not None:
        window._analysis_container.setVisible(analysis_visible)
    if window._console_container is not None:
        window._console_container.setVisible(console_visible)
    if window._file_explorer is not None:
        window._file_explorer.setVisible(explorer_visible)

    if window._analysis_panel is not None:
        window._analysis_panel.setVisible(analysis_visible and not window._analysis_minimized)
    if window._console_panel is not None:
        window._console_panel.setVisible(console_visible and not window._console_minimized)

    if window._top_splitter is not None and top_sizes:
        parsed_top_sizes = [int(value) for value in top_sizes if str(value).strip()]
        if parsed_top_sizes:
            window._top_splitter.setSizes(parsed_top_sizes)
            window._top_sizes_before_analysis_toggle = parsed_top_sizes

    if window._main_splitter is not None and main_sizes:
        parsed_main_sizes = [int(value) for value in main_sizes if str(value).strip()]
        if parsed_main_sizes:
            window._main_splitter.setSizes(parsed_main_sizes)
            window._main_sizes_before_console_toggle = parsed_main_sizes

    if window._analysis_minimized and window._analysis_container is not None:
        window._analysis_container.setVisible(False)
    if window._console_minimized and window._console_container is not None:
        window._console_container.setVisible(False)
    if not explorer_visible and window._file_explorer is not None:
        window._file_explorer.setVisible(False)


def close_tab(window, index: int) -> None:
    if window._editor_tabs is None:
        return
    if not confirm_unsaved_for_tab(window, index):
        return

    widget = window._editor_tabs.widget(index)
    if widget and window._file_explorer is not None:
        file_path_raw = widget.property("file_path")
        if file_path_raw:
            window._file_explorer.remove_open_file(str(file_path_raw))
            unwatch_file_if_unused(window, Path(str(file_path_raw)))
    window._editor_tabs.removeTab(index)
    if widget:
        widget.deleteLater()
    if window._editor_tabs.count() == 0:
        new_file(window)


def on_tab_changed(window, _index: int) -> None:
    editor = get_active_editor(window)
    if editor:
        editor.setReadOnly(False)
        editor.set_search_highlights(window._search_text)
        window._update_find_match_label()
        editor.setFocus()
    window._update_cursor_status()


def on_path_renamed(window, old_path_raw: str, new_path_raw: str) -> None:
    old_path = Path(old_path_raw).resolve()
    new_path = Path(new_path_raw).resolve()

    if window._editor_tabs is None:
        return

    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue

        tab_file_raw = editor.property("file_path")
        if not tab_file_raw:
            continue

        tab_path = Path(str(tab_file_raw)).resolve()
        updated_path: Path | None = None

        if tab_path == old_path:
            updated_path = new_path
        elif old_path.is_dir() and tab_path.is_relative_to(old_path):
            updated_path = new_path / tab_path.relative_to(old_path)

        if updated_path is None:
            continue

        editor.setProperty("file_path", str(updated_path))
        window._editor_tabs.setTabText(index, updated_path.name)
        window._editor_tabs.setTabToolTip(index, str(updated_path))
        unwatch_file_if_unused(window, tab_path)
        watch_file(window, updated_path)


def on_path_deleted(window, deleted_path_raw: str) -> None:
    deleted_path = Path(deleted_path_raw).resolve()

    if window._editor_tabs is None:
        return

    indexes_to_close: list[int] = []
    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue
        tab_file_raw = editor.property("file_path")
        if not tab_file_raw:
            continue
        tab_path = Path(str(tab_file_raw)).resolve()
        if tab_path == deleted_path or (deleted_path.is_dir() and tab_path.is_relative_to(deleted_path)):
            indexes_to_close.append(index)

    for index in sorted(indexes_to_close, reverse=True):
        widget = window._editor_tabs.widget(index)
        if widget is not None:
            file_path_raw = widget.property("file_path")
            if file_path_raw:
                unwatch_file_if_unused(window, Path(str(file_path_raw)))
        window._editor_tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

    if indexes_to_close and window._editor_tabs.count() == 0:
        new_file(window)


def get_active_editor(window) -> CodeEditor | None:
    if window._editor_tabs is None:
        return None
    widget = window._editor_tabs.currentWidget()
    if isinstance(widget, CodeEditor):
        return widget
    return None


def get_active_file_path(window) -> Path | None:
    editor = get_active_editor(window)
    if not editor:
        return None
    file_path_raw = editor.property("file_path")
    if not file_path_raw:
        return None
    return Path(str(file_path_raw))


def current_tab_title(window) -> str:
    if window._editor_tabs is None:
        return "Sin archivo"
    current_index = window._editor_tabs.currentIndex()
    if current_index < 0:
        return "Sin archivo"
    return window._editor_tabs.tabText(current_index) or "Sin archivo"


def clear_outputs(window) -> None:
    if window._analysis_panel is not None:
        window._analysis_panel.set_tokens("")
        window._analysis_panel.set_syntax("")
        window._analysis_panel.set_semantic("")
        window._analysis_panel.set_intermediate("")
        window._analysis_panel.set_symbols("")
    if window._console_panel is not None:
        window._console_panel.clear_all()
