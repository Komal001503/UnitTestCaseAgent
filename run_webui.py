"""Launcher for the local Flask web UI."""

from __future__ import annotations

import runpy


if __name__ == "__main__":
    runpy.run_module("webui.app", run_name="__main__")
