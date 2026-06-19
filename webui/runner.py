"""Subprocess runner + shared activity log buffer."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
import subprocess
import threading
import traceback


@dataclass(frozen=True)
class LogEntry:
    seq: int
    ts: str
    label: str
    message: str


class LogBuffer:
    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._seq = 0
        self._lock = threading.Lock()

    def append(self, label: str, message: str) -> int:
        with self._lock:
            self._seq += 1
            entry = LogEntry(
                seq=self._seq,
                ts=datetime.now(timezone.utc).isoformat(),
                label=label,
                message=message.rstrip("\n"),
            )
            self._entries.append(entry)
            return entry.seq

    def tail(self, since: int = 0) -> list[dict[str, object]]:
        with self._lock:
            return [
                {"seq": e.seq, "ts": e.ts, "label": e.label, "message": e.message}
                for e in self._entries
                if e.seq > since
            ]

    def current_seq(self) -> int:
        with self._lock:
            return self._seq

    def last_lines(self, count: int = 50) -> list[str]:
        with self._lock:
            return [f"[{e.label}] {e.message}" for e in list(self._entries)[-count:]]


LOG_BUFFER = LogBuffer()


def run_script(argv: list[str], *, cwd, env, label: str) -> tuple[int, list[str]]:
    """Run a subprocess, stream output into the shared log buffer, and return code + tail."""
    if not argv or any(not isinstance(arg, str) or "\x00" in arg for arg in argv):
        LOG_BUFFER.append(label, "Invalid command arguments")
        return 1, LOG_BUFFER.last_lines(50)

    LOG_BUFFER.append(label, f"$ {' '.join(argv)}")
    try:
        proc = subprocess.Popen(
            argv,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            LOG_BUFFER.append(label, line.rstrip("\n"))
        proc.wait()
        LOG_BUFFER.append(label, f"exit={proc.returncode}")
        return proc.returncode, LOG_BUFFER.last_lines(50)
    except Exception:
        LOG_BUFFER.append(label, traceback.format_exc())
        return 1, LOG_BUFFER.last_lines(50)
