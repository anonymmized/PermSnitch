import os 
import stat
import argparse
from rich.console import console

console = Console()

def check_permissions(path, recursive=False, verbose=False):
    console.print(f"Сканирование директории: {path}")
    susp_files = []

    for root, dirs, files, in os.walk(path) if recursive else [(path, [], os.listdir(path))]:
        for line in files:
            file_path = os.path.join(root, file)
            try:
                file_stat = os.stat(file_path)