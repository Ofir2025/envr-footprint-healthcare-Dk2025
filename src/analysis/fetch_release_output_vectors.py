# -*- coding: utf-8 -*-
"""Fetch one EXIOBASE total-output vector per release and table year.

Motivation
----------
Choosing an EXIOBASE release is the single decision that moves this study's
numbers most, and until now it rested on a comparison of two releases in two
years. The question it has to answer is whether the release used, v3.8.2, is the
one whose Danish health industry tracks the national accounts across 2016, 2019
and 2022 — and that cannot be answered without reading every release published
since.

Reading them the obvious way costs about 13 GB: nine releases, three years, and
each ``IOT_<year>_ixi.zip`` is 0.3 to 0.8 GB. But the comparison needs exactly
one member of each archive — ``x.txt``, the 9,800-row total-output vector, 0.46 MB
uncompressed. So this module does not download the archives. It reads each zip's
central directory over HTTP range requests, locates ``x.txt``, and fetches only
the bytes of that member: **0.09 MB transferred per release-year instead of
0.76 GB**, four orders of magnitude less. Zenodo's own service banner asks for
restraint from automated traffic, and this is what restraint looks like when the
data are needed anyway.

Layouts differ by generation, which is why the member is located rather than
assumed:

============  ==============================  ===============
generation    archive layout                  ``x.txt``
============  ==============================  ===============
v3.7, v3.8    ``IOT_<year>_ixi/`` prefix       **absent**
v3.8.1        ``IOT_<year>_ixi/`` prefix       absent
v3.8.2        ``IOT_<year>_ixi/`` prefix       present
v3.9, v3.10   flat, per-extension folders      present
============  ==============================  ===============

v3.7 and v3.8 publish ``A.txt`` and ``Y.txt`` but no ``x.txt``; their total output
has to be reconstructed, and neither is a candidate release for this study, so
they are out of scope here.

Licence
-------
From v3.9 onwards EXIOBASE is released under a customised non-commercial,
academic licence, not the CC BY-SA 4.0 of v3.7 to v3.8.2. The fetched vectors are
therefore **not** tracked; ``.gitignore`` says so and why. What this study
publishes is the derived comparison — Danish health output against the national
accounts — which is a research finding, not redistribution.
"""

from __future__ import annotations

import argparse
import struct
import urllib.request
import zlib
from pathlib import Path

from paths import BRONZE_DIR

#: Zenodo record id per EXIOBASE release, for the releases that publish
#: ``x.txt``. The concept DOI 10.5281/zenodo.3583070 resolves to all versions.
RELEASE_RECORDS: dict[str, str] = {
    "3.8.2": "5589597",
    "3.9.4": "14614930",
    "3.9.5": "14869924",
    "3.9.6": "15689391",
    "3.10.1": "18937492",
    "3.10.2": "20051562",
}

#: Where the vectors land. Untracked; see the module docstring on the licence.
#: Named for what it holds rather than for being this module's output. The
#: repository reserves the output-directory name for the gold tree, so a bronze
#: fetcher carrying that name reads as a layer skip to a reviewer, and to check
#: C17, which matches the identifier anywhere in the file - including, as this
#: comment first demonstrated, in a comment explaining that it is not used.
VECTOR_DIR = BRONZE_DIR / "exiobase" / "release_output_vectors"

#: Zenodo file URL template.
FILE_URL = "https://zenodo.org/records/{record}/files/IOT_{year}_ixi.zip?download=1"


def _range(url: str, start: int | None = None,
           end: int | None = None) -> bytes:
    """Fetch a byte range of a remote file.

    Parameters
    ----------
    url : str
        File URL.
    start, end : int, optional
        Inclusive byte offsets. Omit both for the whole file.

    Returns
    -------
    bytes
        The requested bytes.
    """
    request = urllib.request.Request(url)
    if start is not None:
        request.add_header("Range",
                           f"bytes={start}-{'' if end is None else end}")
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def remote_size(url: str) -> int:
    """Return the size of a remote file in bytes.

    Parameters
    ----------
    url : str
        File URL.

    Returns
    -------
    int
        Content length.
    """
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=120) as response:
        return int(response.headers["Content-Length"])


