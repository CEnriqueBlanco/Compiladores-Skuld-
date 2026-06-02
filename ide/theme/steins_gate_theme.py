from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    background: str = "#1a1a1a"
    foreground: str = "#e8e8e8"
    keywords: str = "#c41e3a"
    strings: str = "#8fbc8f"
    comments: str = "#696969"
    numbers: str = "#ff6b6b"
    operators: str = "#ffd166"
    selection: str = "#4a0e0e"
    accent: str = "#c41e3a"
    panel_bg: str = "#252525"
    border: str = "#3a3a3a"
    hover: str = "#5a1e1e"


@dataclass(frozen=True)
class ErrorColors:
    underline: str
    background: str
    text: str
    border: str


THEMES: dict[str, tuple[str, ThemeColors]] = {
    "labmem_001": (
        "LabMem 001 · Okabe",
        ThemeColors(
            background="#0f1116",
            foreground="#e6edf3",
            keywords="#ff6b6b",
            strings="#98c379",
            comments="#6b7280",
            numbers="#f7b267",
            operators="#ffd166",
            selection="#5a1f1f",
            accent="#ff6b6b",
            panel_bg="#161b22",
            border="#30363d",
            hover="#222a33",
        ),
    ),
    "labmem_002": (
        "LabMem 002 · Daru",
        ThemeColors(
            background="#101018",
            foreground="#e9e9ff",
            keywords="#8ab4f8",
            strings="#7ee787",
            comments="#7d8590",
            numbers="#d2a8ff",
            operators="#ffd166",
            selection="#1f2a4a",
            accent="#8ab4f8",
            panel_bg="#161b22",
            border="#30363d",
            hover="#1d2633",
        ),
    ),
    "labmem_003": (
        "LabMem 003 · Mayuri",
        ThemeColors(
            background="#141014",
            foreground="#f6edf3",
            keywords="#ff7aa2",
            strings="#9dd9b8",
            comments="#8a7b87",
            numbers="#ffb86c",
            operators="#ffd166",
            selection="#4b1f35",
            accent="#ff7aa2",
            panel_bg="#1f1721",
            border="#3b2d40",
            hover="#5a2b4f",
        ),
    ),
    "labmem_004": (
        "LabMem 004 · Kurisu",
        ThemeColors(),
    ),
    "labmem_005": (
        "LabMem 005 · Moeka",
        ThemeColors(
            background="#121212",
            foreground="#ececec",
            keywords="#8be9fd",
            strings="#50fa7b",
            comments="#7f8490",
            numbers="#bd93f9",
            operators="#ffd166",
            selection="#2f2a44",
            accent="#8be9fd",
            panel_bg="#1d1f24",
            border="#343a46",
            hover="#2a303a",
        ),
    ),
    "labmem_006": (
        "LabMem 006 · Suzuha",
        ThemeColors(
            background="#0f1410",
            foreground="#eaf8ea",
            keywords="#ff9f43",
            strings="#7dcea0",
            comments="#7e8f7f",
            numbers="#f5cd79",
            operators="#ffd166",
            selection="#3a2c18",
            accent="#ff9f43",
            panel_bg="#18211a",
            border="#2f3b31",
            hover="#2c3a2f",
        ),
    ),
    "labmem_007": (
        "LabMem 007 · Faris",
        ThemeColors(
            background="#150f1f",
            foreground="#f4eeff",
            keywords="#c792ea",
            strings="#7fdbca",
            comments="#877f98",
            numbers="#f78c6c",
            operators="#ffd166",
            selection="#3d2a57",
            accent="#c792ea",
            panel_bg="#21172e",
            border="#3b2b4f",
            hover="#4a3463",
        ),
    ),
    "personalizado": (
        "Personalizado",
        ThemeColors(
            background="#11131a",
            foreground="#e6edf3",
            keywords="#ff7b72",
            strings="#79c0ff",
            comments="#8b949e",
            numbers="#d2a8ff",
            operators="#ffa657",
            selection="#2d3a50",
            accent="#58a6ff",
            panel_bg="#161b22",
            border="#30363d",
            hover="#21262d",
        ),
    ),
}

DEFAULT_THEME_KEY = "labmem_004"
_current_theme_key = DEFAULT_THEME_KEY

