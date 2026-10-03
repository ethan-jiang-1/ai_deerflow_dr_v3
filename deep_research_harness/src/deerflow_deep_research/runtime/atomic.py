"""Shared safe file layer: atomic writes, directory fsync, atomic directory publish.

Pure stdlib, POSIX-only (the repo targets POSIX exactly as v2 did). This module is the
single home for the O_EXCL-temp + os.replace + fsync pattern — stores copy the pattern
by calling it, never by re-implementing it.

@impl RUB-001"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
        with os.fdopen(fd, "wb", closefd=True) as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_name, path)
        temp_name = None
        fsync_dir(path.parent)
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def append_line(path: Path, line: str) -> None:
    """One O_APPEND write: journal entries land whole or fail loudly."""

    path.parent.mkdir(parents=True, exist_ok=True)
    data = line.encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_dir(staging: Path, target: Path) -> None:
    """Atomically publish a fully built staging directory onto its final path.

    The target must not exist; the caller owns cleanup on failure."""

    if target.exists():
        raise FileExistsError(f"target already exists: {target}")
    os.rename(staging, target)
    fsync_dir(target.parent)

