"""
lastfm-client
=============

A lightweight Python client for the Last.fm Web API.

Every public method returns the decoded JSON response as a plain Python
``dict``.  No response parsing or data modelling is performed.

Basic usage::

    from lastfm_client import LastFMClient

    client = LastFMClient()                    # reads LASTFM_API_KEY from env
    data   = client.track_get_info("Deep Purple", "Smoke on the Water")
    print(data["track"]["listeners"])
"""

from .client import LastFMClient

__all__ = [
    "LastFMClient",
]