ERROR_THEMES: dict[str, ErrorColors] = {
    "labmem_001": ErrorColors(underline="#ff5f56", background="#4a1818", text="#ffb4ad", border="#8b2d2a"),
    "labmem_002": ErrorColors(underline="#ff6b9e", background="#3a1730", text="#ffb8d2", border="#7a2a59"),
    "labmem_003": ErrorColors(underline="#ff5c8a", background="#4a1730", text="#ffc1d6", border="#8a2d58"),
    "labmem_004": ErrorColors(underline="#ff4d4d", background="#4a1414", text="#ffb3b3", border="#8c2a2a"),
    "labmem_005": ErrorColors(underline="#ff6a6a", background="#3f1a1f", text="#ffc0c8", border="#7e323d"),
    "labmem_006": ErrorColors(underline="#ff7f50", background="#4a2718", text="#ffd2bf", border="#915236"),
    "labmem_007": ErrorColors(underline="#ff6ed3", background="#3e1f45", text="#ffc8f0", border="#7c3a8a"),
    "personalizado": ErrorColors(underline="#ff4d4d", background="#401818", text="#ffb3b3", border="#8c2a2a"),
}

DEFAULT_THEMES: dict[str, tuple[str, ThemeColors]] = dict(THEMES)
DEFAULT_ERROR_THEMES: dict[str, ErrorColors] = dict(ERROR_THEMES)


def list_themes() -> list[tuple[str, str]]:
    return [(key, data[0]) for key, data in THEMES.items()]


def get_theme_name(theme_key: str | None = None) -> str:
    key = theme_key or _current_theme_key
    if key not in THEMES:
        key = DEFAULT_THEME_KEY
    return THEMES[key][0]


def get_theme_key() -> str:
    return _current_theme_key


def set_theme(theme_key: str) -> bool:
    global _current_theme_key
    if theme_key not in THEMES:
        return False
    _current_theme_key = theme_key
    return True


def set_theme_palette(theme_key: str, colors: ThemeColors, error_colors: ErrorColors, *, name: str | None = None) -> bool:
    if theme_key not in THEMES:
        return False

    current_name = THEMES[theme_key][0]
    THEMES[theme_key] = (name or current_name, colors)
    ERROR_THEMES[theme_key] = error_colors
    return True


def reset_theme_palette(theme_key: str) -> bool:
    if theme_key not in DEFAULT_THEMES or theme_key not in DEFAULT_ERROR_THEMES:
        return False
    THEMES[theme_key] = DEFAULT_THEMES[theme_key]
    ERROR_THEMES[theme_key] = DEFAULT_ERROR_THEMES[theme_key]
    return True


def get_colors() -> ThemeColors:
    return THEMES[_current_theme_key][1]


def get_error_colors() -> ErrorColors:
    return ERROR_THEMES.get(_current_theme_key, ERROR_THEMES[DEFAULT_THEME_KEY])


def get_error_colors_for_theme(theme_key: str) -> ErrorColors:
    if theme_key not in ERROR_THEMES:
        return ERROR_THEMES[DEFAULT_THEME_KEY]
    return ERROR_THEMES[theme_key]


def get_colors_for_theme(theme_key: str) -> ThemeColors:
    if theme_key not in THEMES:
        return THEMES[DEFAULT_THEME_KEY][1]
    return THEMES[theme_key][1]


def get_default_theme_name(theme_key: str) -> str:
    if theme_key not in DEFAULT_THEMES:
        return DEFAULT_THEMES[DEFAULT_THEME_KEY][0]
    return DEFAULT_THEMES[theme_key][0]


def get_default_colors_for_theme(theme_key: str) -> ThemeColors:
    if theme_key not in DEFAULT_THEMES:
        return DEFAULT_THEMES[DEFAULT_THEME_KEY][1]
    return DEFAULT_THEMES[theme_key][1]


def get_default_error_colors_for_theme(theme_key: str) -> ErrorColors:
    if theme_key not in DEFAULT_ERROR_THEMES:
        return DEFAULT_ERROR_THEMES[DEFAULT_THEME_KEY]
    return DEFAULT_ERROR_THEMES[theme_key]


def set_custom_theme(colors: ThemeColors, error_colors: ErrorColors, *, name: str = "Personalizado") -> None:
    THEMES["personalizado"] = (name, colors)
    ERROR_THEMES["personalizado"] = error_colors


