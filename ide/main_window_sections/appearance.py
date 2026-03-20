from __future__ import annotations

import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ide.code_editor import CodeEditor
from ide.theme import steins_gate_theme
from ide.theme.steins_gate_theme import ErrorColors, ThemeColors


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
        preview_text = "Skuld Preview 0123 // El Psy Kongroo"
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
            editor.refresh_syntax_theme()
            editor.highlight_current_line()
            editor.viewport().update()
            editor.update()

    if window._console_panel is not None:
        window._console_panel.refresh_theme()

    if persist:
        window._settings.setValue("session/theme", theme_key)

    if show_status:
        window._status.showMessage(f"Tema aplicado: {steins_gate_theme.get_theme_name(theme_key)}", 3000)


def open_theme_dialog(window) -> None:
    dialog = QDialog(window)
    dialog.setWindowTitle("Temas")
    dialog.resize(1280, 760)
    dialog.setMinimumSize(1140, 680)
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
        QLabel#theme_title {{
            font-size: 15px;
            font-weight: 600;
            padding: 4px 0;
        }}
        QLabel#section_title {{
            font-size: 12px;
            font-weight: 600;
            color: {colors.accent};
            padding-top: 4px;
        }}
        QLabel#color_chip {{
            border: 1px solid {colors.border};
            border-radius: 3px;
            min-height: 24px;
            padding: 2px 6px;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            font-weight: 600;
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
        QLineEdit {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
            selection-background-color: {colors.selection};
            min-height: 24px;
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
    root_layout.setSpacing(12)

    left_panel = QWidget(dialog)
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)

    left_title = QLabel("Temas disponibles", left_panel)
    left_title.setObjectName("section_title")
    theme_list = QListWidget(left_panel)
    theme_list.setMinimumWidth(290)

    for theme_key, theme_name in steins_gate_theme.list_themes():
        item = QListWidgetItem(theme_name)
        item.setData(Qt.UserRole, theme_key)
        theme_list.addItem(item)

    left_layout.addWidget(left_title)
    left_layout.addWidget(theme_list, 1)

    right_panel = QWidget(dialog)
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(8)

    selected_theme_label = QLabel(right_panel)
    selected_theme_label.setObjectName("theme_title")
    right_layout.addWidget(selected_theme_label)

    actions_row = QHBoxLayout()
    reset_button = QPushButton("Restablecer tema seleccionado", right_panel)
    actions_row.addWidget(reset_button)
    actions_row.addStretch(1)
    right_layout.addLayout(actions_row)

    tabs = QTabWidget(right_panel)
    right_layout.addWidget(tabs, 1)

    tab_active = QWidget(tabs)
    tab_base = QWidget(tabs)
    tab_errors = QWidget(tabs)
    tabs.addTab(tab_active, "Paleta activa")
    tabs.addTab(tab_base, "Paleta base")
    tabs.addTab(tab_errors, "Colores de error")

    active_layout = QVBoxLayout(tab_active)
    active_layout.setContentsMargins(8, 8, 8, 8)
    active_layout.setSpacing(8)

    active_group_title = QLabel("Colores aplicados", tab_active)
    active_group_title.setObjectName("section_title")
    active_layout.addWidget(active_group_title)

    active_scroll = QScrollArea(tab_active)
    active_scroll.setWidgetResizable(True)
    active_scroll_content = QWidget(active_scroll)
    active_form = QFormLayout(active_scroll_content)
    active_form.setContentsMargins(6, 6, 6, 6)
    active_form.setSpacing(6)
    active_scroll.setWidget(active_scroll_content)
    active_layout.addWidget(active_scroll, 1)

    preview_code = QPlainTextEdit(tab_active)
    preview_code.setReadOnly(True)
    preview_code.setMinimumHeight(180)
    preview_code.setPlainText(
        "<> Vista previa de tema\n"
        "labmem worldline mensaje = \"El Psy Kongroo\";\n"
        "gate {\n"
        "    dmail(mensaje);\n"
        "}\n"
    )
    active_layout.addWidget(preview_code)

    base_layout = QVBoxLayout(tab_base)
    base_layout.setContentsMargins(8, 8, 8, 8)
    base_layout.setSpacing(8)
    base_form = QFormLayout()
    base_layout.addLayout(base_form)
    base_layout.addStretch(1)

    error_layout = QVBoxLayout(tab_errors)
    error_layout.setContentsMargins(8, 8, 8, 8)
    error_layout.setSpacing(8)
    error_form = QFormLayout()
    error_layout.addLayout(error_form)
    error_layout.addStretch(1)

    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    right_layout.addWidget(buttons)

    color_field_labels = [
        ("background", "Fondo"),
        ("foreground", "Texto"),
        ("keywords", "Palabras clave"),
        ("strings", "Cadenas"),
        ("comments", "Comentarios"),
        ("numbers", "Números"),
        ("operators", "Operadores"),
        ("selection", "Selección"),
        ("accent", "Acento"),
        ("panel_bg", "Panel"),
        ("border", "Borde"),
        ("hover", "Hover"),
    ]
    error_field_labels = [
        ("err_underline", "Error subrayado"),
        ("err_background", "Error fondo"),
        ("err_text", "Error texto"),
        ("err_border", "Error borde"),
    ]

    active_chips: dict[str, QLabel] = {}
    edit_fields: dict[str, QLineEdit] = {}
    edit_chips: dict[str, QLabel] = {}
    edit_buttons: dict[str, QPushButton] = {}
    current_payload: dict[str, str] = {}
    selected_theme_key = {"value": steins_gate_theme.get_theme_key()}

    def contrast_text(hex_color: str) -> str:
        color = QColor(hex_color)
        if not color.isValid():
            return colors.foreground
        return "#111111" if color.lightness() > 140 else "#f8f8f8"

    def style_color_chip(chip: QLabel, color_hex: str, *, border_color: str | None = None) -> None:
        valid = QColor(color_hex).isValid()
        border = border_color or colors.border
        chip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if not valid:
            chip.setText(" INVALIDO")
            chip.setStyleSheet(
                f"background-color: {colors.panel_bg}; color: {colors.foreground}; border: 1px dashed {border};"
            )
            return

        normalized = QColor(color_hex).name().upper()
        chip.setText(f" {normalized}")
        chip.setStyleSheet(
            f"background-color: {QColor(color_hex).name()}; color: {contrast_text(color_hex)}; border: 1px solid {border};"
        )

    for key, label in [*color_field_labels, *error_field_labels]:
        chip = QLabel(active_scroll_content)
        chip.setObjectName("color_chip")
        chip.setMinimumWidth(260)
        chip.setMinimumHeight(24)
        active_form.addRow(f"{label}:", chip)
        active_chips[key] = chip

    def create_editor_row(layout: QFormLayout, key: str, label: str, parent: QWidget) -> None:
        row_widget = QWidget(parent)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        chip = QLabel(row_widget)
        chip.setObjectName("color_chip")
        chip.setFixedWidth(120)
        chip.setMinimumHeight(24)

        line = QLineEdit(row_widget)
        line.setPlaceholderText("#RRGGBB")

        button = QPushButton("Color", row_widget)
        button.setFixedWidth(66)

        def pick_color() -> None:
            initial = QColor(line.text().strip() or "#000000")
            picked = QColorDialog.getColor(initial, dialog, f"Seleccionar color: {label}")
            if not picked.isValid():
                return
            line.setText(picked.name().upper())

        def on_changed(_text: str) -> None:
            style_color_chip(chip, line.text().strip())
            payload = read_payload_from_fields()
            if payload is not None:
                apply_preview(payload, selected_theme_key["value"])

        button.clicked.connect(pick_color)
        line.textChanged.connect(on_changed)

        row_layout.addWidget(chip)
        row_layout.addWidget(line, 1)
        row_layout.addWidget(button)
        layout.addRow(f"{label}:", row_widget)

        edit_fields[key] = line
        edit_chips[key] = chip
        edit_buttons[key] = button

    def theme_payload(theme_key: str) -> dict[str, str]:
        theme_colors = steins_gate_theme.get_colors_for_theme(theme_key)
        error_colors = steins_gate_theme.get_error_colors_for_theme(theme_key)
        return {
            "background": theme_colors.background,
            "foreground": theme_colors.foreground,
            "keywords": theme_colors.keywords,
            "strings": theme_colors.strings,
            "comments": theme_colors.comments,
            "numbers": theme_colors.numbers,
            "operators": theme_colors.operators,
            "selection": theme_colors.selection,
            "accent": theme_colors.accent,
            "panel_bg": theme_colors.panel_bg,
            "border": theme_colors.border,
            "hover": theme_colors.hover,
            "err_underline": error_colors.underline,
            "err_background": error_colors.background,
            "err_text": error_colors.text,
            "err_border": error_colors.border,
        }

    def default_theme_payload(theme_key: str) -> dict[str, str]:
        theme_colors = steins_gate_theme.get_default_colors_for_theme(theme_key)
        error_colors = steins_gate_theme.get_default_error_colors_for_theme(theme_key)
        return {
            "background": theme_colors.background,
            "foreground": theme_colors.foreground,
            "keywords": theme_colors.keywords,
            "strings": theme_colors.strings,
            "comments": theme_colors.comments,
            "numbers": theme_colors.numbers,
            "operators": theme_colors.operators,
            "selection": theme_colors.selection,
            "accent": theme_colors.accent,
            "panel_bg": theme_colors.panel_bg,
            "border": theme_colors.border,
            "hover": theme_colors.hover,
            "err_underline": error_colors.underline,
            "err_background": error_colors.background,
            "err_text": error_colors.text,
            "err_border": error_colors.border,
        }

    def payload_to_objects(payload: dict[str, str]) -> tuple[ThemeColors, ErrorColors]:
        return (
            ThemeColors(
                background=payload["background"],
                foreground=payload["foreground"],
                keywords=payload["keywords"],
                strings=payload["strings"],
                comments=payload["comments"],
                numbers=payload["numbers"],
                operators=payload["operators"],
                selection=payload["selection"],
                accent=payload["accent"],
                panel_bg=payload["panel_bg"],
                border=payload["border"],
                hover=payload["hover"],
            ),
            ErrorColors(
                underline=payload["err_underline"],
                background=payload["err_background"],
                text=payload["err_text"],
                border=payload["err_border"],
            ),
        )

    def read_payload_from_fields() -> dict[str, str] | None:
        payload: dict[str, str] = {}
        for key, line in edit_fields.items():
            value = line.text().strip()
            if not QColor(value).isValid():
                return None
            payload[key] = QColor(value).name().upper()
        return payload

    def fill_fields(payload: dict[str, str]) -> None:
        for key, line in edit_fields.items():
            line.setText(payload.get(key, ""))
            style_color_chip(edit_chips[key], payload.get(key, ""))

    def apply_preview(payload: dict[str, str], theme_key: str) -> None:
        theme_name = steins_gate_theme.get_theme_name(theme_key)
        selected_theme_label.setText(f"Tema en vista: {theme_name}  ({theme_key})")

        tabs.setStyleSheet(
            f""
            f"QTabWidget::pane {{"
            f"border: 1px solid {payload['border']};"
            f"background-color: {payload['panel_bg']};"
            f"}}"
            f"QTabBar::tab {{"
            f"background-color: {payload['panel_bg']};"
            f"color: {payload['foreground']};"
            f"border: 1px solid {payload['border']};"
            f"padding: 5px 10px;"
            f"}}"
            f"QTabBar::tab:selected {{"
            f"background-color: {payload['background']};"
            f"color: {payload['accent']};"
            f"}}"
        )
        tab_active.setStyleSheet(f"background-color: {payload['panel_bg']};")
        tab_base.setStyleSheet(f"background-color: {payload['panel_bg']};")
        tab_errors.setStyleSheet(f"background-color: {payload['panel_bg']};")
        active_scroll.setStyleSheet(
            f""
            f"QScrollArea {{"
            f"background-color: {payload['panel_bg']};"
            f"border: 1px solid {payload['border']};"
            f"}}"
        )
        active_scroll_content.setStyleSheet(f"background-color: {payload['panel_bg']};")

        for key, chip in active_chips.items():
            style_color_chip(chip, payload.get(key, ""), border_color=payload.get("border", colors.border))

        preview_code.setStyleSheet(
            f""
            f"QPlainTextEdit {{"
            f"background-color: {payload['background']};"
            f"color: {payload['foreground']};"
            f"selection-background-color: {payload['selection']};"
            f"border: 1px solid {payload['border']};"
            f"}}"
        )

    for key, label in color_field_labels:
        create_editor_row(base_form, key, label, tab_base)
    for key, label in error_field_labels:
        create_editor_row(error_form, key, label, tab_errors)

    def on_theme_selected() -> None:
        selected_item = theme_list.currentItem()
        if selected_item is None:
            return
        theme_key = str(selected_item.data(Qt.UserRole))
        selected_theme_key["value"] = theme_key

        payload = theme_payload(theme_key)
        current_payload.clear()
        current_payload.update(payload)
        fill_fields(payload)
        apply_preview(payload, theme_key)

    def on_reset_selected_theme() -> None:
        theme_key = selected_theme_key["value"]
        payload = default_theme_payload(theme_key)
        current_payload.clear()
        current_payload.update(payload)
        fill_fields(payload)
        apply_preview(payload, theme_key)

    reset_button.clicked.connect(on_reset_selected_theme)
    theme_list.currentRowChanged.connect(lambda _row: on_theme_selected())

    current_theme_key = steins_gate_theme.get_theme_key()
    for row in range(theme_list.count()):
        item = theme_list.item(row)
        if item.data(Qt.UserRole) == current_theme_key:
            theme_list.setCurrentRow(row)
            break
    on_theme_selected()

    root_layout.addWidget(left_panel)
    root_layout.addWidget(right_panel, 1)

    if dialog.exec_() != QDialog.Accepted:
        return

    payload = read_payload_from_fields()
    if payload is None:
        QMessageBox.warning(window, "Temas", "Hay colores inválidos. Usa formato #RRGGBB.")
        return

    theme_key = selected_theme_key["value"]
    new_theme_colors, new_error_colors = payload_to_objects(payload)
    steins_gate_theme.set_theme_palette(theme_key, new_theme_colors, new_error_colors)

    overrides = steins_gate_theme.export_theme_overrides_payload()
    window._settings.setValue("session/theme_overrides_payload", json.dumps(overrides))

    apply_theme(window, theme_key)
