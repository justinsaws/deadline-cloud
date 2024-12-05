# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
"""
Provides a modal dialog box for logging in to AWS Deadline Cloud.

Example code:
    from deadline.client.ui.dialogs import DeadlineLoginDialog
    if DeadlineLoginDialog.login(parent=self):
        print("Logged in successfully.")
    else:
        print("Failed to log in.")
"""

__all__ = ["DeadlineLoginDialog"]

import html
import logging
from configparser import ConfigParser
from typing import Optional

from qtpy.QtCore import Signal, QThread, Qt
from qtpy.QtWidgets import (  # pylint: disable=import-error; type: ignore
    QMessageBox,
)

from ... import api
from ...api._session import AwsCredentialsSource


logger = logging.getLogger(__name__)


class _DeadlineLoginThread(QThread):

    login_succeeded = Signal(str, Exception)
    login_message = Signal(str)

    def __init__(self, config, parent=None):
        super(_DeadlineLoginThread, self).__init__(parent)

        self._config = config

    def run(self):
        """
        This function gets started in a background thread to run the login handshake. It
        polls the `self.canceled` flag for cancellation, and fills in details about the
        login when they become available.
        """
        try:

            def on_pending_authorization(**kwargs):
                if (
                    kwargs["credentials_source"]
                    == AwsCredentialsSource.DEADLINE_CLOUD_MONITOR_LOGIN
                ):
                    self.login_message.emit(
                        "Opening Deadline Cloud monitor. Please log in before returning here."
                    )

            success_message = api.login(
                on_pending_authorization,
                on_cancellation_check=self.isInterruptionRequested,
                config=self._config,
            )
            self.login_succeeded.emit(success_message, None)
        except Exception as e:
            # Send the exception to the dialog
            self.login_succeeded.emit(None, e)


class DeadlineLoginDialog(QMessageBox):
    """
    A modal dialog box for logging in to AWS Deadline Cloud. The return value
    of the static DeadlineLoginDialog.login() and the modal exec()
    is True when the login is successful, False otherwise.

    Example code:
        if DeadlineLoginDialog.login(parent=self):
            print("Logged in successfully.")
        else:
            print("Failed to log in.")
    """

    # This signal is sent when the background login thread raises an exception.
    login_thread_exception = Signal(BaseException)
    # This signal is sent when the background login thread wants to change the
    # displayed message.
    login_thread_message = Signal(str)
    # This signal is sent when the background login thread succeeds.
    login_thread_succeeded = Signal(str)

    @staticmethod
    def login(
        parent=None,
        force_refresh=False,
        close_on_success=True,
        config: Optional[ConfigParser] = None,
    ) -> QMessageBox:
        """
        Static method that runs the Deadline Login Dialog. Returns True for
        a successful login, False otherwise.

        Args:
            force_refresh (bool, default False): Forces a re-login even when already authorized.
            close_on_success (bool, default True): Closes the dialog on successful login, instead
                   of showing a "successfully logged in" message.
            config (ConfigParser, optional): The AWS Deadline Cloud configuration
                    object to use instead of the config file.
        """
        deadline_login = DeadlineLoginDialog(
            parent=parent,
            close_on_success=close_on_success,
            config=config,
        )
        return deadline_login

    def __init__(
        self,
        parent=None,
        close_on_success=True,
        config: Optional[ConfigParser] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.close_on_success = close_on_success
        self.config = config
        self.__login_thread = None

        self.setWindowTitle("Log in to AWS Deadline Cloud")
        self.setText("Logging you in...")
        self.setStandardButtons(QMessageBox.Cancel)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        self._start_login()

    def _start_login(self) -> None:
        """
        Starts the background login thread.
        """

        logger.debug("Starting login thread...")

        self.__login_thread = _DeadlineLoginThread(self.config, self.parentWidget())
        self.__login_thread.login_succeeded.connect(self.handle_login_thread_succeeded)
        self.__login_thread.login_message.connect(self.handle_login_message)
        self.destroyed.connect(self.__login_thread.requestInterruption)
        self.__login_thread.start()

    def handle_login_message(self, message: str) -> None:
        """
        Handles the signal sent from the background login thread when
        a message is sent.
        """
        self.setText(message)

    def handle_login_thread_succeeded(
        self, success_message: Optional[str], e: Optional[Exception]
    ) -> None:
        """
        Handles the signal sent from the background login thread when
        the login has succeeded.
        """
        if success_message:
            if self.close_on_success:
                # Effectively clicks on "OK"
                self.accept()
            else:
                self.setStandardButtons(QMessageBox.Ok)
                self.setIcon(QMessageBox.Information)
                self.setText(f"Successfully logged into: <br/><br/>{html.escape(success_message)}")
        elif e:
            self.setStandardButtons(QMessageBox.Close)
            self.setIcon(QMessageBox.Warning)
            self.setText(f"Failed to log in to AWS Deadline Cloud:<br/><br/>{html.escape(str(e))}")

    def exec_(self) -> bool:
        """
        Runs the modal login dialog, returning True if the login was
        successful, False otherwise.
        """
        return super().exec_() == QMessageBox.Ok
