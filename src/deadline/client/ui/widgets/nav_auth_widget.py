# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Compact auth status widget for the side navigation panel.
Purple-bordered icon button matching the resource selectors.
Shows profile name when expanded, opens a menu for login/logout/switch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QWidget,
)

from ..deadline_authentication_status import DeadlineAuthenticationStatus
from ...config import config_file

_RES = Path(__file__).parent.parent / "resources"

_PURPLE = "#8456CE"
_PURPLE_HOVER = "#9469D6"
_PURPLE_BG = "#1a1025"
_NAV_TEXT = "#d1d5db"
_NAV_TEXT_DIM = "#9aa0a6"
_GREEN = "#29ad32"
_YELLOW = "#ffe457"
_RED = "#ff3131"

_MENU_STYLE = f"""
    QMenu {{
        background-color: #17181b;
        border: 1px solid {_PURPLE};
        border-radius: 8px;
        padding: 4px;
        color: {_NAV_TEXT};
        font-size: 13px;
    }}
    QMenu::item {{
        padding: 6px 16px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background-color: {_PURPLE_BG};
    }}
    QMenu::item:disabled {{
        color: {_NAV_TEXT_DIM};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: #5f6368;
        margin: 4px 8px;
    }}
"""


class NavAuthWidget(QWidget):
    """
    Compact auth widget for the side nav footer.
    Matches the purple-bordered icon style of the resource selectors.
    """

    login_clicked = Signal()
    logout_clicked = Signal()
    switch_profile_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._expanded = False
        self._auth_status = DeadlineAuthenticationStatus.getInstance()
        self._auth_status.auth_status_changed.connect(self._refresh)
        self._auth_status.api_availability_changed.connect(self._refresh)

        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        self._icon_btn = QPushButton()
        self._icon_btn.setIcon(QIcon(str(_RES / "nav_user.svg")))
        self._icon_btn.setIconSize(QSize(16, 16))
        self._icon_btn.setFixedSize(32, 32)
        self._icon_btn.setCursor(Qt.PointingHandCursor)
        self._icon_btn.clicked.connect(self._show_menu)
        layout.addWidget(self._icon_btn)

        self._name_label = QLabel()
        self._name_label.setStyleSheet(
            f"color: {_NAV_TEXT}; font-size: 12px; background: transparent;"
        )
        self._name_label.setCursor(Qt.PointingHandCursor)
        self._name_label.mousePressEvent = lambda e: self._show_menu()
        self._name_label.hide()
        layout.addWidget(self._name_label, stretch=1)

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self._name_label.setVisible(expanded)

    def _get_profile_name(self) -> str:
        return config_file.get_setting("defaults.aws_profile_name") or "(default)"

    def _get_status_color(self) -> str:
        api = self._auth_status.api_availability
        if api is True:
            return _GREEN
        elif api is False:
            return _RED
        return _YELLOW  # still loading

    def _refresh(self) -> None:
        color = self._get_status_color()
        self._icon_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 2px solid {color};"
            f" border-radius: 8px; padding: 2px; }}"
            f"QPushButton:hover {{ border-color: {_PURPLE_HOVER};"
            f" background: {_PURPLE_BG}; }}"
        )
        profile = self._get_profile_name()
        self._name_label.setText(profile)
        self._icon_btn.setToolTip(f"Profile: {profile}")

    def _show_menu(self) -> None:
        from ... import api as deadline_api

        menu = QMenu(self)
        menu.setStyleSheet(_MENU_STYLE)

        # Profile header (disabled, just for display)
        profile_action = menu.addAction(f"Profile: {self._get_profile_name()}")
        profile_action.setEnabled(False)

        menu.addSeparator()

        # Status-dependent actions
        auth = self._auth_status
        if auth.api_availability is True:
            menu.addAction("Log out", self.logout_clicked.emit)
        else:
            creds_source = getattr(auth, "_DeadlineAuthenticationStatus__creds_source", None)
            if creds_source == deadline_api.AwsCredentialsSource.DEADLINE_CLOUD_MONITOR_LOGIN:
                menu.addAction("Log in", self.login_clicked.emit)

        menu.addAction("Switch profile", self.switch_profile_clicked.emit)

        pos = self._icon_btn.mapToGlobal(self._icon_btn.rect().bottomLeft())
        menu.exec_(pos)
