# lastfm-client

[日本語版 README はこちら](README_JP.md)

A lightweight Python client for the Last.fm Web API.

`lastfm-client` is a minimal wrapper around the Last.fm REST API, designed for data collection and research rather than object-oriented API access.

Unlike libraries such as `pylast`, this project intentionally performs **no response parsing or data modeling**. Every API call simply returns the decoded JSON response (`dict`), allowing users to freely process, analyze, or store the data.

---

## Features

* Lightweight and dependency-minimal
* Thin wrapper over the Last.fm Web API
* Returns raw JSON as Python `dict`
* Simple and predictable API
* Built-in request and error handling
* Environment variable support for API keys

---

## Supported API Methods

### Artist

* `artist.getInfo`
* `artist.search`

### Album

* `album.getInfo`
* `album.search`

### Track

* `track.getInfo`
* `track.search`

Only these six endpoints are intentionally supported.

---

## Installation

```bash
pip install requests
```

Clone this repository and add the project root to your Python path, or place `lastfm_client/` alongside your script.

---

## Authentication

Create a Last.fm API account and obtain an API key at https://www.last.fm/api/account/create.

The client looks for the API key in the following order:

1. Explicitly passed to the constructor
2. Environment variable `LASTFM_API_KEY`

```python
from lastfm_client import LastFMClient

# From environment variable LASTFM_API_KEY
client = LastFMClient()

# Or pass directly
client = LastFMClient(api_key="your_api_key_here")
```

If neither is available, a `UsageError` is raised during initialization.

---

## Usage

### Track

```python
# Get detailed info for a track
track = client.track_get_info(
    artist="Deep Purple",
    track="Smoke on the Water",
)
print(track["track"]["name"])          # "Smoke on the Water"
print(track["track"]["listeners"])     # "1234567"
print(track["track"]["duration"])      # "312000" (milliseconds)

# Search for tracks by name
results = client.track_search(track="Smoke on the Water", limit=5)
for item in results["results"]["trackmatches"]["track"]:
    print(item["name"], "-", item["artist"])
```

### Artist

```python
# Get detailed info for an artist
artist = client.artist_get_info("Deep Purple")
print(artist["artist"]["name"])        # "Deep Purple"
print(artist["artist"]["stats"]["listeners"])

# List top tags
for tag in artist["artist"]["tags"]["tag"]:
    print(tag["name"])

# Search for artists by name
results = client.artist_search(artist="Deep Purple", limit=5)
for item in results["results"]["artistmatches"]["artist"]:
    print(item["name"])
```

### Album

```python
# Get detailed info for an album
album = client.album_get_info(
    artist="Deep Purple",
    album="Machine Head",
)
print(album["album"]["name"])          # "Machine Head"
print(album["album"]["tracks"]["track"][0]["name"])  # First track title

# Search for albums by name
results = client.album_search(album="Machine Head", limit=5)
for item in results["results"]["albummatches"]["album"]:
    print(item["name"], "-", item["artist"])
```

### Pagination

`artist_search`, `album_search`, and `track_search` all support `limit` and `page` parameters.

```python
# First page
page1 = client.track_search(track="yesterday", limit=10, page=1)

# Second page
page2 = client.track_search(track="yesterday", limit=10, page=2)
```

---

## Returned Value

Every public method returns the decoded API response as a Python `dict`. No additional parsing, conversion, or validation of the response content is performed.

```python
data = client.track_get_info(artist="Deep Purple", track="Smoke on the Water")
# data is a plain dict — access fields directly
print(data["track"]["listeners"])
```

