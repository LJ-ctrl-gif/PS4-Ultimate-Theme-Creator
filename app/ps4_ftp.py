"""Read-only, private-LAN GoldHEN FTP directory browsing."""
from __future__ import annotations

import ftplib
import ipaddress
import posixpath

MEDIA_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".dds",
    ".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".opus",
    ".wma", ".at9", ".vag", ".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".gif", ".apng", ".wmv", ".flv",
}


def validate_target(host: str, port: int, path: str) -> tuple[str, int, str]:
    try:
        address = ipaddress.ip_address(host.strip())
    except ValueError as exc:
        raise ValueError("Enter the PS4's numeric IP address.") from exc
    if address.version != 4 or not address.is_private or address.is_loopback or address.is_link_local:
        raise ValueError("FTP browsing is limited to a private IPv4 LAN address.")
    if port != 2121:
        raise ValueError("GoldHEN FTP uses port 2121.")
    normalized = posixpath.normpath("/" + str(path or "/").lstrip("/"))
    if any(ord(char) < 32 or ord(char) == 127 for char in str(path)) or any(part == ".." for part in str(path).split("/")):
        raise ValueError("Invalid PS4 folder path.")
    return str(address), port, normalized


def list_media(host: str, port: int = 2121, path: str = "/", timeout: float = 4.0) -> dict:
    host, port, path = validate_target(host, port, path)
    ftp = ftplib.FTP()
    try:
        ftp.connect(host, port, timeout=timeout)
        ftp.login()
        ftp.cwd(path)
        names = ftp.nlst()
        entries = []
        for raw in names[:200]:
            name = raw.rstrip("/").split("/")[-1]
            if not name or name in {".", ".."} or any(c in name for c in "\\r\\n\\x00"):
                continue
            is_dir = False
            try:
                ftp.cwd(posixpath.join(path, name))
                ftp.cwd(path)
                is_dir = True
            except ftplib.all_errors:
                try:
                    ftp.cwd(path)
                except ftplib.all_errors:
                    pass
            ext = posixpath.splitext(name)[1].lower()
            if is_dir or ext in MEDIA_EXTENSIONS:
                entries.append({"name": name, "path": posixpath.join(path, name), "directory": is_dir, "media": ext in MEDIA_EXTENSIONS})
        return {"host": host, "port": port, "path": path, "entries": entries, "read_only": True}
    except ftplib.all_errors as exc:
        raise ValueError("Could not browse GoldHEN FTP. Check the PS4 IP, port 2121, and that FTP is enabled.") from exc
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


def download_media(host: str, port: int, path: str, max_bytes: int = 512 * 1024 * 1024) -> tuple[str, bytes]:
    """Download one whitelisted media file from the private PS4 FTP server."""
    host, port, normalized = validate_target(host, port, path)
    name = posixpath.basename(normalized)
    if not name or name in {".", ".."} or posixpath.dirname(normalized) == normalized:
        raise ValueError("Choose a media file, not a folder.")
    if posixpath.splitext(name)[1].lower() not in MEDIA_EXTENSIONS:
        raise ValueError("That file type is not supported.")
    ftp = ftplib.FTP()
    chunks: list[bytes] = []
    total = 0
    try:
        ftp.connect(host, port, timeout=8.0)
        ftp.login()
        def receive(block: bytes) -> None:
            nonlocal total
            total += len(block)
            if total > max_bytes:
                raise ValueError("The selected file exceeds the 512 MB import limit.")
            chunks.append(block)
        ftp.retrbinary(f"RETR {normalized}", receive, blocksize=64 * 1024)
        if not total:
            raise ValueError("The selected file is empty.")
        return name, b"".join(chunks)
    except ValueError:
        raise
    except ftplib.all_errors as exc:
        raise ValueError("Could not download that file from GoldHEN FTP. Check its path and FTP connection.") from exc
    finally:
        try:
            ftp.quit()
        except Exception:
            pass
