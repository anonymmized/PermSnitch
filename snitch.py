#!/usr/bin/env python3
import os
import stat
import argparse
from colorama import init, Fore

# Инициализация colorama для цветного вывода
init()

def check_permissions(path, recursive=False, verbose=False):
    """Проверка прав доступа к файлам в указанной директории."""
    print(f"{Fore.CYAN}Сканирование директории: {path}{Fore.RESET}")
    suspicious_files = []

    # Рекурсивное сканирование или только текущая директория
    for root, dirs, files in os.walk(path) if recursive else [(path, [], os.listdir(path))]:
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Получение информации о файле
                file_stat = os.stat(file_path)
                mode = file_stat.st_mode
                owner = file_stat.st_uid

                # Права в восьмеричной системе
                permissions = oct(mode & 0o777)[2:].zfill(3)  # Например, '777'

                # Проверка на небезопасные права (например, доступ на запись для всех)
                is_suspicious = (mode & stat.S_IWOTH) or permissions == '777'

                if is_suspicious:
                    suspicious_files.append((file_path, permissions, owner))
                    print(f"{Fore.RED}Обнаружен файл с небезопасными правами: {file_path} ({permissions}){Fore.RESET}")
                    if verbose:
                        print(f"  Владелец: {owner}, Рекомендация: Используйте 'chmod 644' или 'chmod 600'")
                else:
                    if verbose:
                        print(f"{Fore.GREEN}Файл: {file_path} ({permissions}) - OK{Fore.RESET}")

            except Exception as e:
                print(f"{Fore.YELLOW}Ошибка при проверке {file_path}: {e}{Fore.RESET}")

        if not recursive:
            break

    return suspicious_files

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Скрипт для проверки прав доступа к файлам.")
    parser.add_argument("path", help="Путь к директории для проверки")
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивное сканирование")
    parser.add_argument("-v", "--verbose", action="store_true", help="Подробный вывод")
    args = parser.parse_args()

    # Проверка существования директории
    if not os.path.isdir(args.path):
        print(f"{Fore.RED}Ошибка: Указанный путь не является директорией или не существует{Fore.RESET}")
        return

    # Запуск проверки
    suspicious_files = check_permissions(args.path, args.recursive, args.verbose)

    # Итоговый отчёт
    print(f"\n{Fore.CYAN}Итоговый отчёт:{Fore.RESET}")
    if suspicious_files:
        print(f"Найдено {len(suspicious_files)} файлов с небезопасными правами:")
        for file_path, permissions, owner in suspicious_files:
            print(f"- {file_path} (права: {permissions}, владелец: {owner})")
    else:
        print(f"{Fore.GREEN}Небезопасные файлы не найдены{Fore.RESET}")

if __name__ == "__main__":
    main()