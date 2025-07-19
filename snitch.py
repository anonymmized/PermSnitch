import os
import stat
import argparse
import subprocess
from pwd import getpwuid
from rich.console import Console

console = Console()

def find_uid(uid_num):
    try:
        user_info = getpwuid(int(uid_num))
        return user_info.pw_name
    except KeyError:
        return "Unknown"

def check_permissions(path, recursive=False, verbose=False):
    console.print(f"Сканирование директории: {path}")
    suspicious_files = []

    for root, dirs, files in os.walk(path) if recursive else [(path, [], os.listdir(path))]:
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_stat = os.stat(file_path)
                mode = file_stat.st_mode
                owner_num = str(file_stat.st_uid)
                owner = find_uid(owner_num)
                
                permissions = oct(mode & 0o777)[2:].zfill(3)

                is_suspicious = (mode & stat.S_IWOTH) or permissions == '777'

                if is_suspicious:
                    suspicious_files.append((file_path, permissions, owner))
                    console.print(f"Обнаружен файл с небезопасными правами: {file_path} ({permissions})")
                    if verbose:
                        console.print(f"  Владелец: {owner}, Рекомендация: Используйте 'chmod 644' или 'chmod 600'")
                else:
                    if verbose:
                        console.print(f"Файл: {file_path} ({permissions}) - OK")

            except Exception as e:
                console.print(f"Ошибка при проверке {file_path}: {e}")

        if not recursive:
            break

    return suspicious_files

def main():
    parser = argparse.ArgumentParser(description="Скрипт для проверки прав доступа к файлам.")
    parser.add_argument("path", help="Путь к директории для проверки")
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивное сканирование")
    parser.add_argument("-v", "--verbose", action="store_true", help="Подробный вывод")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        console.print(f"Ошибка: Указанный путь не является директорией или не существует")
        return

    suspicious_files = check_permissions(args.path, args.recursive, args.verbose)

    console.print(f"\nИтоговый отчёт:")
    if suspicious_files:
        console.print(f"Найдено {len(suspicious_files)} файлов с небезопасными правами:")
        for file_path, permissions, owner in suspicious_files:
            console.print(f"- {file_path} (права: {permissions}, владелец: {owner})")
    else:
        console.print(f"Небезопасные файлы не найдены")

if __name__ == "__main__":
    main()