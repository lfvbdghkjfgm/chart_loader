from __future__ import annotations

import os

from .config import (
    clear_default_directory,
    get_default_directory,
    get_last_icao,
    set_default_directory,
)
from .logging_setup import get_logger
from .service import chart_file_path, update_chart, download_chart, validate_icao

logger = get_logger()


def choose_act(acts: list[str], input_fn=input, print_fn=print) -> str | None:
    print_fn("Выберите действие:")
    for num, act in enumerate(acts, 1):
        print_fn(f"{num} - {act}")
    choice = input_fn(f"Выберите вариант 1-{len(acts)}: ").strip()
    if choice not in [str(i) for i in range(1, len(acts) + 1)]:
        print_fn("Такого варианта нет")
        return None
    return choice


def prompt_icao(last_icao: str, input_fn=input, print_fn=print) -> str | None:
    while True:
        if last_icao:
            print_fn(f"Последний ICAO: {last_icao}")
            value = input_fn(
                "Введите ICAO (4 буквы), 1 - использовать последний, Enter - отмена: "
            ).strip()
            if value == "1":
                return last_icao
        else:
            value = input_fn("Введите ICAO (4 буквы, Enter - отмена): ").strip()

        if not value:
            return None

        normalized = validate_icao(value)
        if normalized:
            return normalized
        print_fn("Неправильный формат ICAO. Используйте 4 латинские буквы.")


def prompt_directory(default_directory: str, input_fn=input, print_fn=print) -> str | None:
    while True:
        if default_directory:
            print_fn(f"Директория по умолчанию: {default_directory}")
        choice = input_fn(
            "Введите директорию для сохранения, Enter - текущая, 1 - по умолчанию, 0 - отмена\n - "
        ).strip()

        if choice == "0":
            return None
        if choice == "":
            return os.getcwd()
        if choice == "1":
            if default_directory and os.path.isdir(default_directory):
                return default_directory
            print_fn("Директория по умолчанию не задана или недоступна.")
            continue

        if os.path.isdir(choice):
            remember = input_fn(
                "Сделать эту директорию директорией по умолчанию? 1 - да, любой символ - нет: "
            ).strip()
            if remember == "1":
                set_default_directory(choice)
                print_fn("Директория сохранена как директория по умолчанию.")
            return choice

        print_fn("Такой директории нет.")


def settings_menu(input_fn=input, print_fn=print) -> None:
    while True:
        print_fn("\nНастройки:")
        default_dir = get_default_directory()
        print_fn(f"Текущая директория по умолчанию: {default_dir or 'не задана'}")
        acts = [
            "установить директорию по умолчанию",
            "очистить директорию по умолчанию",
            "назад",
        ]
        choice = choose_act(acts, input_fn=input_fn, print_fn=print_fn)
        if not choice:
            continue
        if choice == "1":
            new_dir = input_fn("Введите путь к директории (0 - отмена): ").strip()
            if new_dir == "0":
                continue
            if os.path.isdir(new_dir):
                set_default_directory(new_dir)
                logger.info("Default directory updated: %s", new_dir)
                print_fn("Директория по умолчанию обновлена.")
            else:
                print_fn("Такой директории нет.")
        elif choice == "2":
            clear_default_directory()
            logger.info("Default directory cleared")
            print_fn("Директория по умолчанию очищена.")
        elif choice == "3":
            return


def _confirm_overwrite(file_exists: bool, input_fn=input, print_fn=print) -> bool:
    if not file_exists:
        return True
    overwrite = input_fn(
        "Файл для этого ICAO уже существует. Перезаписать? 1 - да, любой символ - нет: "
    ).strip()
    if overwrite != "1":
        print_fn("Операция отменена.")
        return False
    return True


def _run_chart_action(update_mode: bool, input_fn=input, print_fn=print) -> None:
    default_dir = get_default_directory()
    last_icao = get_last_icao()
    icao = prompt_icao(last_icao, input_fn=input_fn, print_fn=print_fn)
    if not icao:
        return

    target_dir = prompt_directory(default_dir, input_fn=input_fn, print_fn=print_fn)
    if not target_dir:
        return

    try:
        target_file = chart_file_path(icao, target_dir)
        file_exists = target_file.exists()
    except ValueError:
        print_fn("Неправильный формат ICAO.")
        return

    if not _confirm_overwrite(file_exists=file_exists, input_fn=input_fn, print_fn=print_fn):
        return

    if update_mode:
        success, message = update_chart(icao=icao, directory=target_dir)
    else:
        success, message = download_chart(icao=icao, directory=target_dir)

    if success:
        logger.info("Action completed update=%s icao=%s directory=%s", update_mode, icao, target_dir)
    else:
        logger.warning(
            "Action failed update=%s icao=%s directory=%s message=%s",
            update_mode,
            icao,
            target_dir,
            message,
        )
    print_fn(message)


def run(input_fn=input, print_fn=print) -> None:
    logger.info("Application started")
    while True:
        print_fn("\n=== Chart Loader ===")
        default_dir = get_default_directory()
        last_icao = get_last_icao()
        print_fn(f"Директория по умолчанию: {default_dir or 'не задана'}")
        print_fn(f"Последний ICAO: {last_icao or 'не задан'}")

        acts = [
            "загрузить чарты",
            "обновить чарты",
            "настройки",
            "выйти из приложения",
        ]
        choice = choose_act(acts, input_fn=input_fn, print_fn=print_fn)
        if not choice:
            continue
        if choice == "1":
            _run_chart_action(update_mode=False, input_fn=input_fn, print_fn=print_fn)
        elif choice == "2":
            _run_chart_action(update_mode=True, input_fn=input_fn, print_fn=print_fn)
        elif choice == "3":
            settings_menu(input_fn=input_fn, print_fn=print_fn)
        elif choice == "4":
            break

    logger.info("Application finished")
    print_fn("Благодарю за использование данного загрузчика")

