import os
import csv
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

def check_permissions(path, recursive=False, verbose=False, fix=False):
    count_error = 0
    count_log = 0
    console.print(f"Directory scanning: {path}")
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
                    console.print(f"Found a file with unsafe rights: {file_path} ({permissions})")
                    if is_suspicious.endswith('.log'):
                        count_log += 1
                    if fix:
                        new_mode = 0o644 if os.path.isfile(file_path) else 0o755
                    os.chmod(file_path, new_mode)
                    console.print(f"Fixed rights for {file_path}: {permissions} -> {oct(new_mode)[2:].zfill(3)}")
                    if verbose:
                        console.print(f"Owner: {owner}, Recommendation: Use 'chmod 644' or 'chmod 600'")
                else:
                    if verbose:
                        console.print(f"File: {file_path} ({permissions}) - OK")

            except Exception as e:
                count_error += 1

        if not recursive:
            break

    return suspicious_files, count_error

def main():
    parser = argparse.ArgumentParser(description="Script for checking the rights to files.")
    parser.add_argument("path", help="The path to the directory for verification")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive scanning")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detailed conclusion")
    parser.add_argument("--fix", action="store_true", help="Automatically correct unsafe rights")
    parser.add_argument("-csv", help="Save report to file (CSV)")
    parser.add_argument("-json", help="Save report to file (JSON)")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        console.print(f"Error: the specified path is not a directory or does not exist")
        return

    suspicious_files, errors = check_permissions(args.path, args.recursive, args.verbose, args.fix)

    console.print(f"\nThe final report:")
    if suspicious_files:
        console.print(f"Found {len(suspicious_files)} Files with unsafe rights:")
        for file_path, permissions, owner in suspicious_files:
            console.print(f"- {file_path} (rights: {permissions}, owner: {owner})")
    else:
        console.print(f"Unsafe files were not found")
    console.print(f"The number of errors: {errors}")

    if args.csv and suspicious_files:
        try:
            with open(args.csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Path", "Permissions", "Owner"])
                for file_path, permissions, owner in suspicious_files:
                    writer.writerow([file_path, permissions, owner])
            console.print(f"The report is saved in {args.csv}")
        except Exception as e:
            console.print(f"Error saving CSV report: {e}")
    
    if args.json and suspicious_files:
        report = [{"path": file_path, "permissions": permissions, "owner": owner} for file_path, permissions, owner in suspicious_files]
        try:
            with open(args.json, 'w', encoding="utf-8") as file:
                json.dump(report, file, indent=4, ensure_ascii=False)
            console.print(f"The report is saved in {args.json}")
        except Exception as e:
            console.print(f"Error saving JSON report: {e}")
if __name__ == "__main__":
    main()