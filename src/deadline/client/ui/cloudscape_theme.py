# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Dark theme for AWS Deadline Cloud GUI components, inspired by the BealineMonitor
(Deadline Cloud Monitor) web application.

Color tokens are derived from the BealineMonitor theme:
https://code.amazon.com/packages/BealineMonitor/blobs/mainline/--/src/routes/themes.ts
https://code.amazon.com/packages/BealineMonitor/blobs/mainline/--/src/styles/tokens.scss

Usage:
    from deadline.client.ui.cloudscape_theme import apply_cloudscape_theme
    apply_cloudscape_theme(app)  # QApplication instance
"""

from __future__ import annotations as _annotations

from pathlib import Path as _Path

from qtpy.QtCore import QObject as _QObject
from qtpy.QtGui import QColor as _QColor, QPalette as _QPalette
from qtpy.QtWidgets import QApplication as _QApplication

# Path to SVG resources (arrows, icons)
_RESOURCES_DIR = str(_Path(__file__).parent / "resources").replace("\\", "/")


# ---------------------------------------------------------------------------
# BealineMonitor color tokens
# ---------------------------------------------------------------------------

# Blues
_BLUE_100 = "#f0f5ff"
_BLUE_400 = "#8cb4ff"
_BLUE_500 = "#5c94ff"
_BLUE_600 = "#1044a7"
_BLUE_900 = "#191e2c"

# Cyan
_CYAN_400 = "#85e2ff"

# Orange / Amber
_ORANGE_500 = "#fb8213"
_AMAZON_ORANGE = "#ff9900"

# Red
_RED_500 = "#f55c5c"
_RED_600 = "#ff3131"
_RED_900 = "#340606"

# Green
_GREEN_400 = "#79de4b"
_GREEN_500 = "#29ad32"
_GREEN_900 = "#001a02"

# Yellow
_YELLOW_600 = "#ffe457"
_YELLOW_900 = "#1d1906"

# Greys – the core of the BealineMonitor palette
_GREY_100 = "#fbfbfb"
_GREY_200 = "#e9ebed"
_GREY_300 = "#d1d5db"
_GREY_450 = "#9aa0a6"
_GREY_500 = "#80868b"
_GREY_550 = "#5f6368"
_GREY_600 = "#3c4043"
_GREY_650 = "#2e3134"
_GREY_700 = "#282a2d"
_GREY_750 = "#202124"
_GREY_800 = "#17181b"
_GREY_900 = "#0e1013"
_GREY_1000 = "#09090a"
_WHITE = "#ffffff"

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

_FONT_FAMILY = "'Amazon Ember', Helvetica, Arial, sans-serif"
_FONT_SIZE_BODY = "14px"
_FONT_SIZE_SMALL = "12px"
_FONT_SIZE_HEADING = "16px"

# ---------------------------------------------------------------------------
# Spacing
# ---------------------------------------------------------------------------

_SPACE_XS = "8px"
_SPACE_S = "12px"
_SPACE_M = "16px"
_SPACE_L = "20px"

# ---------------------------------------------------------------------------
# Border radii
# ---------------------------------------------------------------------------

_RADIUS_INPUT = "8px"
_RADIUS_BUTTON = "20px"
_RADIUS_CONTAINER = "8px"
_RADIUS_DROPDOWN = "8px"
_RADIUS_ITEM = "8px"


def _dark_stylesheet() -> str:
    """Return the BealineMonitor-inspired dark QSS stylesheet."""
    return f"""
/* ===================================================================
   Deadline Cloud Monitor Dark Theme
   =================================================================== */

/* --- Global defaults ------------------------------------------------ */
* {{
    font-family: {_FONT_FAMILY};
    font-size: {_FONT_SIZE_BODY};
    color: {_GREY_300};
    outline: none;
}}

/* --- QWidget (base) ------------------------------------------------- */
QWidget {{
    background-color: transparent;
    color: {_GREY_300};
}}

/* --- QDialog / QMainWindow ------------------------------------------ */
QDialog, QMainWindow {{
    background-color: {_GREY_1000};
}}

/* --- QLabel --------------------------------------------------------- */
QLabel {{
    background-color: transparent;
    color: {_GREY_300};
    padding: 0px;
}}

QLabel:disabled {{
    color: {_GREY_550};
}}

