from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ide.code_editor import CodeEditor
from ide.theme import steins_gate_theme


def select_code_font(window) -> None:
    dialog = QDialog(window)
    dialog.setWindowTitle("Topografia")
    dialog.resize(760, 460)

    colors = steins_gate_theme.get_colors()
    dialog.setStyleSheet(
        f"""
        QDialog {{
            background-color: {colors.panel_bg};
            color: {colors.foreground};
        }}
        QLabel {{
            color: {colors.foreground};
        }}
        QListWidget, QLineEdit {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            selection-background-color: {colors.selection};
        }}
        QPushButton {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            padding: 4px 10px;
        }}
        QPushButton:hover {{
            background-color: {colors.hover};
        }}
        """
    )

    layout = QVBoxLayout(dialog)
    lists_row = QHBoxLayout()

    family_container = QVBoxLayout()
    style_container = QVBoxLayout()
    size_container = QVBoxLayout()

    family_label = QLabel("Font")
    style_label = QLabel("Font style")
    size_label = QLabel("Size")

    family_list = QListWidget(dialog)
    style_list = QListWidget(dialog)
    size_list = QListWidget(dialog)

    family_container.addWidget(family_label)
    family_container.addWidget(family_list)
    style_container.addWidget(style_label)
    style_container.addWidget(style_list)
    size_container.addWidget(size_label)
    size_container.addWidget(size_list)

    lists_row.addLayout(family_container, 4)
    lists_row.addLayout(style_container, 3)
    lists_row.addLayout(size_container, 2)
    layout.addLayout(lists_row)

    preview_label = QLabel("Sample")
    preview_edit = QLineEdit(dialog)
    preview_edit.setReadOnly(True)
    preview_edit.setMinimumHeight(36)
    layout.addWidget(preview_label)
    layout.addWidget(preview_edit)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
    reset_button = button_box.addButton("Restablecer", QDialogButtonBox.ResetRole)
    layout.addWidget(button_box)

    db = QFontDatabase()
    for family in db.families():
        family_list.addItem(family)

    def select_item_by_text(widget: QListWidget, value: str) -> None:
        for row in range(widget.count()):
            item = widget.item(row)
            if item and item.text() == value:
                widget.setCurrentRow(row)
                return
        if widget.count() > 0:
            widget.setCurrentRow(0)

    def select_item_by_size(widget: QListWidget, size: int) -> None:
        best_row = 0
        best_delta = 10_000
        for row in range(widget.count()):
            item = widget.item(row)
            if item is None:
                continue
            try:
                current_size = int(item.text())
            except ValueError:
                continue
            delta = abs(current_size - size)
            if delta < best_delta:
                best_delta = delta
                best_row = row
        if widget.count() > 0:
            widget.setCurrentRow(best_row)

    def selected_font() -> QFont:
        family_item = family_list.currentItem()
        style_item = style_list.currentItem()
        size_item = size_list.currentItem()

        family = family_item.text() if family_item else window._DEFAULT_CODE_FONT_FAMILY
        style = style_item.text() if style_item else "Regular"
        try:
            size = int(size_item.text()) if size_item else window._DEFAULT_CODE_FONT_SIZE
        except ValueError:
            size = window._DEFAULT_CODE_FONT_SIZE

        return db.font(family, style, size)

    def refresh_styles_and_sizes() -> None:
        family_item = family_list.currentItem()
        if family_item is None:
            return

        family = family_item.text()
        current_style = style_list.currentItem().text() if style_list.currentItem() else "Regular"
        style_list.clear()
        styles = db.styles(family) or ["Regular"]
        for style in styles:
            style_list.addItem(style)
        select_item_by_text(style_list, current_style)

        current_size = window._code_font.pointSize()
        size_list.clear()
        sizes = db.pointSizes(family)
        if not sizes:
            sizes = [6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32]
        for size in sizes:
            size_list.addItem(str(size))
        select_item_by_size(size_list, current_size)

    def update_preview() -> None:
        candidate_font = selected_font()
        preview_text = "AaBbYyZz 0123"
        metrics = QFontMetrics(candidate_font)
        supports_preview = all(metrics.inFont(char) for char in preview_text if char != " ")

        if supports_preview:
            preview_edit.setFont(candidate_font)
            preview_edit.setText(preview_text)
            return

        preview_edit.setFont(QFont(window._DEFAULT_CODE_FONT_FAMILY, window._DEFAULT_CODE_FONT_SIZE))
        preview_edit.setText("Sin vista previa para esta fuente")

    family_list.currentRowChanged.connect(lambda _row: (refresh_styles_and_sizes(), update_preview()))
    style_list.currentRowChanged.connect(lambda _row: update_preview())
    size_list.currentRowChanged.connect(lambda _row: update_preview())

    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    reset_button.clicked.connect(
        lambda: (
            select_item_by_text(family_list, window._DEFAULT_CODE_FONT_FAMILY),
            refresh_styles_and_sizes(),
            select_item_by_size(size_list, window._DEFAULT_CODE_FONT_SIZE),
            update_preview(),
        )
    )

    select_item_by_text(family_list, window._code_font.family())
    refresh_styles_and_sizes()
    select_item_by_text(style_list, db.styleString(window._code_font) or "Regular")
    select_item_by_size(size_list, window._code_font.pointSize())
    update_preview()

    if dialog.exec_() != QDialog.Accepted:
        return

    selected = selected_font()
    selected_size = selected.pointSize() if selected.pointSize() > 0 else window._code_font.pointSize()
    window._code_font = QFont(selected.family(), selected_size)
    apply_code_font_to_open_editors(window)
    window._settings.setValue("session/code_font_family", window._code_font.family())
    window._settings.setValue("session/code_font_size", window._code_font.pointSize())
    window._status.showMessage(f"Topografia aplicada: {window._code_font.family()} {window._code_font.pointSize()}pt", 3000)