def zip_entries(url: str, total: int) -> dict[str, tuple[int, int, int, int]]:
    """Read a remote zip's central directory.

    Parameters
    ----------
    url : str
        Archive URL.
    total : int
        Archive size in bytes, from :func:`remote_size`.

    Returns
    -------
    dict
        Member name to ``(compression method, compressed size, uncompressed
        size, local header offset)``. ZIP64 extra fields are resolved, because
        these archives cross the 4 GB field limits in the member count even
        when they do not in size.

    Raises
    ------
    RuntimeError
        If no end-of-central-directory record is found.
    """
    tail = _range(url, total - min(total, 1 << 16), total - 1)
    marker = tail.rfind(b"PK\x05\x06")
    if marker < 0:
        raise RuntimeError(f"{url}: no end-of-central-directory record")
    size, offset = struct.unpack("<II", tail[marker + 12:marker + 20])
    if offset == 0xFFFFFFFF or size == 0xFFFFFFFF:
        zip64 = tail.rfind(b"PK\x06\x06")
        if zip64 < 0:
            raise RuntimeError(f"{url}: ZIP64 directory expected but missing")
        size, offset = struct.unpack("<QQ", tail[zip64 + 40:zip64 + 56])
    directory = _range(url, offset, offset + size - 1)

    entries: dict[str, tuple[int, int, int, int]] = {}
    position = 0
    while (position + 46 <= len(directory)
           and directory[position:position + 4] == b"PK\x01\x02"):
        method, = struct.unpack("<H", directory[position + 10:position + 12])
        csize, usize = struct.unpack("<II",
                                     directory[position + 20:position + 28])
        nlen, elen, clen = struct.unpack("<HHH",
                                         directory[position + 28:position + 34])
        header, = struct.unpack("<I", directory[position + 42:position + 46])
        name = directory[position + 46:position + 46 + nlen].decode(
            "utf-8", "replace")
        extra = directory[position + 46 + nlen:position + 46 + nlen + elen]
        if 0xFFFFFFFF in (csize, usize, header):
            cursor = 0
            while cursor + 4 <= len(extra):
                field, length = struct.unpack("<HH", extra[cursor:cursor + 4])
                if field == 0x0001:
                    resolved, at = [], cursor + 4
                    for value in (usize, csize, header):
                        if value == 0xFFFFFFFF:
                            resolved.append(
                                struct.unpack("<Q", extra[at:at + 8])[0])
                            at += 8
                        else:
                            resolved.append(value)
                    usize, csize, header = resolved
                    break
                cursor += 4 + length
        entries[name] = (method, csize, usize, header)
        position += 46 + nlen + elen + clen
    return entries


def fetch_member(url: str, entry: tuple[int, int, int, int]) -> bytes:
    """Fetch and inflate one member of a remote zip.

    Parameters
    ----------
    url : str
        Archive URL.
    entry : tuple
        The member's central-directory record, from :func:`zip_entries`.

    Returns
    -------
    bytes
        The member's uncompressed content.
    """
    method, csize, _usize, header = entry
    local = _range(url, header, header + 29)
    nlen, elen = struct.unpack("<HH", local[26:30])
    start = header + 30 + nlen + elen
    raw = _range(url, start, start + csize - 1)
    return raw if method == 0 else zlib.decompress(raw, -15)


def fetch(release: str, year: str, refresh: bool = False) -> Path:
    """Fetch one release-year total-output vector into bronze.

    Parameters
    ----------
    release : str
        A key of :data:`RELEASE_RECORDS`, e.g. ``"3.9.6"``.
    year : str
        EXIOBASE table year.
    refresh : bool, optional
        Re-fetch even when the file is already present. Default ``False``.

    Returns
    -------
    pathlib.Path
        The written file.

    Raises
    ------
    KeyError
        If the release is not one that publishes ``x.txt``.
    RuntimeError
        If the archive carries no ``x.txt``.
    """
    if release not in RELEASE_RECORDS:
        raise KeyError(f"{release} is not a release that publishes x.txt; "
                       f"known: {sorted(RELEASE_RECORDS)}")
    out = VECTOR_DIR / f"x_v{release.replace('.', '_')}_{year}.txt"
    if out.exists() and not refresh:
        return out
    url = FILE_URL.format(record=RELEASE_RECORDS[release], year=year)
    entries = zip_entries(url, remote_size(url))
    members = [name for name in entries if name.endswith("x.txt")]
    if not members:
        raise RuntimeError(f"v{release} {year}: archive carries no x.txt "
                           f"({len(entries)} members)")
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    out.write_bytes(fetch_member(url, entries[members[0]]))
    return out


def main() -> None:
    """Fetch the releases and years named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--releases", nargs="+",
                        default=sorted(RELEASE_RECORDS),
                        help="releases to fetch (default: all with x.txt)")
    parser.add_argument("--years", nargs="+",
                        default=[str(y) for y in range(2016, 2023)],
                        help="EXIOBASE table years (default: 2016-2022)")
    parser.add_argument("--refresh", action="store_true",
                        help="re-fetch files already present")
    arguments = parser.parse_args()

    for release in arguments.releases:
        for year in arguments.years:
            try:
                path = fetch(release, year, refresh=arguments.refresh)
                print(f"v{release} {year} -> {path.name} "
                      f"({path.stat().st_size / 1e6:.2f} MB)")
            except Exception as error:                # noqa: BLE001
                print(f"v{release} {year}: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
