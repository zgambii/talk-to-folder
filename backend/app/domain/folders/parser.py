from urllib.parse import ParseResult, parse_qs, urlparse


class InvalidDriveFolderUrlError(ValueError):
    """Raised when a URL is not a valid Google Drive folder URL."""


def parse_google_drive_folder_url(folder_url: str) -> str:
    stripped_url = folder_url.strip()
    if not stripped_url:
        raise InvalidDriveFolderUrlError("Google Drive folder URL is required.")

    parsed_url = _parse_url(stripped_url)
    if parsed_url.netloc.lower() != "drive.google.com":
        raise InvalidDriveFolderUrlError("Enter a valid Google Drive folder URL.")

    folder_id = _folder_id_from_path(parsed_url.path)
    if folder_id is not None:
        return folder_id

    folder_id = _folder_id_from_open_query(parsed_url.path, parsed_url.query)
    if folder_id is not None:
        return folder_id

    raise InvalidDriveFolderUrlError("Enter a valid Google Drive folder URL.")


def _parse_url(folder_url: str) -> ParseResult:
    if "://" not in folder_url:
        folder_url = f"https://{folder_url}"

    parsed_url = urlparse(folder_url)
    if parsed_url.scheme not in {"http", "https"}:
        raise InvalidDriveFolderUrlError("Enter a valid Google Drive folder URL.")

    return parsed_url


def _folder_id_from_path(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]

    # Example: /drive/folders/<folder_id>
    if len(parts) == 3 and parts[:2] == ["drive", "folders"]:
        return parts[2]

    # Example: /drive/u/<account_index>/folders/<folder_id>
    if len(parts) == 5 and parts[:2] == ["drive", "u"] and parts[3] == "folders":
        return parts[4]

    return None


def _folder_id_from_open_query(path: str, query: str) -> str | None:
    if path != "/open":
        return None

    # /open?id=<id> can point to either files or folders. The Drive API will
    # verify the resource type later, after authentication is implemented.
    folder_ids = parse_qs(query).get("id", [])
    if not folder_ids or not folder_ids[0]:
        return None

    return folder_ids[0]
