from cx_Freeze import setup, Executable
import sys
import os

sys.setrecursionlimit(1500)  # Increase if necessary

# Define the packages you need
packages = ["os", "pandas", "PySide6"]

# Include additional files (like data files, images, etc.)
include_files = [
    r"C:\Users\134\Documents\Python Scripts\query_LLM.py",
    r"C:\Users\134\Documents\Python Scripts\llama_parse_module.py",
    r"C:\Users\134\Documents\Python Scripts\llama_index_multiple_files.py",
    (r"C:\Users\134\Documents\Python Scripts\paths.json", "paths.json")  # (source, destination)
]

# Automatically include all imported modules from the scripts
def get_modules_from_file(file_path):
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # If UTF-8 fails, try with cp1251
        with open(file_path, 'r', encoding='cp1251') as file:
            content = file.read()
    return [line.split()[1] for line in content.split('\n') if line.startswith('import') or line.startswith('from')]

for file in include_files:
    if isinstance(file, tuple):
        file_path = file[0]
    else:
        file_path = file
    if os.path.isfile(file_path):
        try:
            packages.extend(get_modules_from_file(file_path))
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")

# Remove duplicates and system modules
packages = list(set(packages) - set(sys.builtin_module_names))

# Set options for cx_Freeze
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "include_msvcr": True,  # Include Microsoft Visual C++ runtime
}

# Specify the icon file
icon_file = r"C:\Users\134\Documents\Python Scripts\target-with-an-arrow-page-1.ico"

# Setup configuration
setup(
    name="YourApp",
    version="0.1",
    description="Your application description",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        r"C:\Users\134\Documents\Python Scripts\GUI_table.py",
        base="Win32GUI",
        icon=icon_file,
        target_name="RAG_manager.exe"
    )]
)