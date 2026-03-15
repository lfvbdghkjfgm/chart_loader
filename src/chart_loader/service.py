from __future__ import annotations

import os
import re
from pathlib import Path

from .config import set_last_icao
from .logging_setup import get_logger
from .network import ChartDownloadError, fetch_chart_pdf

logger = get_logger()
ICAO_PATTERN = re.compile(r"^[A-Z]{4}$")


def validate_icao(value: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().upper()
    if not cleaned:
        return None
    if ICAO_PATTERN.fullmatch(cleaned):
        return cleaned
    return None


def chart_file_path(icao: str, directory: str) -> Path:
    normalized = validate_icao(icao)
    if not normalized:
        raise ValueError("Invalid ICAO code")
    return Path(directory) / f"{normalized}.pdf"


def check_dir(directory: str) -> bool:
    return os.path.isdir(directory)


def delete_file(file_path: Path) -> tuple[bool, str]:
    try:
        file_path.unlink()
        logger.info("File deleted: %s", file_path)
        return True, "файл удален"
    except FileNotFoundError:
        logger.warning("Delete skipped, file not found: %s", file_path)
        return False, "файл не найден"
    except OSError as exc:
        logger.error("Delete failed for %s: %s", file_path, exc)
        return False, f"Не удалось удалить файл: {exc}"


def download_chart(icao: str, directory: str = ".", overwrite: bool = False) -> tuple[bool, str]:
    normalized = validate_icao(icao)
    if not normalized:
        return False, "Неправильный формат ICAO. Используйте 4 латинские буквы."

    target_dir = Path(directory)
    if not target_dir.is_dir():
        return False, "Указанная директория не существует."

    target_file = target_dir / f"{normalized}.pdf"
    if target_file.exists() and not overwrite:
        logger.info("Chart already exists, overwrite disabled: %s", target_file)
        return False, "чарты уже скачаны"

    if target_file.exists() and overwrite:
        deleted, msg = delete_file(target_file)
        if not deleted:
            return False, msg

    try:
        pdf_bytes = fetch_chart_pdf(normalized)
    except ChartDownloadError as exc:
        logger.error("Download failed for ICAO=%s: %s", normalized, exc)
        return False, str(exc)

    try:
        target_file.write_bytes(pdf_bytes)
    except OSError as exc:
        logger.error("Failed to write file %s: %s", target_file, exc)
        return False, f"Ошибка записи файла: {exc}"

    set_last_icao(normalized)
    logger.info("Chart downloaded ICAO=%s path=%s", normalized, target_file)
    return True, f"чарты успешно скачаны: {target_file}"


def update_chart(icao: str, directory: str = ".") -> tuple[bool, str]:
    logger.info("Update requested ICAO=%s directory=%s", icao, directory)
    return download_chart(icao=icao, directory=directory, overwrite=True)

