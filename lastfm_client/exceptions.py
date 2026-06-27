"""
Exception hierarchy for lastfm-client.

All exceptions inherit from ``LastFMClientError``, so callers can catch
every library error with a single ``except`` clause when fine-grained
handling is not required.

Hierarchy::

    LastFMClientError
    ├── UsageError
    ├── ClientError
    │   ├── HTTPError
    │   └── APIError
    │       ├── AuthenticationError
    │       ├── RateLimitError
    │       ├── InvalidRequestError
    │       ├── InvalidParametersError
    │       ├── ServiceError
    │       └── SuspendedError
    └── ResponseError
"""


class LastFMClientError(Exception):
    """Base exception for all lastfm-client errors."""


# ---------------------------------------------------------------------------
# Usage errors
# ---------------------------------------------------------------------------

class UsageError(LastFMClientError):
    """
    Raised when the library is called with invalid arguments or configuration.

    This exception is raised before any network request is made.

    Examples include:

    * missing or empty API key
    * non-string parameter where a string is required
    * pagination values outside the allowed range
    """


# ---------------------------------------------------------------------------
# Network / API errors
# ---------------------------------------------------------------------------

class ClientError(LastFMClientError):
    """
    Raised when communication with the Last.fm API fails.

    This is the base class for all network and API-level errors.
    Catch this class to handle any failure that occurs after a request
    has been attempted.
    """


class HTTPError(ClientError):
    """
    Raised when the server returns an unexpected HTTP status code.

    Parameters
    ----------
    status_code : int
        The HTTP status code returned by the server.
    message : str
        The HTTP reason phrase (e.g. ``"Not Found"``).

    Attributes
    ----------
    status_code : int
        The HTTP status code returned by the server.
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)


class APIError(ClientError):
    """
    Raised when the Last.fm API returns an error code.

    Last.fm signals API-level errors as JSON within an HTTP 200 response.
    Known error codes are mapped to dedicated subclasses; unknown codes
    are raised as this class directly.

    Parameters
    ----------
    code : int
        Last.fm API error code.
    message : str
        Error description returned by the API.

    Attributes
    ----------
    code : int
        Last.fm API error code.
    """

    def __init__(self, code: int, message: str):
        self.code = code
        super().__init__(message)


class AuthenticationError(APIError):
    """
    Raised when authentication fails or the session/key is invalid.

    Corresponds to Last.fm API error codes 4, 9, and 10.
    """


class InvalidRequestError(APIError):
    """
    Raised when the request is malformed or unsupported.

    Covers invalid service, method, format, resource, or signature.
    Corresponds to Last.fm API error codes 2, 3, 5, 7, and 13.
    """


class InvalidParametersError(APIError):
    """
    Raised when a required parameter is missing or invalid.

    Corresponds to Last.fm API error code 6.
    """


class ServiceError(APIError):
    """
    Raised when the Last.fm service is temporarily unavailable.

    Corresponds to Last.fm API error codes 8, 11, and 16.
    """


class SuspendedError(APIError):
    """
    Raised when the API key has been suspended.

    Corresponds to Last.fm API error code 26.
    """


class RateLimitError(APIError):
    """
    Raised when the request rate limit has been exceeded.

    Corresponds to Last.fm API error code 29.
    """


# ---------------------------------------------------------------------------
# Response errors
# ---------------------------------------------------------------------------

class ResponseError(LastFMClientError):
    """
    Raised when the server returns a response that cannot be parsed.

    Examples include:

    * response body is not valid JSON
    * decoded JSON is not a ``dict``
    """