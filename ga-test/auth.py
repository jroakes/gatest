"""Common flows for obtaining OAuth credentials for Google APIs."""
import pathlib
from typing import List, Union

import google.auth.exceptions
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


class GoogleAuthManager:
    """Manages Google OAuth scopes and credentials and builds the service.

    Attributes:
        scopes:
            A list of scopes required for the authorization. A full list of
            available scopes can be found at:
            https://developers.google.com/identity/protocols/oauth2/scopes
        serialize:
            If True, will serialize the credentials to a JSON file. The save
            location is specified by the `token_path` attribute. Defaults
            to False.
        secrets_path: The path to the client secrets JSON file from Google.
        token_path:
            The path to the existing token details. This doubles as the save
            location for newly serialized credentials.
    """

    def __init__(
        self,
        scopes: List[str],
        serialize: bool = False,
        secrets_path: Union[str, pathlib.Path] = 'credentials/secrets.json',
        token_path: Union[str, pathlib.Path] = 'credentials/token.json',
    ):
        self.scopes = scopes
        self.serialize = serialize
        self.secrets_path = secrets_path
        self.token_path = token_path
        self._credentials = None

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @staticmethod
    def refresh_credentials(credentials: Credentials) -> Credentials:
        """Refreshes a Google Credentials object."""
        request = google.auth.transport.requests.Request()
        return credentials.refresh(request)

    def _run_flow(self) -> Credentials:
        """Runs the InstalledAppFlow to fetch credentials."""
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.secrets_path), self.scopes)
        creds = flow.run_console()
        return creds

    def authorize(self) -> Credentials:
        """Authorizes access to Google and returns credentials.

        Credentials can be serialized to a JSON file and reloaded as needed. A
        refresh will be attempted for expired credentials. If the refresh doesn't
        succeed, the authorization flow will be attempted again.

        Returns:
            A Credentials object that can be used with Google API client libraries.
        """
        try:
            if self._credentials:
                creds = self._credentials
            else:
                # Try to get credentials from file
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path))

            if not creds.valid:
                creds = self.refresh_credentials(creds)
        except (FileNotFoundError, google.auth.exceptions.RefreshError):
            # Run through the OAuth flow and retrieve credentials
            creds = self._run_flow()

        if self.serialize:
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self._credentials = creds
        return creds