def apply_code_font_to_open_editors(window) -> None:
    if window._editor_tabs is None:
        return

    for index in range(window._editor_tabs.count()):
        editor = window._editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            continue
        editor.setFont(window._code_font)
        editor.update_line_number_area_width(0)
        editor.viewport().update()
        editor.update()


def change_code_font_size(window, delta: int) -> None:
    current_size = window._code_font.pointSize() if window._code_font.pointSize() > 0 else window._DEFAULT_CODE_FONT_SIZE
    new_size = max(6, min(48, current_size + delta))
    if new_size == current_size:
        return

    window._code_font = QFont(window._code_font.family(), new_size)
    apply_code_font_to_open_editors(window)
    window._settings.setValue("session/code_font_family", window._code_font.family())
    window._settings.setValue("session/code_font_size", window._code_font.pointSize())
    window._status.showMessage(f"Topografia: {window._code_font.family()} {window._code_font.pointSize()}pt", 1500)


def apply_theme(window, theme_key: str, *, persist: bool = True, show_status: bool = True) -> None:
    if not steins_gate_theme.set_theme(theme_key):
        return

    app = QApplication.instance()
    if app is not None:
        app.setStyleSheet(steins_gate_theme.build_stylesheet())

    if window._editor_tabs is not None:
        for index in range(window._editor_tabs.count()):
            editor = window._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            editor.highlight_current_line()
            editor.viewport().update()
            editor.update()

    if persist:
        window._settings.setValue("session/theme", theme_key)

    if show_status:
        window._status.showMessage(f"Tema aplicado: {steins_gate_theme.get_theme_name(theme_key)}", 3000)


def open_theme_dialog(window) -> None:
    dialog = QDialog(window)
    dialog.setWindowTitle("Temas")
    dialog.resize(920, 500)
    colors = steins_gate_theme.get_colors()
    dialog.setStyleSheet(
        f"""
        QDialog {{
            background-color: {colors.panel_bg};
            color: {colors.foreground};
        }}
        QLabel {{
            color: {colors.foreground};
        }}
        QListWidget {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
        }}
        QListWidget::item:selected {{
            background-color: {colors.selection};
            color: {colors.foreground};
        }}
        QPlainTextEdit {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            selection-background-color: {colors.selection};
        }}
        QPushButton {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            padding: 4px 10px;
        }}
        QPushButton:hover {{
            background-color: {colors.hover};
        }}
        """
    )

    root_layout = QHBoxLayout(dialog)

    theme_list = QListWidget(dialog)
    theme_list.setMinimumWidth(250)
    for theme_key, theme_name in steins_gate_theme.list_themes():
        item = QListWidgetItem(theme_name)
        item.setData(Qt.UserRole, theme_key)
        theme_list.addItem(item)

    current_theme_key = steins_gate_theme.get_theme_key()
    for row in range(theme_list.count()):
        item = theme_list.item(row)
        if item.data(Qt.UserRole) == current_theme_key:
            theme_list.setCurrentRow(row)
            break

    right_panel = QWidget(dialog)
    right_layout = QVBoxLayout(right_panel)

    preview_code = QPlainTextEdit(right_panel)
    preview_code.setReadOnly(True)
    preview_code.setPlainText(
        "// Vista previa de tema\n"
        "gate {\n"
        "    let mensaje = \"El Psy Kongroo\";\n"
        "    dmail(mensaje);\n"
        "}\n"
    )

    preview_info = QFormLayout()
    label_background = QLabel(right_panel)
    label_foreground = QLabel(right_panel)
    label_accent = QLabel(right_panel)
    label_selection = QLabel(right_panel)
    preview_info.addRow("Fondo:", label_background)
    preview_info.addRow("Texto:", label_foreground)
    preview_info.addRow("Acento:", label_accent)
    preview_info.addRow("Selección:", label_selection)

    def apply_preview(theme_key: str) -> None:
        colors = steins_gate_theme.get_colors_for_theme(theme_key)
        swatch_style = "padding: 4px 8px; border: 1px solid {}; background-color: {}; color: {};"

        label_background.setText(colors.background)
        label_background.setStyleSheet(swatch_style.format(colors.border, colors.background, colors.foreground))
        label_foreground.setText(colors.foreground)
        label_foreground.setStyleSheet(swatch_style.format(colors.border, colors.panel_bg, colors.foreground))
        label_accent.setText(colors.accent)
        label_accent.setStyleSheet(swatch_style.format(colors.border, colors.accent, colors.background))
        label_selection.setText(colors.selection)
        label_selection.setStyleSheet(swatch_style.format(colors.border, colors.selection, colors.foreground))

        preview_code.setStyleSheet(
            f""
            f"QPlainTextEdit {{"
            f"background-color: {colors.background};"
            f"color: {colors.foreground};"
            f"selection-background-color: {colors.selection};"
            f"border: 1px solid {colors.border};"
            f"}}"
        )

    def on_theme_selected() -> None:
        selected_item = theme_list.currentItem()
        if selected_item is None:
            return
        selected_key = str(selected_item.data(Qt.UserRole))
        apply_preview(selected_key)

    theme_list.currentRowChanged.connect(lambda _row: on_theme_selected())
    on_theme_selected()

    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    right_layout.addLayout(preview_info)
    right_layout.addWidget(preview_code, 1)
    right_layout.addWidget(buttons)

    root_layout.addWidget(theme_list)
    root_layout.addWidget(right_panel, 1)

    if dialog.exec_() != QDialog.Accepted:
        return

    selected_item = theme_list.currentItem()
    if selected_item is None:
        return
    selected_key = str(selected_item.data(Qt.UserRole))
    apply_theme(window, selected_key)
