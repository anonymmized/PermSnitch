import os
import csv
import stat
import time
import argparse
from pwd import getpwuid
from rich.console import Console
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ATTENTION_COLOR = "#DC143C"
MAIN_COLOR = "#EE82EE"

console = Console()

def show_ascii():
    art = r"""
       ___                ____     _ __      __ 
      / _ \___ ______ _  / __/__  (_) /_____/ / 
     / ___/ -_) __/  ' \_\ \/ _ \/ / __/ __/ _ \
    /_/   \__/_/ /_/_/_/___/_//_/_/\__/\__/_//_/
                                            
    """
    return art

def find_uid(uid_num):
    try:
        user_info = getpwuid(int(uid_num))
        return user_info.pw_name
    except KeyError:
        return "Unknown"

def check_permissions(path, recursive=False, verbose=False, fix=False, suid_scan=False, interactive=False):
    count_error = 0
    count_log = 0
    count_conf = 0
    suid_count = 0
    world_writable_count = 0
    fixed_count = 0 
    console.print(f"Directory scanning: {path}", style=f"bold italic {MAIN_COLOR}")
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

                if suid_scan and mode & stat.S_ISUID:
                    is_suspicious = True 
                    suid_count += 1
                    console.print(f"Found SUID file: {file_path} (perms: {oct(mode & 0o7777)[2:]}) - Potential privilege escalation risk!", style=f"bold italic {ATTENTION_COLOR}")

                if is_suspicious:
                    suspicious_files.append((file_path, permissions, owner))
                    console.print(f"Found a file with unsafe rights: {file_path} ({permissions})", style=f"bold italic {ATTENTION_COLOR}")
                    if file_path.endswith('.log'):
                        count_log += 1
                    if file_path.endswith('.conf'):
                        count_conf += 1
                    if mode & stat.S_IWOTH or permissions == '777':
                        world_writable_count += 1
                    if interactive and not fix:
                        while True:
                            console.print("Fix (y/n): ", style=f"bold italic {MAIN_COLOR}", end="")
                            interactive_ans = input().lower()
                            if interactive_ans == "y":
                                new_mode = 0o644 if os.path.isfile(file_path) else 0o755
                                os.chmod(file_path, new_mode)
                                fixed_count += 1
                                console.print(f"Successfully fixed rights for {file_path}: {permissions} -> {oct(new_mode)[2:].zfill(3)}", style=f"bold italic {MAIN_COLOR}")
                                break
                            elif interactive_ans == "n":
                                break
                            else:
                                console.print("Invalid input. Please enter 'y' or 'n'", style=f"bold italic {ATTENTION_COLOR}")
                    if fix:
                        new_mode = 0o644 if os.path.isfile(file_path) else 0o755
                        os.chmod(file_path, new_mode)
                        console.print(f"Fixed rights for {file_path}: {permissions} -> {oct(new_mode)[2:].zfill(3)}", style=f"bold italic {MAIN_COLOR}")
                    if verbose:
                        console.print(f"Owner: {owner}, Recommendation: Use 'chmod 644' or 'chmod 600'", style=f"bold italic {MAIN_COLOR}")
                else:
                    if verbose:
                        console.print(f"File: {file_path} ({permissions}) - OK", style=f"bold italic {MAIN_COLOR}")

            except Exception as e:
                count_error += 1

        if not recursive:
            break

    return suspicious_files, count_error, count_log, count_conf, suid_count, world_writable_count, fixed_count

class PermSnitchHandler(FileSystemEventHandler):
    def __init__(self, console):
        self.console = console
    def on_modified(self, event):
        if not event.is_directory:
            try: 
                file_stat = os.stat(event.src_path)
                mode = file_stat.st_mode
                permissions = oct(mode & 0o777)[2:].zfill(3)
                is_suspicious = (mode & stat.S_IWOTH) or permissions == "777"
                if mode & stat.S_ISUID:
                    is_suspicious = True
                    self.console.print(f"New SUID detected: {event.src_path} (perms: {oct(mode & 0o7777)[2:]}) - Potential privilege escalation risk!", style=f"bold italic {ATTENTION_COLOR}")
                if is_suspicious:
                    self.console.print(f"New unsafe rights detected: {event.src_path} (perms: {permissions})", style=f"bold italic {ATTENTION_COLOR}")
            except Exception as e:
                self.console.print(f"Error monitoring {event.src_path}: {e}", style=f"bold italic {ATTENTION_COLOR}")
    def on_created(self, event):
        if not event.is_directory:
            try:
                file_stat = os.stat(event.src_path)
                mode = file_stat.st_mode
                permissions = oct(mode & 0o777)[2:].zfill(3)
                if mode & stat.S_ISUID or (mode & stat.S_IWOTH) or permissions == '777':
                    self.console.print(
                        f"[red]New file with unsafe rights: {event.src_path} (perms: {oct(mode & 0o7777)[2:] if mode & stat.S_ISUID else permissions})[/red]"
                    )
            except Exception as e:
                self.console.print(f"Error monitoring {event.src_path}: {e}", style=f"bold italic {ATTENTION_COLOR}")