def export_custom_theme_payload() -> dict[str, str]:
    theme_name, custom_colors = THEMES["personalizado"]
    custom_error_colors = ERROR_THEMES["personalizado"]
    return {
        "name": theme_name,
        "background": custom_colors.background,
        "foreground": custom_colors.foreground,
        "keywords": custom_colors.keywords,
        "strings": custom_colors.strings,
        "comments": custom_colors.comments,
        "numbers": custom_colors.numbers,
        "operators": custom_colors.operators,
        "selection": custom_colors.selection,
        "accent": custom_colors.accent,
        "panel_bg": custom_colors.panel_bg,
        "border": custom_colors.border,
        "hover": custom_colors.hover,
        "err_underline": custom_error_colors.underline,
        "err_background": custom_error_colors.background,
        "err_text": custom_error_colors.text,
        "err_border": custom_error_colors.border,
    }


def import_custom_theme_payload(payload: dict[str, str]) -> bool:
    required = {
        "background",
        "foreground",
        "keywords",
        "strings",
        "comments",
        "numbers",
        "operators",
        "selection",
        "accent",
        "panel_bg",
        "border",
        "hover",
        "err_underline",
        "err_background",
        "err_text",
        "err_border",
    }
    if not required.issubset(payload.keys()):
        return False

    set_custom_theme(
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
        name=payload.get("name", "Personalizado"),
    )
    return True


def export_theme_overrides_payload() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for theme_key, (theme_name, theme_colors) in THEMES.items():
        default_theme_name, default_theme_colors = DEFAULT_THEMES.get(theme_key, (theme_name, theme_colors))
        default_error_colors = DEFAULT_ERROR_THEMES.get(theme_key, ERROR_THEMES.get(theme_key, DEFAULT_ERROR_THEMES[DEFAULT_THEME_KEY]))
        current_error_colors = ERROR_THEMES.get(theme_key, default_error_colors)

        if (
            theme_name == default_theme_name
            and theme_colors == default_theme_colors
            and current_error_colors == default_error_colors
        ):
            continue

        result[theme_key] = {
            "name": theme_name,
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
            "err_underline": current_error_colors.underline,
            "err_background": current_error_colors.background,
            "err_text": current_error_colors.text,
            "err_border": current_error_colors.border,
        }

    return result


def import_theme_overrides_payload(payload: dict[str, dict[str, str]]) -> bool:
    if not isinstance(payload, dict):
        return False

    for theme_key, theme_data in payload.items():
        if not isinstance(theme_data, dict) or theme_key not in THEMES:
            continue
        required = {
            "background",
            "foreground",
            "keywords",
            "strings",
            "comments",
            "numbers",
            "operators",
            "selection",
            "accent",
            "panel_bg",
            "border",
            "hover",
            "err_underline",
            "err_background",
            "err_text",
            "err_border",
        }
        if not required.issubset(theme_data.keys()):
            continue

        set_theme_palette(
            theme_key,
            ThemeColors(
                background=theme_data["background"],
                foreground=theme_data["foreground"],
                keywords=theme_data["keywords"],
                strings=theme_data["strings"],
                comments=theme_data["comments"],
                numbers=theme_data["numbers"],
                operators=theme_data["operators"],
                selection=theme_data["selection"],
                accent=theme_data["accent"],
                panel_bg=theme_data["panel_bg"],
                border=theme_data["border"],
                hover=theme_data["hover"],
            ),
            ErrorColors(
                underline=theme_data["err_underline"],
                background=theme_data["err_background"],
                text=theme_data["err_text"],
                border=theme_data["err_border"],
            ),
            name=theme_data.get("name"),
        )

    return True