/* --- QGroupBox (container) ------------------------------------------ */
QGroupBox {{
    background-color: {_GREY_800};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_CONTAINER};
    margin-top: 6px;
    padding: {_SPACE_S};
    padding-top: 32px;
}}

QGroupBox:disabled {{
    background-color: {_GREY_900};
    border-color: {_GREY_600};
}}

QGroupBox::title:disabled {{
    color: {_GREY_550};
}}

QGroupBox::title {{
    subcontrol-origin: padding;
    subcontrol-position: top left;
    padding: {_SPACE_S} {_SPACE_S};
    color: {_GREY_100};
    font-size: 20px;
    font-weight: bold;
    background-color: transparent;
}}

/* --- QPushButton (normal) ------------------------------------------- */
QPushButton {{
    background-color: {_GREY_800};
    color: {_GREY_300};
    border: 2px solid {_GREY_550};
    border-radius: {_RADIUS_BUTTON};
    padding: 4px {_SPACE_L};
    font-weight: 700;
    font-size: {_FONT_SIZE_BODY};
    min-height: 24px;
}}

QPushButton:hover {{
    background-color: {_GREY_700};
    border-color: {_GREY_450};
    color: {_GREY_100};
}}

QPushButton:pressed {{
    background-color: {_GREY_200};
    border-color: {_GREY_550};
    color: {_GREY_900};
}}

QPushButton:disabled {{
    background-color: {_GREY_800};
    border-color: {_GREY_600};
    color: {_GREY_550};
}}

/* --- QPushButton primary variant ------------------------------------ */
QPushButton[cssClass="primary"],
QPushButton#primary_button,
QDialogButtonBox QPushButton:default {{
    background-color: {_AMAZON_ORANGE};
    color: {_GREY_900};
    border: 2px solid {_AMAZON_ORANGE};
    border-radius: 20px;
    font-weight: 700;
    padding: 4px 24px;
}}

/* Ensure all dialog box buttons get the rounded style */
QDialogButtonBox QPushButton {{
    border-radius: 20px;
    min-width: 70px;
    padding: 4px 20px;
}}

QPushButton[cssClass="primary"]:hover,
QPushButton#primary_button:hover,
QDialogButtonBox QPushButton:default:hover {{
    background-color: {_ORANGE_500};
    border-color: {_ORANGE_500};
}}

QPushButton[cssClass="primary"]:pressed,
QPushButton#primary_button:pressed,
QDialogButtonBox QPushButton:default:pressed {{
    background-color: {_ORANGE_500};
    border-color: {_ORANGE_500};
}}

QPushButton[cssClass="primary"]:disabled,
QPushButton#primary_button:disabled,
QDialogButtonBox QPushButton:default:disabled {{
    background-color: {_GREY_700};
    border-color: {_GREY_700};
    color: {_GREY_550};
}}

/* --- QLineEdit / QTextEdit / QPlainTextEdit (inputs) ---------------- */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {_GREY_800};
    color: {_GREY_200};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_INPUT};
    padding: 5px {_SPACE_S};
    selection-background-color: {_BLUE_900};
    selection-color: {_GREY_200};
    min-height: 22px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {_BLUE_500};
    padding: 4px 11px;
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {_GREY_800};
    color: {_GREY_550};
    border-color: {_GREY_600};
}}

QLineEdit::placeholder {{
    color: {_GREY_500};
}}

/* --- QComboBox (select) --------------------------------------------- */
QComboBox {{
    combobox-popup: 0;
    background-color: {_GREY_800};
    color: {_GREY_200};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_INPUT};
    padding: 5px {_SPACE_S};
    min-height: 22px;
}}

QComboBox:hover {{
    border-color: {_GREY_450};
}}

QComboBox:focus, QComboBox:on {{
    border: 2px solid {_BLUE_500};
    padding: 4px 11px;
}}

QComboBox:disabled {{
    background-color: {_GREY_900};
    color: {_GREY_550};
    border-color: {_GREY_600};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 24px;
    border: none;
    border-left: 1px solid {_GREY_550};
    background: {_GREY_700};
    border-top-right-radius: {_RADIUS_INPUT};
    border-bottom-right-radius: {_RADIUS_INPUT};
}}

QComboBox::down-arrow {{
    image: url({_RESOURCES_DIR}/arrow_down.svg);
    width: 10px;
    height: 6px;
}}

