# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Side navigation panel widget inspired by the BealineMonitor's collapsible
left-hand navigation.  Collapsed state shows icons only; expanded state
shows icons + labels.  A toggle button appears on hover at the right edge.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from qtpy.QtCore import QSize, Qt, Signal, QTimer
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QFrame,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_RES = Path(__file__).parent.parent / "resources"

_COLLAPSED_WIDTH = 48
_EXPANDED_WIDTH = 200
_ICON_SIZE = QSize(16, 16)

# Colours from the BealineMonitor palette
_NAV_BG = "#202124"  # GREY_750 – $deadline-nav-background
_NAV_ITEM_HOVER = "#282a2d"  # GREY_700
_NAV_ITEM_SELECTED = "#191e2c"  # BLUE_900
_NAV_BORDER = "#5f6368"  # GREY_550 – nav border / toggle button border
_NAV_TEXT = "#d1d5db"  # GREY_300
_TOGGLE_HOVER_BG = "#e9ebed"  # GREY_200 – toggle button hover bg
_DIVIDER = "#5f6368"  # GREY_550


class _NavButton(QPushButton):
    """A single navigation item – icon-only when collapsed, icon+label when expanded."""

    def __init__(
        self,
        icon_path: str,
        label: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._label_text = label
        self._icon = QIcon(icon_path)
        self.setIcon(self._icon)
        self.setIconSize(_ICON_SIZE)
        self.setCheckable(True)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(label)
        self._expanded = False
        self._apply_style(selected=False)
        self.setText("")

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        if expanded:
            self.setText(f"  {self._label_text}")
            self.setMinimumWidth(_EXPANDED_WIDTH - 16)
        else:
            self.setText("")
            self.setMinimumWidth(0)

    def _apply_style(self, selected: bool) -> None:
        bg = _NAV_ITEM_SELECTED if selected else "transparent"
        self.setStyleSheet(
            f"QPushButton {{ background: {bg}; color: {_NAV_TEXT}; text-align: left;"
            f" padding: 6px 8px; border: none; border-radius: 6px; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {_NAV_ITEM_HOVER}; }}"
            f"QPushButton:checked {{ background: {_NAV_ITEM_SELECTED}; }}"
        )


class SideNavigationPanel(QWidget):
    """
    Collapsible side navigation panel.

    Signals:
        page_changed(int): emitted when the user clicks a nav item; carries the page index.
    """

    page_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._expanded = False
        self._nav_buttons: List[_NavButton] = []
        self._hover = False

        self.setFixedWidth(_COLLAPSED_WIDTH)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {_NAV_BG};")

        # Main vertical layout fills the entire panel
        self._nav_layout = QVBoxLayout(self)
        self._nav_layout.setContentsMargins(6, 8, 6, 8)
        self._nav_layout.setSpacing(2)

        # --- resource selectors section (farm, queue, storage profile) ---
        self._resources_layout = QVBoxLayout()
        self._resources_layout.setSpacing(6)
        self._resources_layout.setContentsMargins(0, 0, 0, 8)
        self._nav_layout.addLayout(self._resources_layout)
        self._resource_selectors: List = []

        # --- resource/page divider ---
        res_divider = QFrame()
        res_divider.setFrameShape(QFrame.HLine)
        res_divider.setStyleSheet(f"color: {_DIVIDER};")
        res_divider.setFixedHeight(1)
        self._nav_layout.addWidget(res_divider)

        # --- page nav buttons section ---
        self._pages_layout = QVBoxLayout()
        self._pages_layout.setSpacing(2)
        self._pages_layout.setContentsMargins(0, 6, 0, 0)
        self._nav_layout.addLayout(self._pages_layout)

        # Stretch to push footer to bottom
        self._nav_layout.addStretch(1)

        # --- divider ---
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"color: {_DIVIDER};")
        divider.setFixedHeight(1)
        self._nav_layout.addWidget(divider)

        # --- footer section ---
        self._footer_layout = QVBoxLayout()
        self._footer_layout.setSpacing(2)
        self._footer_layout.setContentsMargins(0, 6, 0, 0)
        self._nav_layout.addLayout(self._footer_layout)

        # Right-edge toggle strip and chevron button – created on first show
        self._toggle_strip: Optional[QWidget] = None
        self._toggle_btn: Optional[QPushButton] = None
        # Timer to delay hiding (prevents flicker when moving between nav and strip)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(200)
        self._hide_timer.timeout.connect(self._maybe_hide_toggle)

    # ----- public API -----

    def add_resource_selector(self, selector) -> None:
        """Add a NavResourceSelector to the resource selectors section."""
        self._resources_layout.addWidget(selector)
        self._resource_selectors.append(selector)

    def add_page(self, icon_filename: str, label: str) -> int:
        """Add a navigation page. Returns the page index."""
        btn = _NavButton(str(_RES / icon_filename), label, self)
        index = len(self._nav_buttons)
        btn.clicked.connect(lambda checked, i=index: self._on_nav_clicked(i))
        self._nav_buttons.append(btn)
        self._pages_layout.addWidget(btn)
        if index == 0:
            btn.setChecked(True)
        return index

    def add_footer_button(self, icon_filename: str, label: str, callback) -> QPushButton:
        """Add a button to the footer section (settings, help, etc.)."""
        btn = _NavButton(str(_RES / icon_filename), label, self)
        btn.setCheckable(False)
        btn.clicked.connect(callback)
        self._footer_layout.addWidget(btn)
        return btn

    def add_footer_widget(self, widget: QWidget) -> None:
        """Add an arbitrary widget to the footer (e.g. auth status)."""
        self._footer_layout.addWidget(widget)

    # ----- internal -----

    def _ensure_toggle_btn(self) -> None:
        """Create the right-edge toggle strip and chevron as children of our parent."""
        if self._toggle_strip is not None:
            return
        container = self.parentWidget() or self

        # Full-height clickable strip along the right edge
        self._toggle_strip = QWidget(container)
        self._toggle_strip.setCursor(Qt.PointingHandCursor)
        self._toggle_strip.setMouseTracking(True)
        self._toggle_strip.setStyleSheet(
            f"background: transparent; border-left: 1px solid {_NAV_BORDER};"
        )
        self._toggle_strip.installEventFilter(self)
        self._toggle_strip.hide()
        # Make the strip clickable by installing a mouse press handler
        self._toggle_strip.mousePressEvent = lambda e: self._toggle()

        # Small chevron button centered on the strip
        self._toggle_btn = QPushButton(container)
        self._toggle_btn.setFixedSize(14, 32)
        self._toggle_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._toggle)
        self._toggle_btn.setMouseTracking(True)
        self._toggle_btn.installEventFilter(self)
        self._update_toggle_icon()
        self._update_toggle_style(hovered=False)
        self._toggle_btn.hide()

    def _update_toggle_icon(self) -> None:
        if not self._toggle_btn:
            return
        icon_name = "nav_collapse.svg" if self._expanded else "nav_expand.svg"
        self._toggle_btn.setIcon(QIcon(str(_RES / icon_name)))
        self._toggle_btn.setIconSize(QSize(10, 16))

    def _update_toggle_style(self, hovered: bool) -> None:
        if not self._toggle_btn:
            return
        if hovered:
            self._toggle_btn.setStyleSheet(
                f"QPushButton {{ background: {_TOGGLE_HOVER_BG}; border: none;"
                f" border-radius: 0 4px 4px 0; padding: 0; }}"
            )
        else:
            self._toggle_btn.setStyleSheet(
                f"QPushButton {{ background: {_NAV_BG}; border: 1px solid {_NAV_BORDER};"
                f" border-left: none; border-radius: 0 4px 4px 0; padding: 0; }}"
            )

    def _position_toggle_btn(self) -> None:
        if not self._toggle_strip or not self._toggle_btn:
            return
        nav_rect = self.geometry()

        # Strip: full height, 3px wide, right at the nav edge
        strip_w = 3
        self._toggle_strip.setFixedSize(strip_w, nav_rect.height())
        self._toggle_strip.move(nav_rect.right() + 1, nav_rect.top())
        self._toggle_strip.raise_()

        # Chevron button: just to the right of the strip
        btn_x = nav_rect.right() + 1 + strip_w
        btn_y = nav_rect.top() + (nav_rect.height() // 2) - (self._toggle_btn.height() // 2)
        self._toggle_btn.move(btn_x, btn_y)
        self._toggle_btn.raise_()

    def _show_toggle(self) -> None:
        self._hide_timer.stop()
        self._ensure_toggle_btn()
        self._position_toggle_btn()
        if self._toggle_strip:
            self._toggle_strip.setStyleSheet(
                f"background: qlineargradient(y1:0, y2:1,"
                f" stop:0 transparent, stop:0.5 white, stop:1 transparent);"
                f" border-left: 1px solid {_NAV_BORDER};"
            )
            self._toggle_strip.show()
        if self._toggle_btn:
            self._toggle_btn.show()

    def _schedule_hide_toggle(self) -> None:
        self._hide_timer.start()

    def _maybe_hide_toggle(self) -> None:
        """Only hide if neither the nav, strip, nor chevron is hovered."""
        if self._toggle_btn and self._toggle_btn.underMouse():
            return
        if self._toggle_strip and self._toggle_strip.underMouse():
            return
        if self.underMouse():
            return
        if self._toggle_strip:
            self._toggle_strip.hide()
        if self._toggle_btn:
            self._toggle_btn.hide()

    def _on_nav_clicked(self, index: int) -> None:
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        width = _EXPANDED_WIDTH if self._expanded else _COLLAPSED_WIDTH
        self.setFixedWidth(width)
        self._update_toggle_icon()
        for btn in self._nav_buttons:
            btn.set_expanded(self._expanded)
        for sel in self._resource_selectors:
            sel.set_expanded(self._expanded)
        for i in range(self._footer_layout.count()):
            item = self._footer_layout.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, _NavButton):
                w.set_expanded(self._expanded)
        # Reposition after width change
        self._position_toggle_btn()

    def eventFilter(self, obj, event) -> bool:
        """Track hover on the toggle strip and button to prevent premature hiding."""
        if obj is self._toggle_btn or obj is self._toggle_strip:
            if event.type() == event.Type.Enter:
                self._hide_timer.stop()
                if obj is self._toggle_btn:
                    self._update_toggle_style(hovered=True)
            elif event.type() == event.Type.Leave:
                if obj is self._toggle_btn:
                    self._update_toggle_style(hovered=False)
                self._schedule_hide_toggle()
        return super().eventFilter(obj, event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._ensure_toggle_btn()
        self._position_toggle_btn()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_toggle_btn()

    def enterEvent(self, event) -> None:
        self._show_toggle()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._schedule_hide_toggle()
        super().leaveEvent(event)
