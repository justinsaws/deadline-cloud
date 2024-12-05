# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Provides an object that can be used to track current status of AWS Deadline Cloud 
authentication.

The object emits the following Qt Signals:
   aws_creds_changed: The AWS credentials in ~/.aws changed.
   deadline_config_changed: The AWS Deadline Cloud configuration in ~/.deadline changed.
   creds_source_changed: triggered when credential source changes
   auth_status_changed: triggered when authentication status changes
   api_availability_changed: triggered when api availability changes

The status includes three parts:
  1. Are credentials configured and available for use?
     This is checked with an sts:GetCallerIdentity AWS API call.
  2. Do the credentials grant access to AWS Deadline Cloud APIs?
     This is checked with a simplified deadline:ListFarms AWS API call.
  3. Do the credentials use Deadline Cloud monitor?
     This is checked by looking for the relevant properties
     in the AWS profile configuration.
"""
import os
from configparser import ConfigParser
from logging import getLogger
from typing import Optional

from qtpy.QtCore import QObject, QFileSystemWatcher, Signal, QThread

from .. import api
from ..config import config_file

logger = getLogger(__name__)

_deadline_authentication_status = None


class DeadlineCredentialSourceThread(QThread):

    creds_source_changed = Signal(api.AwsCredentialsSource)

    def __init__(self, config, parent=None):
        super(DeadlineCredentialSourceThread, self).__init__(parent)
        self._config = config

    def run(self):
        creds_source = api.get_credentials_source(config=self._config)
        self.creds_source_changed.emit(creds_source)


class DeadlineAuthenticationStatusThread(QThread):

    auth_status_changed = Signal(api.AwsAuthenticationStatus)

    def __init__(self, config, parent=None):
        super(DeadlineAuthenticationStatusThread, self).__init__(parent)
        self._config = config

    def run(self):
        auth_status = None
        try:
            auth_status = api.check_authentication_status(config=self._config)
        except Exception as e:
            logger.exception(e)
            auth_status = api.AwsAuthenticationStatus.CONFIGURATION_ERROR
        self.auth_status_changed.emit(auth_status)


class DeadlineApiStatusThread(QThread):

    api_availability_changed = Signal(bool)

    def __init__(self, config, parent=None):
        super(DeadlineApiStatusThread, self).__init__(parent)
        self._config = config

    def run(self):
        api_availability = None
        try:
            api_availability = api.check_deadline_api_available(config=self._config)
        except Exception as e:
            logger.exception(e)
            api_availability = False
        self.api_availability_changed.emit(api_availability)


class DeadlineAuthenticationStatus(QObject):
    """
    Holds status information about AWS Deadline Cloud credentials.
    Currently status values are available as properties:

       status.creds_source: result of api.get_credentials_source()
       status.auth_status: result of api.check_authentication_status()
       status.api_availability: result of api.check_deadline_api_available()

    To initialize the status of a non-default AWS Deadline Cloud configuration, pass in
    an AWS Deadline Cloud configuration object to config, call set_config to change it.
    """

    # This signal is sent when an AWS credential changes (e.g. config file)
    aws_creds_changed = Signal()
    # This signal is sent when the AWS Deadline Cloud configuration changes
    deadline_config_changed = Signal()

    # This signal is sent when an AWS authentication type changes
    creds_source_changed = Signal()
    # This signal is sent when an AWS authentication status changes
    auth_status_changed = Signal()
    # This signal is sent when AWS Deadline Cloud API availability changes
    api_availability_changed = Signal()

    @staticmethod
    def getInstance():
        global _deadline_authentication_status
        if _deadline_authentication_status is None:
            _deadline_authentication_status = DeadlineAuthenticationStatus()
        return _deadline_authentication_status

    def __init__(self, parent=None) -> None:
        super(DeadlineAuthenticationStatus, self).__init__(parent)

        self.__creds_source: Optional[api.AwsCredentialsSource] = None
        self.__auth_status: Optional[api.AwsAuthenticationStatus] = None
        self.__api_availability: Optional[bool] = None

        # Load the default config
        self.config = ConfigParser()
        self.config.read_dict(config_file.read_config())

        # Watch the ~/.aws path for any changes to config or credentials, and
        # the ~/.deadline path for any changes to the AWS Deadline Cloud config.
        self.aws_creds_file_watcher = QFileSystemWatcher()
        self.aws_creds_paths = [
            os.path.expanduser(os.path.join("~", ".aws")),
        ]
        self.deadline_config_paths = [
            os.path.expanduser(os.path.join("~", ".deadline")),
        ]
        failed_paths = self.aws_creds_file_watcher.addPaths(
            self.aws_creds_paths + self.deadline_config_paths
        )
        if failed_paths:
            logger.error(
                "Failed to watch these AWS Deadline Cloud configurations: %s", failed_paths
            )
        self.aws_creds_file_watcher.fileChanged.connect(self.files_changed)
        self.aws_creds_file_watcher.directoryChanged.connect(self.files_changed)

        self.refresh_status()

    def set_config(self, config: Optional[ConfigParser]) -> None:
        """
        Changes the AWS Deadline Cloud configuration object used to display authentication
        status.

        Args:
            config (ConfigParser): The AWS Deadline Cloud configuration to use.
        """

        # Refresh the status if any setting that impacts authentication was changed
        if self.config:
            auth_config_changed = False
            for setting_name in [
                "defaults.aws_profile_name",
            ]:
                if config_file.get_setting(setting_name, self.config) != config_file.get_setting(
                    setting_name, config
                ):
                    auth_config_changed = True
        else:
            auth_config_changed = True

        # Make a copy of the config object
        self.config = ConfigParser()
        if config:
            self.config.read_dict(config)
        else:
            self.config.read_dict(config_file.read_config())

        if auth_config_changed:
            self.refresh_status()

    @property
    def creds_source(self) -> Optional[api.AwsCredentialsSource]:
        return self.__creds_source

    @property
    def auth_status(self) -> Optional[api.AwsAuthenticationStatus]:
        return self.__auth_status

    @property
    def api_availability(self) -> Optional[bool]:
        return self.__api_availability

    def _on_creds_source_changed(self, creds_source):
        self.__creds_source = creds_source
        self.creds_source_changed.emit()

    def _on_auth_status_changed(self, auth_status):
        self.__auth_status = auth_status
        self.auth_status_changed.emit()

    def _on_api_availability_changed(self, api_availability):
        self.__api_availability = api_availability
        self.api_availability_changed.emit()

    def files_changed(self, changed_path) -> None:
        # Force the cached boto3 session to refresh, since we don't check the creds
        # file
        if changed_path in self.aws_creds_paths:
            logger.info(f"Path {changed_path} changed, refreshing authentication status")
            self._get_session(changed_path)
        else:
            logger.info(f"Path {changed_path} changed, does not affect authentication status")

    def _get_session(self, changed_path):
        api.get_boto3_session(force_refresh=True)
        self.refresh_status()

        if changed_path in self.aws_creds_paths:
            self.aws_creds_changed.emit()
        elif changed_path in self.deadline_config_paths:
            self.deadline_config_changed.emit()

    def refresh_status(self) -> None:
        """
        Initiates an asynchronous status refresh.
        """
        self.__creds_source_thread = DeadlineCredentialSourceThread(self.config)
        self.__creds_source_thread.creds_source_changed.connect(self._on_creds_source_changed)
        self.__creds_source_thread.start()
        self.__auth_status_thread = DeadlineAuthenticationStatusThread(self.config)
        self.__auth_status_thread.auth_status_changed.connect(self._on_auth_status_changed)
        self.__auth_status_thread.start()
        self.__api_availability_thread = DeadlineApiStatusThread(self.config)
        self.__api_availability_thread.api_availability_changed.connect(
            self._on_api_availability_changed
        )
        self.__api_availability_thread.start()