The exact structure of each response follows the [Last.fm API documentation](https://www.last.fm/api).

---

## Error Handling

All exceptions inherit from `LastFMClientError`.

```
LastFMClientError
├── UsageError
├── ClientError
│   ├── HTTPError
│   └── APIError
│       ├── AuthenticationError
│       ├── RateLimitError
│       └── NotFoundError
└── ResponseError
```

### UsageError

Raised when invalid arguments or configuration are supplied — before any network request is made.

```python
from lastfm_client.exceptions import UsageError

try:
    client = LastFMClient()           # No API key set
except UsageError as e:
    print(e)  # "API key not provided. ..."

try:
    client.artist_get_info("")        # Empty string
except UsageError as e:
    print(e)  # "'artist' must not be empty."

try:
    client.track_search("love", limit=0)  # Invalid limit
except UsageError as e:
    print(e)  # "'limit' must be greater than or equal to 1."
```

### ClientError

Raised when communication with the Last.fm API fails.

```python
from lastfm_client.exceptions import ClientError, HTTPError

try:
    data = client.artist_get_info("Deep Purple")
except HTTPError as e:
    print(e.status_code, e)           # e.g. 503 "Service Unavailable"
except ClientError as e:
    print(e)                          # Network error, timeout, etc.
```

### APIError

Raised when the Last.fm API returns an error code. Known codes are mapped to dedicated subclasses.

```python
from lastfm_client.exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError

try:
    data = client.artist_get_info("Deep Purple")
except AuthenticationError as e:
    print(f"[{e.code}] Invalid API key")
except NotFoundError as e:
    print(f"[{e.code}] Artist not found")
except RateLimitError as e:
    print(f"[{e.code}] Rate limit exceeded")
except APIError as e:
    print(f"[{e.code}] API error: {e}")
```

### ResponseError

Raised when the server returns a response that cannot be parsed.

```python
from lastfm_client.exceptions import ResponseError

try:
    data = client.artist_get_info("Deep Purple")
except ResponseError as e:
    print(e)                          # "Response is not valid JSON."
```

### Catching all errors

```python
from lastfm_client.exceptions import LastFMClientError

try:
    data = client.track_get_info(artist="Deep Purple", track="Smoke on the Water")
except LastFMClientError as e:
    print(f"Request failed: {e}")
```

---

## API Error Code Mapping

Known Last.fm API error codes are automatically mapped to dedicated exception classes.

| API Code | Exception             |
| -------: | --------------------- |
|        4 | `AuthenticationError` |
|        6 | `NotFoundError`       |
|       29 | `RateLimitError`      |

Unknown API errors are raised as `APIError`. The mapping is maintained in `constants.py`.

---

## Project Structure

```
lastfm_client/
├── __init__.py
├── client.py
├── constants.py
└── exceptions.py
```

### client.py

Provides the public API. All public methods validate their arguments and delegate to the internal `_request()` method, which handles networking and passes the response to `_handle_response()` for validation.

### constants.py

Stores project-wide constants: API endpoint, default timeout, pagination limits, environment variable names, and API error code mappings.

### exceptions.py

Defines the custom exception hierarchy used throughout the project.

---

## Design Philosophy

Every public method simply prepares parameters and delegates to a common request handler.

```
track_get_info()
track_search()

artist_get_info()
artist_search()

album_get_info()
album_search()

        │
        ▼

    _request()

        │
        ▼

 requests.get()

        │
        ▼

_handle_response()
  ├── _handle_http_error()
  ├── response.json()
  └── _handle_api_error()

        │
        ▼

      dict
```

---

## Scope

This project intentionally **does not** provide:

* object models or dataclasses
* response flattening or transformation
* pandas integration
* caching or retry logic
* asynchronous requests
* rate limit management

Its sole responsibility is:

> **Last.fm REST API → Python `dict`**

Everything else is left to the application.

---

## Intended Use Cases

* metadata collection
* music information retrieval (MIR)
* research projects and dataset construction
* exploratory analysis
* scripting

---

## Development Principles

This project aims to remain lightweight, dependency-minimal, predictable, and easy to maintain. New features will only be added if they preserve the project's simplicity.

---

## License

MIT License.

---

## Disclaimer

- This project was developed with the assistance of AI tools (ChatGPT and Claude).
- Developed and tested on Python 3.12.10. Compatibility with other versions is not guaranteed.
- This is a personal project and is not actively maintained. Issues and pull requests may not be addressed promptly, if at all.