def start_monitor(path, console):
    event_handler = PermSnitchHandler(console)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    console.print(f"Monitoring {path}...", style=f"bold italic {MAIN_COLOR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    parser = argparse.ArgumentParser(description="Script for checking the rights to files.")
    parser.add_argument("path", help="The path to the directory for verification")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive scanning")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detailed conclusion")
    parser.add_argument("--fix", action="store_true", help="Automatically correct unsafe rights")
    parser.add_argument("-csv", help="Save report to file (CSV)")
    parser.add_argument("-json", help="Save report to file (JSON)")
    parser.add_argument("--conf", action="store_true", help="Finding suspicious configuration files")
    parser.add_argument("--logs", action="store_true", help="Finding suspicious log files")
    parser.add_argument("--suid", action="store_true", help="Enable SUID scanning")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode for fixing permissions")
    parser.add_argument("--monitoring", action="store_true", help="Monitoring of the selected directory")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        console.print(f"Error: the specified path is not a directory or does not exist", style=f"bold italic {ATTENTION_COLOR}")
        return

    if args.monitoring:
        start_monitor(args.path, console)
    else:
        suspicious_files, errors, cnt_logs, cnt_conf, cnt_suid, cnt_writable, cnt_fixed = check_permissions(args.path, args.recursive, args.verbose, args.fix, args.suid, args.interactive)

        console.print(f"\nThe final report:", style=f"bold italic {MAIN_COLOR}")
        if suspicious_files:
            console.print(f"Found {len(suspicious_files)} Files with unsafe rights:", style=f"bold italic {MAIN_COLOR}")
            for file_path, permissions, owner in suspicious_files:
                console.print(f"- {file_path} (rights: {permissions}, owner: {owner})", style=f"bold italic {ATTENTION_COLOR}")
        else:
            console.print(f"Unsafe files were not found", style=f"bold italic {MAIN_COLOR}")
        if args.conf:
            console.print(f"The number of suspicious conf-files: {cnt_conf}", style=f"bold italic {MAIN_COLOR}")
        if args.logs:
            console.print(f"The number of suspicious log-files: {cnt_logs}", style=f"bold italic {MAIN_COLOR}")
        if cnt_fixed and args.interactive:
            console.print(f"The number of fixed files: {cnt_fixed}", style=f"bold italic {MAIN_COLOR}")
        console.print(f"The number of errors: {errors}", style=f"bold italic {ATTENTION_COLOR}")
        console.print(f"SUID risks: {cnt_suid}", style=f"bold italic {ATTENTION_COLOR}")
        console.print(f"Word-writable: {cnt_writable}", style=f"bold italic {ATTENTION_COLOR}")

        if args.csv and suspicious_files:
            try:
                with open(args.csv, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Path", "Permissions", "Owner"])
                    for file_path, permissions, owner in suspicious_files:
                        writer.writerow([file_path, permissions, owner])
                console.print(f"The report is saved in {args.csv}", style=f"bold italic {MAIN_COLOR}")
            except Exception as e:
                console.print(f"Error saving CSV report: {e}", style=f"bold italic {MAIN_COLOR}")
        
        if args.json and suspicious_files:
            import json
            report = [{"path": file_path, "permissions": permissions, "owner": owner} for file_path, permissions, owner in suspicious_files]
            try:
                with open(args.json, 'w', encoding="utf-8") as file:
                    json.dump(report, file, indent=4, ensure_ascii=False)
                console.print(f"The report is saved in {args.json}", style=f"bold italic {MAIN_COLOR}")
            except Exception as e:
                console.print(f"Error saving JSON report: {e}", style=f"bold italic {MAIN_COLOR}")
if __name__ == "__main__":
    art = show_ascii()
    console.print(art, style="bold italic green")
    main()


