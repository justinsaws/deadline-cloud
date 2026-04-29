# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
UI widgets for the Scene Settings tab.
"""

import os
from typing import Optional

from qtpy.QtCore import Qt  # type: ignore
from .._utils import tr
from qtpy.QtWidgets import (  # type: ignore
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QTextEdit,
    QWidget,
)

from ..dataclasses import CliJobSettings
from .path_widgets import DirectoryPickerWidget


class CliJobSettingsWidget(QWidget):
    """
    Widget containing job setup specific to CLI jobs.

    Args:
        initial_settings (CliJobSettings): dataclass containing the job-specific settings.
        parent: The parent Qt Widget.
    """

    def __init__(self, initial_settings: CliJobSettings, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self._build_ui()
        self._load_initial_settings(initial_settings)

    def _set_enabled_with_label(self, prop_name: str, enabled: bool):
        """Set the enabled status of a control and its label"""
        getattr(self, prop_name).setEnabled(enabled)
        getattr(self, prop_name + "_label").setEnabled(enabled)

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.bash_script = QTextEdit()
        if os.name == "nt":
            font_family = "Consolas"
        elif os.name == "darwin":
            font_family = "Monaco"
        else:
            font_family = "Monospace"
        font = self.bash_script.currentFont()
        font.setFamily(font_family)
        font.setFixedPitch(True)
        font.setKerning(False)
        font.setPointSize(font.pointSize() + 1)
        self.bash_script.setCurrentFont(font)
        self.bash_script.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addRow(self.bash_script)

        # Array parameter: checkbox + name field on the same row
        array_row = QHBoxLayout()
        self.use_array_parameter_chck = QCheckBox(tr("Use array parameter"), self)
        self.array_parameter_name = QLineEdit(self)
        array_row.addWidget(self.use_array_parameter_chck)
        array_row.addWidget(self.array_parameter_name)
        layout.addRow(array_row)
        self.use_array_parameter_chck.stateChanged.connect(self.use_array_parameter_changed)

        self.array_parameter_values_label = QLabel(tr("Array parameter values"))
        self.array_parameter_values = QLineEdit(self)
        layout.addRow(self.array_parameter_values_label, self.array_parameter_values)

        self.data_dir_label = QLabel(tr("Data directory"))
        self.data_dir_edit = DirectoryPickerWidget(
            initial_directory=os.path.expanduser(os.path.join("~", "CLIJobData")),
            directory_label="Data directory",
            parent=self,
        )
        layout.addRow(self.data_dir_label, self.data_dir_edit)

        self.file_format_label = QLabel(tr("Template file format"))
        self.file_format_box = QComboBox(parent=self)
        self.file_format_box.addItems(["YAML", "JSON"])
        layout.addRow(self.file_format_label, self.file_format_box)

    def _load_initial_settings(self, initial_settings: CliJobSettings):
        self.bash_script.setPlainText(initial_settings.bash_script_contents)
        self.use_array_parameter_chck.setChecked(initial_settings.use_array_parameter)
        self.array_parameter_name.setText(initial_settings.array_parameter_name)
        self.array_parameter_values.setText(initial_settings.array_parameter_values)
        self.file_format_box.setCurrentText(initial_settings.file_format)

    def update_settings(self, settings: CliJobSettings):
        """
        Update a settings object with the latest values.
        """
        settings.bash_script_contents = self.bash_script.toPlainText()
        settings.use_array_parameter = self.use_array_parameter_chck.isChecked()
        settings.array_parameter_name = self.array_parameter_name.text()
        settings.array_parameter_values = self.array_parameter_values.text()
        settings.data_dir = os.path.expanduser(self.data_dir_edit.text())
        settings.file_format = self.file_format_box.currentText()

    def use_array_parameter_changed(self, state: int):
        enabled = Qt.CheckState(state) == Qt.Checked
        self.array_parameter_name.setEnabled(enabled)
        self._set_enabled_with_label("array_parameter_values", enabled)
