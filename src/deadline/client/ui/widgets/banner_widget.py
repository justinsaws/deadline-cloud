# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Flashbar-style banner widget for displaying notifications at the top of the
content area.  Inspired by the BealineMonitor's Cloudscape Flashbar component.

Supports error, warning, success, and info types with action buttons,
dismissibility, and embedded progress bars.

Updates are done via slots on _BannerItemWidget so that the banner stack
can call set_header / set_progress / set_detail without recreating widgets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_RES = Path(__file__).parent.parent / "resources"

_COLORS = {
    "error": {"bg": "#340606", "border": "#ff3131", "icon": str(_RES / "status_warning.svg")},
    "warning": {"bg": "#1d1906", "border": "#ffe457", "icon": str(_RES / "status_warning.svg")},
    "success": {"bg": "#001a02", "border": "#29ad32", "icon": str(_RES / "status_ok.svg")},
    "info": {"bg": "#191e2c", "border": "#5c94ff", "icon": str(_RES / "status_loading.svg")},
}

_TEXT_COLOR = "#d1d5db"
_TEXT_DIM = "#9aa0a6"
_BTN_STYLE = (
    "QPushButton { background: transparent; color: #8cb4ff; border: 1px solid #5f6368;"
    " border-radius: 12px; padding: 3px 12px; font-size: 12px; font-weight: 700; }"
    "QPushButton:hover { background: #282a2d; border-color: #8cb4ff; }"
)
_DISMISS_STYLE = (
    "QPushButton { background: transparent; border: none; color: #9aa0a6;"
    " font-size: 16px; padding: 0 4px; }"
    "QPushButton:hover { color: #fbfbfb; }"
)
_EXPAND_STYLE = (
    "QPushButton { background: transparent; border: none; color: #8cb4ff;"
    " font-size: 12px; padding: 0; }"
    "QPushButton:hover { color: #5c94ff; text-decoration: underline; }"
)


@dataclass
class BannerAction:
    """An action button to display in a banner item."""

    label: str
    callback: Callable[[], None]


@dataclass
class BannerItem:
    """A single notification to display in the banner."""

    item_id: str
    banner_type: str = "info"
    header: str = ""
    body: str = ""
    dismissible: bool = True
    actions: List[BannerAction] = field(default_factory=list)
    progress_value: Optional[int] = None
    progress_label: str = ""
    expandable_detail: str = ""


class _BannerItemWidget(QFrame):
    """
    A single banner notification.  All mutable sub-widgets are created
    up-front and shown/hidden as needed.  Public set_* methods act as
    slots so the BannerStack (or any signal) can update content in place.
    """

    dismissed = Signal(str)

    def __init__(self, item: BannerItem, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.item = item
        self._detail_visible = False
        self._build_ui()

    # ── construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        colors = _COLORS.get(self.item.banner_type, _COLORS["info"])
        self.setStyleSheet(
            f"_BannerItemWidget {{ background: {colors['bg']};"
            f" border: 1px solid {colors['border']}; border-radius: 8px; }}"
        )
        self.setFrameShape(QFrame.StyledPanel)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 8, 12, 8)
        outer.setSpacing(4)

        # ── row 1: icon | header | actions | dismiss ──
        top = QHBoxLayout()
        top.setSpacing(8)

        icon = QLabel()
        icon.setPixmap(QPixmap(colors["icon"]).scaled(16, 16, mode=Qt.SmoothTransformation))
        icon.setFixedSize(20, 20)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:transparent;")
        top.addWidget(icon)

        self._header = QLabel(self.item.header)
        self._header.setStyleSheet(
            f"color:{_TEXT_COLOR};font-weight:700;font-size:13px;background:transparent;"
        )
        self._header.setWordWrap(True)
        self._header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top.addWidget(self._header, stretch=1)

        self._action_widgets: list[QPushButton] = []
        for act in self.item.actions:
            b = QPushButton(act.label)
            b.setStyleSheet(_BTN_STYLE)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(act.callback)
            top.addWidget(b)
            self._action_widgets.append(b)

        if self.item.dismissible:
            d = QPushButton("\u2715")
            d.setStyleSheet(_DISMISS_STYLE)
            d.setFixedSize(20, 20)
            d.setCursor(Qt.PointingHandCursor)
            d.clicked.connect(lambda: self.dismissed.emit(self.item.item_id))
            top.addWidget(d)

        outer.addLayout(top)

        # ── row 2: body ──
        self._body = QLabel(self.item.body)
        self._body.setStyleSheet(
            f"color:{_TEXT_DIM};font-size:12px;background:transparent;padding-left:28px;"
        )
        self._body.setWordWrap(True)
        self._body.setVisible(bool(self.item.body))
        outer.addWidget(self._body)

        # ── row 3: progress ──
        prog_box = QVBoxLayout()
        prog_box.setContentsMargins(28, 0, 0, 0)
        prog_box.setSpacing(2)

        self._prog_label = QLabel(self.item.progress_label)
        self._prog_label.setStyleSheet(f"color:{_TEXT_DIM};font-size:12px;background:transparent;")
        has_prog = self.item.progress_value is not None
        self._prog_label.setVisible(has_prog)
        prog_box.addWidget(self._prog_label)

        self._prog_bar = QProgressBar()
        self._prog_bar.setRange(0, 100)
        self._prog_bar.setValue(self.item.progress_value or 0)
        self._prog_bar.setFixedHeight(6)
        self._prog_bar.setTextVisible(False)
        self._prog_bar.setStyleSheet(
            f"QProgressBar{{background:#282a2d;border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{colors['border']};border-radius:3px;}}"
        )
        self._prog_bar.setVisible(has_prog)
        prog_box.addWidget(self._prog_bar)
        outer.addLayout(prog_box)

        # ── row 4: expandable detail ──
        det_row = QHBoxLayout()
        det_row.setContentsMargins(28, 0, 0, 0)
        self._expand_btn = QPushButton("\u25b6 Show details")
        self._expand_btn.setStyleSheet(_EXPAND_STYLE)
        self._expand_btn.setCursor(Qt.PointingHandCursor)
        self._expand_btn.clicked.connect(self._toggle_detail)
        self._expand_btn.setVisible(bool(self.item.expandable_detail))
        det_row.addWidget(self._expand_btn)
        det_row.addStretch()
        outer.addLayout(det_row)

        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setPlainText(self.item.expandable_detail)
        self._detail.setMaximumHeight(200)
        self._detail.setStyleSheet(
            f"QTextEdit{{background:#17181b;color:{_TEXT_DIM};border:1px solid #3c4043;"
            f"border-radius:4px;font-size:12px;font-family:monospace;padding:4px;}}"
        )
        self._detail.hide()
        outer.addWidget(self._detail)

    # ── public slots ──────────────────────────────────────────────

    def set_header(self, text: str) -> None:
        self._header.setText(text)

    def set_body(self, text: str) -> None:
        self._body.setText(text)
        self._body.setVisible(bool(text))

    def set_progress(self, value: int, label: str = "") -> None:
        self._prog_bar.setValue(value)
        self._prog_bar.show()
        if label:
            self._prog_label.setText(label)
        self._prog_label.show()

    def set_detail(self, text: str) -> None:
        self._detail.setPlainText(text)
        self._expand_btn.setVisible(bool(text))

    def hide_progress(self) -> None:
        self._prog_bar.hide()
        self._prog_label.hide()

    # ── internal ──────────────────────────────────────────────────

    def _toggle_detail(self) -> None:
        self._detail_visible = not self._detail_visible
        self._detail.setVisible(self._detail_visible)
        self._expand_btn.setText(
            "\u25bc Hide details" if self._detail_visible else "\u25b6 Show details"
        )


