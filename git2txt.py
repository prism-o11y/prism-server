import os
import sys

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".DS_Store",
}

IGNORE_EXTENSIONS = {
    ".env",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".o",
    ".a",
    ".class",
    ".jar",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".pyc",
    ".swp",
    ".lock",
    ".db",
    ".sqlite",
    ".pdf",
    ".md",
    ".txt",
}


def is_text_file(file_path):
    """
    Check if a file is a text file.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if it's a text file, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read(1024)
        return True
    except Exception:
        return False


def process_directory(root_dir):
    """
    Process the directory and output the contents of text files.

    Args:
        root_dir (str): The root directory to start processing.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() in IGNORE_EXTENSIONS:
                continue

            file_path = os.path.join(dirpath, filename)

            if is_text_file(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        print(f"===== Begin File: {file_path} =====")
                        print(content)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}", file=sys.stderr)
            else:
                print(f"Skipping binary file: {file_path}", file=sys.stderr)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python git2text.py <root_dir>")
        sys.exit(1)

    process_directory(sys.argv[1])


if __name__ == "__main__":
    main()