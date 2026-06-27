"""
Project-wide constants for lastfm-client.

All tuneable values and fixed identifiers used across the package are
defined here so they have a single source of truth.
"""

from .exceptions import (
    AuthenticationError,
    InvalidParametersError,
    InvalidRequestError,
    RateLimitError,
    ServiceError,
    SuspendedError,
)

# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

#: Base URL of the Last.fm Web API.
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

#: Default HTTP request timeout in seconds.
DEFAULT_TIMEOUT = 30

#: HTTP status codes that are treated as successful responses.
#: Last.fm returns API-level errors as JSON within a 200 OK body, so only
#: 200 is whitelisted here.
THROUGH_STATUS = frozenset({200})

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

#: Response format requested from the API.
DEFAULT_FORMAT = "json"

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

#: Default number of results returned per page.
DEFAULT_LIMIT = 30

#: Maximum number of results allowed per page.
MAX_LIMIT = 1000

#: Default page number.
DEFAULT_PAGE = 1

#: Maximum page number.
MAX_PAGE = 1000

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

#: Name of the environment variable used to supply the Last.fm API key.
ENV_API_KEY = "LASTFM_API_KEY"

# ---------------------------------------------------------------------------
# API error mapping
# ---------------------------------------------------------------------------

#: Maps Last.fm API error codes to dedicated exception classes.
#: Codes not present here are raised as the generic ``APIError``.
#:
#: Reference: https://www.last.fm/api/errorcodes
API_ERROR_MAP = {
    2:  InvalidRequestError,
    3:  InvalidRequestError,
    4:  AuthenticationError,
    5:  InvalidRequestError,
    6:  InvalidParametersError,
    7:  InvalidRequestError,
    8:  ServiceError,
    9:  AuthenticationError,
    10: AuthenticationError,
    11: ServiceError,
    13: InvalidRequestError,
    16: ServiceError,
    26: SuspendedError,
    29: RateLimitError,
}