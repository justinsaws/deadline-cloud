# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Non-modal job submission that reports progress through the banner widget
instead of a separate modal dialog.

Each submission gets a unique banner ID so multiple submissions can stack.
Completed banners (success/error/canceled) remain until the user dismisses them.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget

from ..widgets.banner_widget import BannerAction, BannerItem, BannerStack
from ._job_submission_worker import JobSubmissionWorker

logger = logging.getLogger(__name__)


class BannerSubmissionHandler:
    """
    Manages a single job submission using the banner for progress display.
    Each instance gets a unique ID so multiple submissions can coexist.

    Create a new handler for each submission.
    """

    _counter = 0

    def __init__(self, banner: BannerStack, parent: QWidget):
        self._banner = banner
        self._parent = parent
        self._worker: Optional[JobSubmissionWorker] = None
        self._log_lines: list[str] = []
        self._canceled = False

        # Unique IDs for this submission
        BannerSubmissionHandler._counter += 1
        self._id = f"submit-{BannerSubmissionHandler._counter}-{int(time.time())}"
        self._confirm_id = f"{self._id}-confirm"

        self.on_succeeded: Optional[Any] = None

    def start(self, **kwargs) -> None:
        """Start the submission in a background thread."""
        self._canceled = False
        self._log_lines = []

        # Create the initial progress banner
        self._banner.put(
            self._id,
            BannerItem(
                item_id=self._id,
                banner_type="info",
                header="Preparing submission...",
                progress_value=0,
                progress_label="Preparing files...",
                dismissible=False,
                actions=[BannerAction("Cancel", self._cancel)],
            ),
        )

        kwargs["from_gui"] = True
        kwargs["submitter_name"] = kwargs.get("submitter_name", "CustomGUI")

        self._worker = JobSubmissionWorker(self._parent)
        self._worker.print_message.connect(self._on_print, Qt.QueuedConnection)
        self._worker.hashing_progress.connect(self._on_hashing_progress, Qt.QueuedConnection)
        self._worker.upload_progress.connect(self._on_upload_progress, Qt.QueuedConnection)
        self._worker.confirmation_requested.connect(
            self._on_confirmation_requested, Qt.QueuedConnection
        )
        self._worker.succeeded.connect(self._on_succeeded, Qt.QueuedConnection)
        self._worker.failed.connect(self._on_failed, Qt.QueuedConnection)

        self._worker.set_submission_kwargs(**kwargs)
        self._worker.start()

    def _cancel(self) -> None:
        self._canceled = True
        if self._worker:
            self._worker.cancel()
        self._banner.put(
            self._id,
            BannerItem(
                item_id=self._id,
                banner_type="warning",
                header="Canceling submission...",
                dismissible=False,
            ),
        )

    def _on_print(self, message: str) -> None:
        self._log_lines.append(message)
        self._banner.update_banner(self._id, detail="\n".join(self._log_lines))

    def _on_hashing_progress(self, metadata) -> None:
        self._banner.update_banner(
            self._id,
            header="Hashing job attachments...",
            progress_value=int(metadata.progress),
            progress_label=metadata.progressMessage,
            detail="\n".join(self._log_lines),
        )

    def _on_upload_progress(self, metadata) -> None:
        self._banner.update_banner(
            self._id,
            header="Uploading job attachments...",
            progress_value=int(metadata.progress),
            progress_label=metadata.progressMessage,
            detail="\n".join(self._log_lines),
        )

    def _on_confirmation_requested(self, message: str, default_response: bool) -> None:
        if self._worker is None or self._worker.is_canceled:
            return

        def _accept():
            if self._worker:
                self._worker.set_confirmation_result(True)
            self._banner.remove(self._confirm_id)

        def _reject():
            if self._worker:
                self._worker.set_confirmation_result(False)
            self._banner.remove(self._confirm_id)

        self._banner.put(
            self._confirm_id,
            BannerItem(
                item_id=self._confirm_id,
                banner_type="warning",
                header="Confirmation required",
                body=message,
                dismissible=False,
                actions=[
                    BannerAction("Continue", _accept),
                    BannerAction("Cancel", _reject),
                ],
            ),
        )

    def _on_succeeded(self, job_id: str) -> None:
        self._banner.remove(self._confirm_id)
        if job_id:
            self._banner.put(
                self._id,
                BannerItem(
                    item_id=self._id,
                    banner_type="success",
                    header=f"Job submitted successfully (ID: {job_id})",
                    expandable_detail="\n".join(self._log_lines),
                    dismissible=True,
                ),
            )
            if self.on_succeeded:
                self.on_succeeded(job_id)
        else:
            if self._canceled:
                self._banner.put(
                    self._id,
                    BannerItem(
                        item_id=self._id,
                        banner_type="warning",
                        header="Submission canceled",
                        expandable_detail="\n".join(self._log_lines),
                        dismissible=True,
                    ),
                )
            else:
                self._banner.put(
                    self._id,
                    BannerItem(
                        item_id=self._id,
                        banner_type="error",
                        header="Submission failed",
                        expandable_detail="\n".join(self._log_lines),
                        dismissible=True,
                    ),
                )

    def _on_failed(self, error: BaseException) -> None:
        self._banner.remove(self._confirm_id)
        logger.exception(error, exc_info=(type(error), error, error.__traceback__))
        self._banner.put(
            self._id,
            BannerItem(
                item_id=self._id,
                banner_type="error",
                header="Submission error",
                body=str(error),
                expandable_detail="\n".join(self._log_lines),
                dismissible=True,
            ),
        )
