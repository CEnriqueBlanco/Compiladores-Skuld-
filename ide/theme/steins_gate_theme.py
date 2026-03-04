from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    background: str = "#1a1a1a"
    foreground: str = "#e8e8e8"
    keywords: str = "#c41e3a"
    strings: str = "#8fbc8f"
    comments: str = "#696969"
    numbers: str = "#ff6b6b"
    operators: str = "#ffffff"
    selection: str = "#4a0e0e"
    accent: str = "#c41e3a"
    panel_bg: str = "#252525"
    border: str = "#3a3a3a"
    hover: str = "#5a1e1e"


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
            operators="#e6edf3",
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
            operators="#e9e9ff",
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
            operators="#f6edf3",
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
            operators="#ececec",
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
            operators="#eaf8ea",
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
            operators="#f4eeff",
            selection="#3d2a57",
            accent="#c792ea",
            panel_bg="#21172e",
            border="#3b2b4f",
            hover="#4a3463",
        ),
    ),
}

DEFAULT_THEME_KEY = "labmem_004"
_current_theme_key = DEFAULT_THEME_KEY


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


def get_colors() -> ThemeColors:
    return THEMES[_current_theme_key][1]


def get_colors_for_theme(theme_key: str) -> ThemeColors:
    if theme_key not in THEMES:
        return THEMES[DEFAULT_THEME_KEY][1]
    return THEMES[theme_key][1]


def build_stylesheet() -> str:
    colors = get_colors()
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
    QTreeWidget, QListWidget {{
        background-color: {colors.panel_bg};
        color: {colors.foreground};
        border: 1px solid {colors.border};
    }}
    QTreeWidget::item:selected, QListWidget::item:selected {{
        background-color: {colors.selection};
        color: {colors.foreground};
    }}
    QTreeWidget::item:selected:active,
    QTreeWidget::item:selected:!active,
    QListWidget::item:selected:active,
    QListWidget::item:selected:!active {{
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
