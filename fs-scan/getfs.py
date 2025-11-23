import os
import sys
import json

def print_structure(startpath, indent="", last=True, ignored_dirs=None, ignored_files=None, excluded_dirs=None):
    """Recursively print the directory structure in tree format."""
    if ignored_dirs is None:
        ignored_dirs = {'.git', 'venv', '.venv', '__pycache__'}
    if ignored_files is None:
        ignored_files = {'README', 'README.md'}
    if excluded_dirs is None:
        excluded_dirs = {'node_modules'}
        
    basename = os.path.basename(startpath) or os.path.abspath(startpath)
    if last:
        print(indent + "└── " + basename)
        indent += "    "
    else:
        print(indent + "├── " + basename)
        indent += "│   "

    try:
        items = sorted(os.listdir(startpath), key=lambda x: x.lower())
    except PermissionError:
        print(indent + "└── [Permission Denied]")
        return

    total_items = len(items)
    for index, item in enumerate(items):
        path = os.path.join(startpath, item)
        is_last = index == total_items - 1

        # Skip completely ignored directories
        if os.path.isdir(path) and item in ignored_dirs:
            continue
            
        # Skip ignored files
        if os.path.isfile(path) and item in ignored_files:
            continue

        # Handle excluded directories (show them but don't recurse)
        if os.path.isdir(path) and item in excluded_dirs:
            print(indent + ("└── " if is_last else "├── ") + item + " [excluded]")
            continue

        if os.path.isdir(path):
            print_structure(path, indent, is_last, ignored_dirs, ignored_files, excluded_dirs)
        else:
            print(indent + ("└── " if is_last else "├── ") + item)


def build_json_structure(startpath, ignored_dirs=None, ignored_files=None, excluded_dirs=None):
    """Recursively build a JSON-serializable dict of the directory structure."""
    if ignored_dirs is None:
        ignored_dirs = {'.git', 'venv', '.venv', '__pycache__'}
    if ignored_files is None:
        ignored_files = {'README', 'README.md'}
    if excluded_dirs is None:
        excluded_dirs = {'node_modules'}

    structure = {}
    try:
        items = sorted(os.listdir(startpath), key=lambda x: x.lower())
    except PermissionError:
        return "[Permission Denied]"

    for item in items:
        path = os.path.join(startpath, item)
        if os.path.isdir(path):
            # Skip completely ignored directories
            if item in ignored_dirs:
                continue
            # Mark excluded directories but don't recurse
            if item in excluded_dirs:
                structure[item] = "[excluded]"
                continue
            structure[item] = build_json_structure(path, ignored_dirs, ignored_files, excluded_dirs)
        elif os.path.isfile(path):
            if item in ignored_files:
                continue
            structure[item] = None  # Files are leaves
    return structure


def main():
    if len(sys.argv) > 1:
        directory_name = sys.argv[1]
        directory = os.path.abspath(directory_name)
    else:
        print("Please provide a directory name.")
        sys.exit(1)

    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        sys.exit(1)

    # Print visual tree
    print_structure(directory)

    # Ask user if they want JSON output
    try:
        choice = input("\nWould you like to see this structure in JSON format? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        sys.exit(0)

    if choice in ('y', 'yes'):
        json_structure = {os.path.basename(directory) or directory: build_json_structure(directory)}
        print("\nJSON Structure:\n")
        print(json.dumps(json_structure, indent=4))
    else:
        print("JSON output skipped.")


if __name__ == "__main__":
    main()

# {
#     "blog": {
#         ".gitignore": null,
#         "__init__.py": null,
#         "blog.db": null,
#         "database.py": null,
#         "main.py": null,
#         "models.py": null,
#         "repository": {
#             "blog.py": null,
#             "user.py": null
#         },
#         "requirements.txt": null,
#         "routers": {
#             "__init__.py": null,
#             "authentication.py": null,
#             "blog.py": null,
#             "user.py": null
#         },
#         "schemas.py": null,
#         "test.py": null
#     }
# }