QComboBox::down-arrow:disabled {{
    image: url({_RESOURCES_DIR}/arrow_down_disabled.svg);
}}

QComboBox QAbstractItemView {{
    background-color: {_GREY_800};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_DROPDOWN};
    outline: none;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 6px {_SPACE_S};
    border-radius: {_RADIUS_ITEM};
    min-height: 24px;
    color: {_GREY_300};
    background-color: {_GREY_800};
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {_GREY_650};
    color: {_GREY_100};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {_BLUE_900};
    color: {_GREY_100};
}}

/* --- QSpinBox / QDoubleSpinBox -------------------------------------- */
QSpinBox, QDoubleSpinBox {{
    background-color: {_GREY_800};
    color: {_GREY_200};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_INPUT};
    padding: 5px {_SPACE_S};
    min-height: 22px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {_BLUE_500};
    padding: 4px 11px;
}}

QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {_GREY_800};
    color: {_GREY_550};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border: none;
    border-left: 1px solid {_GREY_550};
    border-bottom: 1px solid {_GREY_550};
    background: {_GREY_700};
    border-top-right-radius: {_RADIUS_INPUT};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: padding;
    subcontrol-position: bottom right;
    width: 24px;
    border: none;
    border-left: 1px solid {_GREY_550};
    background: {_GREY_700};
    border-bottom-right-radius: {_RADIUS_INPUT};
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {_GREY_650};
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({_RESOURCES_DIR}/arrow_up.svg);
    width: 10px;
    height: 6px;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({_RESOURCES_DIR}/arrow_down.svg);
    width: 10px;
    height: 6px;
}}

QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {{
    image: url({_RESOURCES_DIR}/arrow_up_disabled.svg);
}}

QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {{
    image: url({_RESOURCES_DIR}/arrow_down_disabled.svg);
}}

/* --- QCheckBox ------------------------------------------------------ */
QCheckBox {{
    spacing: {_SPACE_XS};
    color: {_GREY_300};
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    image: url({_RESOURCES_DIR}/checkbox_unchecked.svg);
}}

QCheckBox::indicator:checked {{
    image: url({_RESOURCES_DIR}/checkbox_checked.svg);
}}

QCheckBox::indicator:disabled {{
    image: url({_RESOURCES_DIR}/checkbox_disabled.svg);
}}

QCheckBox::indicator:checked:disabled {{
    image: url({_RESOURCES_DIR}/checkbox_checked_disabled.svg);
}}

QCheckBox:disabled {{
    color: {_GREY_550};
}}

/* --- QRadioButton --------------------------------------------------- */
QRadioButton {{
    spacing: {_SPACE_XS};
    color: {_GREY_300};
    background-color: transparent;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {_GREY_550};
    border-radius: 9px;
    background-color: {_GREY_800};
}}

QRadioButton::indicator:checked {{
    background-color: {_GREY_200};
    border-color: {_GREY_200};
}}

QRadioButton::indicator:disabled {{
    background-color: {_GREY_600};
    border-color: {_GREY_550};
}}

QRadioButton:disabled {{
    color: {_GREY_550};
}}

/* --- QTabWidget / QTabBar (tabs) ------------------------------------ */
QTabWidget::pane {{
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_CONTAINER};
    background-color: {_GREY_800};
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {_GREY_450};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px {_SPACE_M};
    font-size: {_FONT_SIZE_HEADING};
    font-weight: 700;
    min-width: 60px;
}}

QTabBar::tab:selected {{
    color: {_GREY_100};
    border-bottom: 2px solid {_GREY_100};
}}

QTabBar::tab:hover:!selected {{
    color: {_GREY_200};
}}

QTabBar::tab:disabled {{
    color: {_GREY_550};
}}

/* --- QTableView / QTreeView / QListView (collections) --------------- */
QTableView, QTreeView, QListView, QListWidget {{
    background-color: {_GREY_800};
    alternate-background-color: {_GREY_750};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_CONTAINER};
    gridline-color: {_GREY_600};
    selection-background-color: {_BLUE_900};
    selection-color: {_GREY_200};
    outline: none;
}}

QTableView::item, QTreeView::item, QListView::item, QListWidget::item {{
    padding: 4px {_SPACE_S};
    border-radius: {_RADIUS_ITEM};
}}

QTableView::item:selected, QTreeView::item:selected,
QListView::item:selected, QListWidget::item:selected {{
    background-color: {_BLUE_900};
    color: {_GREY_200};
}}

