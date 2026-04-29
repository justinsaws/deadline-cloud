# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Styled button widgets that apply the BealineMonitor dark theme directly,
bypassing Qt stylesheet engine limitations with QDialogButtonBox.
"""

from __future__ import annotations

from typing import Optional

from qtpy.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)

# BealineMonitor palette
_GREY_100 = "#fbfbfb"
_GREY_300 = "#d1d5db"
_GREY_450 = "#9aa0a6"
_GREY_550 = "#5f6368"
_GREY_600 = "#3c4043"
_GREY_700 = "#282a2d"
_GREY_800 = "#17181b"
_GREY_900 = "#0e1013"
_AMAZON_ORANGE = "#ff9900"
_ORANGE_500 = "#fb8213"

_NORMAL_STYLE = f"""
    QPushButton {{
        background-color: {_GREY_800};
        color: {_GREY_300};
        border: 2px solid {_GREY_550};
        border-radius: 20px;
        padding: 6px 20px;
        font-weight: 700;
        font-size: 14px;
        min-height: 24px;
        min-width: 70px;
    }}
    QPushButton:hover {{
        background-color: {_GREY_700};
        border-color: {_GREY_450};
        color: {_GREY_100};
    }}
    QPushButton:pressed {{
        background-color: {_GREY_600};
        border-color: {_GREY_550};
        color: {_GREY_100};
    }}
    QPushButton:disabled {{
        background-color: {_GREY_800};
        border-color: {_GREY_600};
        color: {_GREY_550};
    }}
"""

_PRIMARY_STYLE = f"""
    QPushButton {{
        background-color: {_AMAZON_ORANGE};
        color: {_GREY_900};
        border: 2px solid {_AMAZON_ORANGE};
        border-radius: 20px;
        padding: 6px 24px;
        font-weight: 700;
        font-size: 14px;
        min-height: 24px;
        min-width: 70px;
    }}
    QPushButton:hover {{
        background-color: {_ORANGE_500};
        border-color: {_ORANGE_500};
    }}
    QPushButton:pressed {{
        background-color: {_ORANGE_500};
        border-color: {_ORANGE_500};
    }}
    QPushButton:disabled {{
        background-color: {_GREY_700};
        border-color: {_GREY_700};
        color: {_GREY_550};
    }}
"""


class StyledButton(QPushButton):
    """A QPushButton with the BealineMonitor normal button style baked in."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setStyleSheet(_NORMAL_STYLE)


class PrimaryButton(QPushButton):
    """A QPushButton with the BealineMonitor primary (orange) button style baked in."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setStyleSheet(_PRIMARY_STYLE)


class StyledButtonBox(QWidget):
    """
    A replacement for QDialogButtonBox that uses StyledButton and PrimaryButton
    to guarantee the rounded pill-shaped appearance.

    Usage:
        box = StyledButtonBox()
        box.add_button("Cancel", callback=dialog.reject)
        box.add_button("Ok", primary=True, callback=dialog.accept)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)
        self._layout.addStretch(1)
        self._buttons: list[QPushButton] = []

    def add_button(
        self,
        text: str,
        *,
        primary: bool = False,
        callback=None,
    ) -> QPushButton:
        """Add a button. Primary buttons get the orange style."""
        btn = PrimaryButton(text, self) if primary else StyledButton(text, self)
        if callback:
            btn.clicked.connect(callback)
        self._layout.addWidget(btn)
        self._buttons.append(btn)
        return btn

    def add_stretch_before(self) -> None:
        """Already has a leading stretch by default. Call this to add more."""
        self._layout.insertStretch(0, 1)
