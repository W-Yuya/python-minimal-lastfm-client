import os

import requests
from requests import Response

from .constants import (
    BASE_URL,
    DEFAULT_FORMAT,
    DEFAULT_TIMEOUT,
    ENV_API_KEY,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    DEFAULT_PAGE,
    MAX_PAGE,
    THROUGH_STATUS,
    API_ERROR_MAP,
)

from .exceptions import (
    APIError,
    ClientError,
    HTTPError,
    ResponseError,
    UsageError,
)


class LastFMClient:
    """
    Lightweight client for the Last.fm Web API.

    Wraps six Last.fm endpoints (artist, album, and track getInfo / search)
    and returns each response as a plain Python ``dict``.  No response
    parsing or data modelling is performed; that responsibility belongs to
    the caller.

    Parameters
    ----------
    api_key : str or None, optional
        Last.fm API key.  If omitted, the value of the ``LASTFM_API_KEY``
        environment variable is used instead.
    timeout : int, optional
        HTTP request timeout in seconds.  Defaults to ``DEFAULT_TIMEOUT``.

    Raises
    ------
    UsageError
        If no API key is found in either the argument or the environment.

    Examples
    --------
    >>> client = LastFMClient()                        # uses LASTFM_API_KEY
    >>> client = LastFMClient(api_key="your_key_here")
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or os.getenv(ENV_API_KEY)

        if not self.api_key:
            raise UsageError(
                "API key not provided. "
                "Pass api_key or set LASTFM_API_KEY."
            )

        self.timeout = timeout

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def artist_get_info(self, artist: str, mbid: str|None = None) -> dict:
        """
        Fetch metadata for an artist.

        Calls ``artist.getInfo`` and returns the raw API response.

        Parameters
        ----------
        artist : str
            Artist name.
        mbid : str or None, optional
            MusicBrainz ID for the artist.  
            If provided, this will be used instead of the artist name.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If ``artist`` is not a non-empty string.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> data = client.artist_get_info("Deep Purple")
        >>> data["artist"]["name"]
        'Deep Purple'
        """
        if mbid is not None:
            self._validate_string(mbid, "mbid")

            return self._request(
                "artist.getInfo",
                mbid=mbid,
            )
        else:
            self._validate_string(artist, "artist")

            return self._request(
                "artist.getInfo",
                artist=artist,
            )

    def artist_search(
        self,
        artist: str,
        limit: int = DEFAULT_LIMIT,
        page: int = DEFAULT_PAGE,
    ) -> dict:
        """
        Search for artists by name.

        Calls ``artist.search`` and returns the raw API response.

        Parameters
        ----------
        artist : str
            Artist name to search for.
        limit : int, optional
            Number of results per page.  Must be between 1 and ``MAX_LIMIT``.
            Defaults to ``DEFAULT_LIMIT``.
        page : int, optional
            Page number to fetch.  Must be between 1 and ``MAX_PAGE``.
            Defaults to ``DEFAULT_PAGE``.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If any argument fails validation.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> results = client.artist_search("Deep Purple", limit=5)
        >>> for item in results["results"]["artistmatches"]["artist"]:
        ...     print(item["name"])
        """
        self._validate_string(artist, "artist")
        self._validate_positive_int(limit, "limit", max_value=MAX_LIMIT)
        self._validate_positive_int(page, "page", max_value=MAX_PAGE)

        return self._request(
            "artist.search",
            artist=artist,
            limit=limit,
            page=page,
        )

    def album_get_info(self, artist: str, album: str, mbid: str|None = None) -> dict:
        """
        Fetch metadata for an album.

        Calls ``album.getInfo`` and returns the raw API response.

        Parameters
        ----------
        artist : str
            Artist name.
        album : str
            Album title.
        mbid : str or None, optional
            MusicBrainz ID for the album.
            If provided, this will be used instead of the artist and album names.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If either argument is not a non-empty string.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> data = client.album_get_info("Deep Purple", "Machine Head")
        >>> data["album"]["name"]
        'Machine Head'
        """

        if mbid is not None:
            self._validate_string(mbid, "mbid")

            return self._request(
                "album.getInfo",
                mbid=mbid,
            )
        else:
            self._validate_string(artist, "artist")
            self._validate_string(album, "album")

            return self._request(
                "album.getInfo",
                artist=artist,
                album=album,
            )

    def album_search(
        self,
        album: str,
        limit: int = DEFAULT_LIMIT,
        page: int = DEFAULT_PAGE,
    ) -> dict:
        """
        Search for albums by title.

        Calls ``album.search`` and returns the raw API response.

        Parameters
        ----------
        album : str
            Album title to search for.
        limit : int, optional
            Number of results per page.  Must be between 1 and ``MAX_LIMIT``.
            Defaults to ``DEFAULT_LIMIT``.
        page : int, optional
            Page number to fetch.  Must be between 1 and ``MAX_PAGE``.
            Defaults to ``DEFAULT_PAGE``.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If any argument fails validation.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> results = client.album_search("Machine Head", limit=5)
        >>> for item in results["results"]["albummatches"]["album"]:
        ...     print(item["name"], "-", item["artist"])
        """
        self._validate_string(album, "album")
        self._validate_positive_int(limit, "limit", max_value=MAX_LIMIT)
        self._validate_positive_int(page, "page", max_value=MAX_PAGE)

        return self._request(
            "album.search",
            album=album,
            limit=limit,
            page=page,
        )

    def track_get_info(self, artist: str, track: str, mbid: str | None = None) -> dict:
        """
        Fetch metadata for a track.

        Calls ``track.getInfo`` and returns the raw API response.

        Parameters
        ----------
        artist : str
            Artist name.
        track : str
            Track title.
        mbid : str | None, optional
            Track MBID.
            If provided, this will be used instead of the artist and track names.
        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If either argument is not a non-empty string.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> data = client.track_get_info("Deep Purple", "Smoke on the Water")
        >>> data["track"]["listeners"]
        '1234567'
        """
        if mbid is not None:
            self._validate_string(mbid, "mbid")

            return self._request(
                "track.getInfo",
                mbid=mbid,
            )
        else:
            self._validate_string(artist, "artist")
            self._validate_string(track, "track")

            return self._request(
                "track.getInfo",
                artist=artist,
                track=track,
            )

    def track_search(
        self,
        track: str,
        artist: str | None = None,
        limit: int = DEFAULT_LIMIT,
        page: int = DEFAULT_PAGE,
    ) -> dict:
        """
        Search for tracks by title.

        Calls ``track.search`` and returns the raw API response.

        Parameters
        ----------
        track : str
            Track title to search for.
        artist : str | None, optional
            Artist name to filter by.
        limit : int, optional
            Number of results per page.  Must be between 1 and ``MAX_LIMIT``.
            Defaults to ``DEFAULT_LIMIT``.
        page : int, optional
            Page number to fetch.  Must be between 1 and ``MAX_PAGE``.
            Defaults to ``DEFAULT_PAGE``.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        UsageError
            If any argument fails validation.
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.

        Examples
        --------
        >>> results = client.track_search("Smoke on the Water", limit=5)
        >>> for item in results["results"]["trackmatches"]["track"]:
        ...     print(item["name"], "-", item["artist"])
        """
        self._validate_string(track, "track")
        if artist is not None:
            self._validate_string(artist, "artist")
        self._validate_positive_int(limit, "limit", max_value=MAX_LIMIT)
        self._validate_positive_int(page, "page", max_value=MAX_PAGE)

        if artist is not None:
            return self._request(
                "track.search",
                track=track,
                artist=artist,
                limit=limit,
                page=page,
            )
        
        return self._request(
            "track.search",
            track=track,
            limit=limit,
            page=page,
        )

    # ---------------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------------

    def _request(self, method: str, **params) -> dict:
        """
        Send a GET request to the Last.fm Web API.

        Builds the query string from ``method``, the instance API key, and any
        additional keyword arguments, then delegates response validation to
        ``_handle_response``.

        Parameters
        ----------
        method : str
            Last.fm API method name (e.g. ``"track.getInfo"``).
        **params
            API-specific query parameters forwarded verbatim.

        Returns
        -------
        dict
            Decoded JSON response.

        Raises
        ------
        ClientError
            If the request fails due to a network error or timeout.
        HTTPError
            If the server returns an unexpected HTTP status code.
        APIError
            If the Last.fm API returns an error code.
        ResponseError
            If the response cannot be parsed as JSON.
        """
        query = {
            "method": method,
            "api_key": self.api_key,
            "format": DEFAULT_FORMAT,
            **params,
        }

        try:
            response = requests.get(
                BASE_URL,
                params=query,
                timeout=self.timeout,
            )

        except requests.Timeout as e:
            raise ClientError("Request timed out.") from e

        except requests.ConnectionError as e:
            raise ClientError("Failed to connect to Last.fm.") from e

        except requests.RequestException as e:
            raise ClientError(str(e)) from e

        return self._handle_response(response)

    def _handle_response(self, response: Response) -> dict:
        """
        Validate and decode an HTTP response from the Last.fm API.

        Runs HTTP status validation, JSON decoding, and Last.fm API error
        checking in sequence.

        Parameters
        ----------
        response : requests.Response
            Raw response object returned by ``requests.get``.

        Returns
        -------
        dict
            Decoded JSON payload.

        Raises
        ------
        HTTPError
            If the HTTP status code is not acceptable.
        ResponseError
            If the body is not valid JSON or not a ``dict``.
        APIError
            If the decoded payload contains a Last.fm API error.
        """
        self._handle_http_error(response)

        try:
            payload = response.json()

        except ValueError as e:
            raise ResponseError("Response is not valid JSON.") from e

        if not isinstance(payload, dict):
            raise ResponseError("Unexpected response type.")

        self._handle_api_error(payload)

        return payload

    def _handle_http_error(self, response: Response) -> None:
        """
        Raise ``HTTPError`` if the HTTP status code is not acceptable.

        Parameters
        ----------
        response : requests.Response
            Raw response object to inspect.

        Raises
        ------
        HTTPError
            If ``response.status_code`` is not in ``THROUGH_STATUS``.
        """
        if response.status_code in THROUGH_STATUS:
            return

        raise HTTPError(
            status_code=response.status_code,
            message=response.reason,
        )

    def _handle_api_error(self, payload: dict) -> None:
        """
        Raise an ``APIError`` subclass if the payload contains an error code.

        Known Last.fm error codes are mapped to dedicated exception classes via
        ``API_ERROR_MAP``; unknown codes fall back to ``APIError``.

        Parameters
        ----------
        payload : dict
            Decoded JSON payload to inspect.

        Raises
        ------
        APIError
            If ``payload`` contains an ``"error"`` key.
        """
        if "error" not in payload:
            return

        code = payload.get("error")
        message = payload.get("message", "Unknown API error.")
        exc = API_ERROR_MAP.get(code, APIError)

        raise exc(
            code=code,
            message=message,
        )

    def _validate_string(self, value: str, name: str) -> None:
        """
        Raise ``UsageError`` if ``value`` is not a non-empty string.

        Parameters
        ----------
        value : str
            Parameter value to validate.
        name : str
            Parameter name used in the error message.

        Raises
        ------
        UsageError
            If ``value`` is not a ``str``, or is blank after stripping.
        """
        if not isinstance(value, str):
            raise UsageError(f"'{name}' must be a string.")

        if not value.strip():
            raise UsageError(f"'{name}' must not be empty.")

    def _validate_positive_int(
        self,
        value: int,
        name: str,
        max_value: int | None = None,
    ) -> None:
        """
        Raise ``UsageError`` if ``value`` is not a positive integer within bounds.

        Parameters
        ----------
        value : int
            Parameter value to validate.
        name : str
            Parameter name used in the error message.
        max_value : int or None, optional
            Upper bound (inclusive).  If ``None``, no upper bound is enforced.

        Raises
        ------
        UsageError
            If ``value`` is not an ``int``, is less than 1, or exceeds
            ``max_value``.
        """
        if not isinstance(value, int):
            raise UsageError(f"'{name}' must be an integer.")

        if value < 1:
            raise UsageError(
                f"'{name}' must be greater than or equal to 1."
            )

        if max_value is not None and value > max_value:
            raise UsageError(
                f"'{name}' must be less than or equal to {max_value}."
            )