class BannerStack(QWidget):
    """
    A vertical stack of banner notifications.

    * ``put()``  – create a new banner (only if the id is new).
    * ``update()`` – update header / body / progress / detail on an existing banner.
    * ``replace()`` – destroy the old widget and create a fresh one (type/actions changed).
    * ``remove()`` – hide a banner.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 4)
        self._layout.setSpacing(4)
        self._widgets: dict[str, _BannerItemWidget] = {}
        self._active_ids: set[str] = set()  # track which banners should be visible
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet("background: transparent;")
        self.hide()

    # ── public API ────────────────────────────────────────────────

    def put(self, item_id: str, item: BannerItem) -> _BannerItemWidget:
        """
        Create a banner if it doesn't exist, or replace it if the type changed.
        For simple text/progress updates on an existing banner, use ``update()``
        instead — it's cheaper.
        """
        item.item_id = item_id

        if item_id in self._widgets:
            old = self._widgets[item_id]
            if old.item.banner_type == item.banner_type:
                # Same type — just update content in place
                old.set_header(item.header)
                old.set_body(item.body)
                if item.progress_value is not None:
                    old.set_progress(item.progress_value, item.progress_label)
                else:
                    old.hide_progress()
                old.set_detail(item.expandable_detail)
                old.item = item
                old.show()
                self._active_ids.add(item_id)
                self._update_visibility()
                return old
            else:
                # Type changed — must rebuild (colours, icon differ)
                return self._replace(item_id, item)
        else:
            return self._create(item_id, item)

    def update_banner(
        self,
        item_id: str,
        *,
        header: Optional[str] = None,
        body: Optional[str] = None,
        progress_value: Optional[int] = None,
        progress_label: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        """Update individual fields on an existing banner without rebuilding."""
        w = self._widgets.get(item_id)
        if w is None:
            return
        if header is not None:
            w.set_header(header)
        if body is not None:
            w.set_body(body)
        if progress_value is not None:
            w.set_progress(progress_value, progress_label or "")
        if detail is not None:
            w.set_detail(detail)

    def remove(self, item_id: str) -> None:
        """Hide a banner."""
        w = self._widgets.get(item_id)
        if w:
            w.hide()
        self._active_ids.discard(item_id)
        self._update_visibility()

    def has(self, item_id: str) -> bool:
        return item_id in self._active_ids

    def clear(self) -> None:
        for w in self._widgets.values():
            w.hide()
        self._active_ids.clear()
        self._update_visibility()

    # ── internal ──────────────────────────────────────────────────

    def _create(self, item_id: str, item: BannerItem) -> _BannerItemWidget:
        w = _BannerItemWidget(item, self)
        w.dismissed.connect(self.remove)
        self._layout.insertWidget(0, w)
        self._widgets[item_id] = w
        self._active_ids.add(item_id)
        self._update_visibility()
        return w

    def _replace(self, item_id: str, item: BannerItem) -> _BannerItemWidget:
        old = self._widgets.pop(item_id, None)
        if old:
            old.hide()
            self._layout.removeWidget(old)
            old.deleteLater()
        return self._create(item_id, item)

    def _update_visibility(self) -> None:
        self.setVisible(bool(self._active_ids))