QTableView::item:hover, QTreeView::item:hover,
QListView::item:hover, QListWidget::item:hover {{
    background-color: {_GREY_650};
}}

QHeaderView::section {{
    background-color: {_GREY_800};
    color: {_GREY_200};
    border: none;
    border-bottom: 1px solid {_GREY_550};
    padding: 6px {_SPACE_S};
    font-weight: 700;
    font-size: {_FONT_SIZE_BODY};
}}

/* --- QScrollBar ----------------------------------------------------- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {_GREY_600};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {_GREY_500};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {_GREY_600};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {_GREY_500};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}

/* --- QScrollArea ---------------------------------------------------- */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

/* --- QProgressBar --------------------------------------------------- */
QProgressBar {{
    background-color: {_GREY_700};
    border: none;
    border-radius: 4px;
    text-align: center;
    color: {_GREY_300};
    min-height: 8px;
    max-height: 8px;
}}

QProgressBar::chunk {{
    background-color: {_BLUE_500};
    border-radius: 4px;
}}

/* --- QToolTip ------------------------------------------------------- */
QToolTip {{
    background-color: {_GREY_700};
    color: {_GREY_200};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_INPUT};
    padding: 6px {_SPACE_S};
    font-size: {_FONT_SIZE_SMALL};
}}

/* --- QMenu ---------------------------------------------------------- */
QMenu {{
    background-color: {_GREY_800};
    border: 1px solid {_GREY_550};
    border-radius: {_RADIUS_DROPDOWN};
    padding: 4px;
}}

QMenu::item {{
    padding: 6px {_SPACE_L};
    border-radius: {_RADIUS_ITEM};
    color: {_GREY_300};
}}

QMenu::item:selected {{
    background-color: {_GREY_650};
}}

QMenu::item:disabled {{
    color: {_GREY_550};
}}

QMenu::separator {{
    height: 1px;
    background-color: {_GREY_550};
    margin: 4px {_SPACE_S};
}}

/* --- QMenuBar ------------------------------------------------------- */
QMenuBar {{
    background-color: {_GREY_800};
    border-bottom: 1px solid {_GREY_550};
    padding: 2px;
}}

QMenuBar::item {{
    padding: 6px {_SPACE_S};
    border-radius: {_RADIUS_ITEM};
    color: {_GREY_300};
}}

QMenuBar::item:selected {{
    background-color: {_GREY_650};
}}

/* --- QStatusBar ----------------------------------------------------- */
QStatusBar {{
    background-color: {_GREY_900};
    border-top: 1px solid {_GREY_550};
    color: {_GREY_450};
    font-size: {_FONT_SIZE_SMALL};
}}

/* --- QDialogButtonBox ----------------------------------------------- */
QDialogButtonBox {{
    dialogbuttonbox-buttons-have-icons: 0;
}}

/* --- QMessageBox ---------------------------------------------------- */
QMessageBox {{
    background-color: {_GREY_800};
}}

QMessageBox QLabel {{
    color: {_GREY_300};
}}

QMessageBox QPushButton {{
    border-radius: 20px;
    min-width: 70px;
    padding: 4px 20px;
}}

