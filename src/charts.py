"""Compatibility layer for old imports."""

from __future__ import annotations

import os

from chart_loader.app import run
from chart_loader.config import (
    clear_default_directory,
    get_default_directory,
    set_default_directory,
)
from chart_loader.service import (
    check_dir,
    download_chart,
    update_chart,
)


def delete_file(filename: str, directory: str = "."):
    try:
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
        return 1
    except Exception as exc:
        return exc


def saved_directory(act: str, directory: str = ""):
    if act == "w" and directory:
        set_default_directory(directory)
        return True
    if act == "r":
        return get_default_directory() or False
    if act == "c":
        clear_default_directory()
        return True
    return False


def check_file_exists(filename, directory):
    return os.path.exists(os.path.join(directory, filename))


def chart(port: str, directory="."):
    success, message = download_chart(port, directory=directory)
    if success:
        return message, None
    if message == "чарты уже скачаны":
        return message, 1
    return "ошибка", message


def charts_main():
    run()
    return False


def update(port: str, directory="."):
    return update_chart(port, directory=directory)
