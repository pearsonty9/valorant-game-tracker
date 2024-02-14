import os
from pathlib import Path
from datetime import datetime

def get_file_paths(source_directory):
    file_paths = []
    with os.scandir(source_directory) as cwd:
        for entry in cwd:
            if not entry.name.startswith('.') and entry.is_file():
                file_paths.append(Path(entry.path))
    return file_paths

def group_files_by_created_date(file_paths):
    sorted_files_by_date = {}
    for entry in file_paths:
        created_at = get_created_by_date(entry)
        file_creation_timestamp = f"{created_at.date().year}-{created_at.date().month}-{created_at.date().day}"
        if file_creation_timestamp in sorted_files_by_date.keys(): 
            sorted_files_by_date[file_creation_timestamp].append(entry)
        else:
            sorted_files_by_date[file_creation_timestamp] = [entry]
    return sorted_files_by_date

def sort_files_into_folders(source_directory, folder_structure):
    for directory, files in folder_structure.items():
        for file_path in files:
            file_name = file_path.parts[-1]
            dest_path = f"{source_directory}\\{directory}"
            if os.path.isfile(file_path):
                if not os.path.exists(dest_path) :
                    Path(dest_path).mkdir(exist_ok=True)
                os.rename(file_path, f"{dest_path}\\{file_name}")

def get_created_by_date(file_path):
    file_birthtime = os.stat(file_path).st_birthtime
    created_at = datetime.fromtimestamp(file_birthtime)
    return created_at