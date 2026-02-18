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


COLORS = ThemeColors()


def build_stylesheet() -> str:
    return f"""
    QMainWindow {{
        background-color: {COLORS.background};
        color: {COLORS.foreground};
    }}
    QMenuBar {{
        background-color: {COLORS.panel_bg};
        color: {COLORS.foreground};
        border-bottom: 1px solid {COLORS.border};
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS.hover};
    }}
    QMenu {{
        background-color: {COLORS.panel_bg};
        color: {COLORS.foreground};
        border: 1px solid {COLORS.border};
    }}
    QMenu::item:selected {{
        background-color: {COLORS.hover};
    }}
    QToolBar {{
        background-color: {COLORS.panel_bg};
        border-bottom: 1px solid {COLORS.border};
        spacing: 6px;
        padding: 4px;
    }}
    QToolButton {{
        background-color: transparent;
        color: {COLORS.foreground};
        border: 1px solid transparent;
        padding: 4px 6px;
        border-radius: 4px;
    }}
    QToolButton:hover {{
        background-color: {COLORS.hover};
        border-color: {COLORS.border};
    }}
    QStatusBar {{
        background-color: {COLORS.panel_bg};
        color: {COLORS.foreground};
    }}
    QPlainTextEdit, QTextEdit {{
        background-color: {COLORS.background};
        color: {COLORS.foreground};
        selection-background-color: {COLORS.selection};
        border: 1px solid {COLORS.border};
    }}
    QTreeWidget, QListWidget {{
        background-color: {COLORS.panel_bg};
        color: {COLORS.foreground};
        border: 1px solid {COLORS.border};
    }}
    QTreeWidget::item:selected, QListWidget::item:selected {{
        background-color: {COLORS.selection};
    }}
    QTabWidget::pane {{
        border: 1px solid {COLORS.border};
        background-color: {COLORS.panel_bg};
    }}
    QTabBar::tab {{
        background-color: {COLORS.panel_bg};
        color: {COLORS.foreground};
        padding: 6px 10px;
        border: 1px solid {COLORS.border};
        border-bottom: none;
    }}
    QTabBar::tab:selected {{
        background-color: {COLORS.background};
        color: {COLORS.accent};
    }}
    QSplitter::handle {{
        background-color: {COLORS.border};
    }}
    QScrollBar:vertical {{
        background: {COLORS.panel_bg};
        width: 12px;
        margin: 0;
        border: 1px solid {COLORS.border};
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS.border};
        min-height: 24px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        background: {COLORS.panel_bg};
        height: 12px;
        border: none;
    }}
    QScrollBar:horizontal {{
        background: {COLORS.panel_bg};
        height: 12px;
        margin: 0;
        border: 1px solid {COLORS.border};
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS.border};
        min-width: 24px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        background: {COLORS.panel_bg};
        width: 12px;
        border: none;
    }}
    QScrollBar::add-page,
    QScrollBar::sub-page {{
        background: {COLORS.background};
    }}
    """.strip()
