import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_duplicates(root_dir):
    file_dict = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename in file_dict:
                file_dict[filename].append(dirpath)
            else:
                file_dict[filename] = [dirpath]
    duplicates = {k: v for k, v in file_dict.items() if len(v) > 1}
    return duplicates

root_dir = os.path.join(BASE_DIR, 'static')  # Adjust to your static directory
duplicates = find_duplicates(root_dir)

if duplicates:
    print("Duplicate files found:")
    for filename, paths in duplicates.items():
        print(f"{filename}:")
        for path in paths:
            print(f"  - {path}")
else:
    print("No duplicate files found.")