def build_stylesheet() -> str:
    colors = get_colors()
    
    # We replace '#' with '%23' because Qt's url() parser interprets '#' as the start of a fragment.
    # We use double quotes inside the SVG to be standard-compliant for Qt's SVG parser, and wrap the QSS url in single quotes.
    closed_svg = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="%23ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3.5l4.5 4.5-4.5 4.5"/></svg>'
    open_svg = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="%23ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 6l4.5 4.5 4.5-4.5"/></svg>'

    return f"""
    QMainWindow {{
        background-color: {colors.background};
        color: {colors.foreground};
    }}
    QMenuBar {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border-bottom: 1px solid {colors.border};
    }}
    QMenuBar::item:selected {{
        background-color: {colors.hover};
    }}
    QMenu {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border: 1px solid {colors.border};
    }}
    QMenu::item:selected {{
        background-color: {colors.hover};
    }}
    QToolBar {{
        background-color: {colors.panel_bg};
        border-bottom: 1px solid {colors.border};
        spacing: 6px;
        padding: 4px;
    }}
    QToolButton {{
        background-color: transparent;
        color: {colors.foreground};
        border: 1px solid transparent;
        padding: 4px 6px;
        border-radius: 4px;
    }}
    QToolButton:hover {{
        background-color: {colors.hover};
        border-color: {colors.border};
    }}
    QWidget#find_bar {{
        background-color: {colors.panel_bg};
        border-bottom: 1px solid {colors.border};
    }}
    QWidget#find_bar QLabel {{
        color: {colors.foreground};
    }}
    QWidget#find_bar QLineEdit {{
        background-color: {colors.background};
        color: {colors.foreground};
        border: 1px solid {colors.border};
        selection-background-color: {colors.selection};
        min-height: 24px;
    }}
    QWidget#find_bar QSpinBox {{
        background-color: {colors.background};
        color: {colors.foreground};
        border: 1px solid {colors.border};
        min-height: 24px;
        min-width: 90px;
        padding: 0 6px;
    }}
    QWidget#find_bar QLabel#find_count {{
        color: {colors.accent};
        border: 1px solid {colors.border};
        background-color: {colors.background};
        border-radius: 3px;
        padding: 2px 8px;
        min-width: 52px;
    }}
    QWidget#find_bar QToolButton {{
        background-color: {colors.background};
        color: {colors.foreground};
        border: 1px solid {colors.border};
        padding: 3px 7px;
        border-radius: 3px;
    }}
    QWidget#find_bar QToolButton:hover {{
        background-color: {colors.hover};
    }}
    QStatusBar {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
    }}
    QDialog, QMessageBox, QFileDialog, QInputDialog {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
    }}
    QFileDialog QTreeView,
    QFileDialog QListView,
    QFileDialog QTableView {{
        background-color: {colors.background};
        color: {colors.foreground};
        border: 1px solid {colors.border};
        selection-background-color: {colors.selection};
        selection-color: {colors.foreground};
        alternate-background-color: {colors.panel_bg};
    }}
    QFileDialog QHeaderView::section {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border: 1px solid {colors.border};
        padding: 4px;
    }}
    QLabel {{
        color: {colors.foreground};
    }}
    QLineEdit, QComboBox, QSpinBox {{
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
    QPlainTextEdit, QTextEdit {{
        background-color: {colors.background};
        color: {colors.foreground};
        selection-background-color: {colors.selection};
        border: 1px solid {colors.border};
    }}
    QTreeView {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border: 1px solid {colors.border};
    }}
    QTreeView::branch:has-children:!has-siblings:closed,
    QTreeView::branch:closed:has-children:has-siblings {{
        border-image: none;
        image: url('{closed_svg}');
    }}
    QTreeView::branch:open:has-children:!has-siblings,
    QTreeView::branch:open:has-children:has-siblings {{
        border-image: none;
        image: url('{open_svg}');
    }}
    QTreeWidget, QListWidget, QListView {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border: 1px solid {colors.border};
    }}
    QTreeWidget::item:selected, QListWidget::item:selected, QListView::item:selected {{
        background-color: {colors.selection};
        color: {colors.foreground};
    }}
    QTreeWidget::item:selected:active,
    QTreeWidget::item:selected:!active,
    QListWidget::item:selected:active,
    QListWidget::item:selected:!active,
    QListView::item:selected:active,
    QListView::item:selected:!active {{
        color: {colors.foreground};
    }}
    QTabWidget::pane {{
        border: 1px solid {colors.border};
        background-color: {colors.panel_bg};
    }}
    QTabBar::tab {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        padding: 6px 10px;
        border: 1px solid {colors.border};
        border-bottom: none;
    }}
    QTabBar::tab:selected {{
        background-color: {colors.background};
        color: {colors.accent};
    }}
    QTabBar::tab:selected:active,
    QTabBar::tab:selected:!active {{
        color: {colors.foreground};
    }}
    QSplitter::handle {{
        background-color: {colors.border};
    }}
    QScrollBar:vertical {{
        background: {colors.panel_bg};
        width: 12px;
        margin: 0;
        border: 1px solid {colors.border};
    }}
    QScrollBar::handle:vertical {{
        background: {colors.border};
        min-height: 24px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        background: {colors.panel_bg};
        height: 12px;
        border: none;
    }}
    QScrollBar:horizontal {{
        background: {colors.panel_bg};
        height: 12px;
        margin: 0;
        border: 1px solid {colors.border};
    }}
    QScrollBar::handle:horizontal {{
        background: {colors.border};
        min-width: 24px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        background: {colors.panel_bg};
        width: 12px;
        border: none;
    }}
    QScrollBar::add-page,
    QScrollBar::sub-page {{
        background: {colors.background};
    }}
    """.strip()