/* --- QSplitter ------------------------------------------------------ */
QSplitter::handle {{
    background-color: {_GREY_550};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* --- QFrame separator ----------------------------------------------- */
QFrame[frameShape="4"], /* HLine */
QFrame[frameShape="5"]  /* VLine */ {{
    color: {_GREY_550};
}}
"""


def _build_palette_dark() -> _QPalette:
    """Build a QPalette matching the BealineMonitor dark theme."""
    pal = _QPalette()

    # Window / base
    pal.setColor(_QPalette.Window, _QColor(_GREY_1000))
    pal.setColor(_QPalette.WindowText, _QColor(_GREY_300))
    pal.setColor(_QPalette.Base, _QColor(_GREY_800))
    pal.setColor(_QPalette.AlternateBase, _QColor(_GREY_750))
    pal.setColor(_QPalette.Text, _QColor(_GREY_300))
    pal.setColor(_QPalette.BrightText, _QColor(_GREY_100))

    # Buttons – ButtonText controls Fusion arrow/indicator color
    pal.setColor(_QPalette.Button, _QColor(_GREY_700))
    pal.setColor(_QPalette.ButtonText, _QColor(_BLUE_400))

    # Selection / highlight
    pal.setColor(_QPalette.Highlight, _QColor(_BLUE_500))
    pal.setColor(_QPalette.HighlightedText, _QColor(_GREY_100))

    # Links
    pal.setColor(_QPalette.Link, _QColor(_BLUE_500))
    pal.setColor(_QPalette.LinkVisited, _QColor(_BLUE_400))

    # Tooltips
    pal.setColor(_QPalette.ToolTipBase, _QColor(_GREY_700))
    pal.setColor(_QPalette.ToolTipText, _QColor(_GREY_200))

    # Disabled states
    pal.setColor(_QPalette.Disabled, _QPalette.WindowText, _QColor(_GREY_550))
    pal.setColor(_QPalette.Disabled, _QPalette.Text, _QColor(_GREY_550))
    pal.setColor(_QPalette.Disabled, _QPalette.ButtonText, _QColor(_GREY_550))
    pal.setColor(_QPalette.Disabled, _QPalette.Base, _QColor(_GREY_800))

    # Midlight / dark / shadow
    pal.setColor(_QPalette.Midlight, _QColor(_GREY_650))
    pal.setColor(_QPalette.Mid, _QColor(_GREY_600))
    pal.setColor(_QPalette.Dark, _QColor(_GREY_900))
    pal.setColor(_QPalette.Shadow, _QColor(_GREY_1000))

    # Placeholder text
    pal.setColor(_QPalette.PlaceholderText, _QColor(_GREY_500))

    return pal


def apply_cloudscape_theme(
    app: _QApplication,
    *,
    use_fusion_style: bool = True,
) -> None:
    """
    Apply the Deadline Cloud Monitor dark theme to a QApplication.

    Args:
        app: The QApplication instance to theme.
        use_fusion_style: If True (default), set the Fusion style as the base
            style before applying the stylesheet.
    """
    if use_fusion_style:
        from qtpy.QtWidgets import QStyleFactory as _QStyleFactory

        app.setStyle(_QStyleFactory.create("Fusion"))

    app.setPalette(_build_palette_dark())
    app.setStyleSheet(_dark_stylesheet())

    # Install a global event filter to prevent scroll wheel from changing combo box
    # and spin box values (matches web UI behavior where scroll doesn't change selects)
    _blocker = _ScrollWheelBlocker(app)
    app.installEventFilter(_blocker)
    # Keep a reference so it doesn't get garbage collected
    app._scroll_blocker = _blocker  # type: ignore[attr-defined]


class _ScrollWheelBlocker(_QObject):
    """Blocks scroll wheel events on QComboBox and QSpinBox widgets."""

    def eventFilter(self, obj, event) -> bool:
        from qtpy.QtCore import QEvent
        from qtpy.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox

        if event.type() == QEvent.Type.Wheel:
            if isinstance(obj, (QComboBox, QSpinBox, QDoubleSpinBox)):
                event.ignore()
                return True
        return False


def apply_cloudscape_stylesheet(widget) -> None:
    """
    Apply the Deadline Cloud Monitor stylesheet to an individual widget.

    Use this when the QApplication is owned by a host application (e.g. a DCC)
    and you cannot safely call ``apply_cloudscape_theme`` on the app.

    Args:
        widget: Any QWidget — typically a top-level QDialog.
    """
    widget.setStyleSheet(_dark_stylesheet())


# Convenience color constants for inline styles elsewhere in the UI.
COLOR_PRIMARY = _BLUE_500
COLOR_PRIMARY_HOVER = _BLUE_400
COLOR_ACCENT = _AMAZON_ORANGE
COLOR_ACCENT_HOVER = _ORANGE_500
COLOR_ERROR = _RED_500
COLOR_SUCCESS = _GREEN_500
COLOR_WARNING = _YELLOW_600
COLOR_TEXT_DEFAULT = _GREY_300
COLOR_TEXT_SECONDARY = _GREY_450
COLOR_TEXT_DISABLED = _GREY_550
COLOR_BORDER_DEFAULT = _GREY_550
COLOR_BORDER_INPUT = _GREY_550
COLOR_BG_CONTAINER = _GREY_800
COLOR_BG_MAIN = _GREY_1000
COLOR_BG_SHADED = _GREY_750
COLOR_BG_SELECTED = _BLUE_900
