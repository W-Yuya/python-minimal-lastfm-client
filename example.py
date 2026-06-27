"""
Example usage of lastfm-client.

Demonstrates all six supported API methods and basic error handling.

Setup
-----
Obtain a Last.fm API key at https://www.last.fm/api/account/create and
expose it as an environment variable before running this script.

Linux / macOS::

    export LASTFM_API_KEY="your_api_key_here"

Windows (PowerShell)::

    $env:LASTFM_API_KEY="your_api_key_here"

Run::

    python example.py
"""

from lastfm_client import LastFMClient
from lastfm_client.exceptions import (
    AuthenticationError,
    LastFMClientError,
    InvalidRequestError,
    InvalidParametersError,
    ServiceError,
    SuspendedError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIVIDER = "-" * 40


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------

def example_track_get_info(client: LastFMClient) -> None:
    section("track.getInfo")

    data = client.track_get_info(
        artist="Deep Purple",
        track="Smoke on the Water",
    )

    track = data["track"]
    print(f"Track    : {track['name']}")
    print(f"Artist   : {track['artist']['name']}")
    print(f"Album    : {track['album']['title']}")
    print(f"Duration : {int(track['duration']) // 1000}s")
    print(f"Listeners: {track['listeners']}")
    print(f"Tags     : {', '.join(t['name'] for t in track['toptags']['tag'][:3])}")


def example_artist_get_info(client: LastFMClient) -> None:
    section("artist.getInfo")

    data = client.artist_get_info("Deep Purple")

    artist = data["artist"]
    print(f"Artist   : {artist['name']}")
    print(f"Listeners: {artist['stats']['listeners']}")
    print(f"Tags     : {', '.join(t['name'] for t in artist['tags']['tag'][:3])}")


def example_album_get_info(client: LastFMClient) -> None:
    section("album.getInfo")

    data = client.album_get_info(
        artist="Deep Purple",
        album="Machine Head",
    )

    album = data["album"]
    tracks = album["tracks"]["track"]
    print(f"Album    : {album['name']}")
    print(f"Artist   : {album['artist']}")
    print(f"Listeners: {album['listeners']}")
    print(f"Tracks   :")
    for track in tracks:
        print(f"  {track['@attr']['rank']}. {track['name']}")


def example_track_search(client: LastFMClient) -> None:
    section("track.search")

    data = client.track_search(track="Smoke on the Water", limit=3)

    matches = data["results"]["trackmatches"]["track"]
    print(f"Query    : 'Smoke on the Water'")
    print(f"Results  :")
    for item in matches:
        print(f"  {item['name']} — {item['artist']}")


def example_artist_search(client: LastFMClient) -> None:
    section("artist.search")

    data = client.artist_search(artist="Deep Purple", limit=3)

    matches = data["results"]["artistmatches"]["artist"]
    print(f"Query    : 'Deep Purple'")
    print(f"Results  :")
    for item in matches:
        print(f"  {item['name']} (listeners: {item['listeners']})")


def example_album_search(client: LastFMClient) -> None:
    section("album.search")

    data = client.album_search(album="Machine Head", limit=3)

    matches = data["results"]["albummatches"]["album"]
    print(f"Query    : 'Machine Head'")
    print(f"Results  :")
    for item in matches:
        print(f"  {item['name']} — {item['artist']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        client = LastFMClient()

        example_track_get_info(client)
        example_artist_get_info(client)
        example_album_get_info(client)
        example_track_search(client)
        example_artist_search(client)
        example_album_search(client)

    except AuthenticationError:
        print("Authentication failed. Check that LASTFM_API_KEY is correct.")
    except RateLimitError:
        print("Rate limit exceeded. Wait a moment and try again.")
    except InvalidRequestError:
        print("Invalid request. Please check your parameters.")
    except InvalidParametersError:
        print("Invalid parameters. Please check your input.")
    except ServiceError:
        print("Last.fm service is temporarily unavailable.")
    except SuspendedError:
        print("Your API key has been suspended.")
    except LastFMClientError as e:
        print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()