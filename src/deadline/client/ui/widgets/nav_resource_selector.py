# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Compact resource selectors for the side navigation panel.
Purple-bordered icon button that shows a label when expanded.
Clicking opens a context menu to change the selection.
Uses DeadlineUIController for async data loading.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QWidget,
)

from ...config import config_file
from ..controllers import DeadlineUIController

_RES = Path(__file__).parent.parent / "resources"

# BealineMonitor purple accent (CHARTS_PURPLE_500)
_PURPLE = "#8456CE"
_PURPLE_HOVER = "#9469D6"
_PURPLE_BG = "#1a1025"
_NAV_TEXT = "#d1d5db"

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
    QMenu::separator {{
        height: 1px;
        background-color: #5f6368;
        margin: 4px 8px;
    }}
"""


class _NavResourceSelector(QWidget):
    """
    Base class for nav panel resource selectors.

    Collapsed: purple-bordered icon button.
    Expanded: icon button + resource name label.
    Click opens a QMenu to select a resource.
    """

    background_exception = Signal(str, BaseException)
    selection_changed = Signal(str)

    def __init__(
        self,
        icon_filename: str,
        resource_label: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.resource_label = resource_label
        self._controller = DeadlineUIController.getInstance()
        self._icon = QIcon(str(_RES / icon_filename))
        self._expanded = False
        # Store items as (display_name, resource_id) tuples
        self._items: List[tuple] = []

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        # Icon button (always visible) — the click trigger
        self._icon_btn = QPushButton()
        self._icon_btn.setIcon(self._icon)
        self._icon_btn.setIconSize(QSize(16, 16))
        self._icon_btn.setFixedSize(32, 32)
        self._icon_btn.setCursor(Qt.PointingHandCursor)
        self._icon_btn.setToolTip(self.resource_label)
        self._icon_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 2px solid {_PURPLE};"
            f" border-radius: 8px; padding: 2px; }}"
            f"QPushButton:hover {{ border-color: {_PURPLE_HOVER};"
            f" background: {_PURPLE_BG}; }}"
        )
        self._icon_btn.clicked.connect(self._show_menu)
        layout.addWidget(self._icon_btn)

        # Name label (visible when expanded)
        self._name_label = QLabel()
        self._name_label.setStyleSheet(
            f"color: {_NAV_TEXT}; font-size: 12px; background: transparent;"
        )
        self._name_label.setCursor(Qt.PointingHandCursor)
        self._name_label.hide()
        self._name_label.mousePressEvent = lambda e: self._show_menu()
        layout.addWidget(self._name_label, stretch=1)

        # Track current selection
        self._selected_id = ""

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self._name_label.setVisible(expanded)

    def refresh_selected_id(self) -> None:
        """Refresh the selected item from config."""
        self._selected_id = config_file.get_setting(self._get_setting_name()) or ""
        self._update_display()

    def _get_setting_name(self) -> str:
        raise NotImplementedError

    def _update_display(self) -> None:
        # Find display name for current ID
        text = self._selected_id
        for name, rid in self._items:
            if rid == self._selected_id:
                text = name
                break
        if not text:
            text = f"No {self.resource_label.lower()}"
        self._name_label.setText(text)
        self._icon_btn.setToolTip(f"{self.resource_label}: {text}")

    def _show_menu(self) -> None:
        if not self._items:
            return
        menu = QMenu(self)
        menu.setStyleSheet(_MENU_STYLE)

        for name, resource_id in self._items:
            action = menu.addAction(name)
            action.setData(resource_id)
            if resource_id == self._selected_id:
                action.setEnabled(False)  # dim the current selection

        # Show below the icon button
        pos = self._icon_btn.mapToGlobal(self._icon_btn.rect().bottomLeft())
        chosen = menu.exec_(pos)
        if chosen and chosen.data():
            self._selected_id = chosen.data()
            config_file.set_setting(self._get_setting_name(), self._selected_id)
            self._update_display()
            self.selection_changed.emit(self._selected_id)

    def _handle_list_update(self, items: List) -> None:
        self._items = []
        for item in items:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                self._items.append((item[0], item[1]))
        self.refresh_selected_id()

    def _handle_loading(self, is_loading: bool) -> None:
        if is_loading:
            self._name_label.setText(f"Loading {self.resource_label.lower()}...")
            self._icon_btn.setToolTip(f"Loading {self.resource_label.lower()}...")


class NavFarmComboBox(_NavResourceSelector):
    """Farm selector for the side nav."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("nav_farm.svg", "Farm", parent)
        self._controller.farms_updated.connect(self._handle_list_update, Qt.QueuedConnection)
        self._controller.farms_loading.connect(self._handle_loading, Qt.QueuedConnection)

    def _get_setting_name(self) -> str:
        return "defaults.farm_id"

    def refresh_list(self) -> None:
        """Trigger an async refresh of the farms list."""
        self._controller.refresh_farms()


class NavQueueComboBox(_NavResourceSelector):
    """Queue selector for the side nav."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("nav_queue.svg", "Queue", parent)
        self._controller.queues_updated.connect(self._handle_list_update, Qt.QueuedConnection)
        self._controller.queues_loading.connect(self._handle_loading, Qt.QueuedConnection)

    def _get_setting_name(self) -> str:
        return "defaults.queue_id"

    def refresh_list(self) -> None:
        """Trigger an async refresh of the queues list."""
        farm_id = config_file.get_setting("defaults.farm_id")
        if farm_id:
            self._controller.refresh_queues(farm_id=farm_id)


class NavStorageProfileComboBox(_NavResourceSelector):
    """Storage profile selector for the side nav."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("nav_storage.svg", "Storage Profile", parent)
        self._controller.storage_profiles_updated.connect(
            self._handle_list_update, Qt.QueuedConnection
        )
        self._controller.storage_profiles_loading.connect(self._handle_loading, Qt.QueuedConnection)

    def _get_setting_name(self) -> str:
        return "settings.storage_profile_id"

    def refresh_list(self) -> None:
        """Trigger an async refresh of the storage profiles list."""
        farm_id = config_file.get_setting("defaults.farm_id")
        queue_id = config_file.get_setting("defaults.queue_id")
        if farm_id and queue_id:
            self._controller.refresh_storage_profiles(farm_id=farm_id, queue_id=queue_id)
