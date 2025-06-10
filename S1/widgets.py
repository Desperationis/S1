import os

def size_of_file(path: str) -> str:
    """
    Returns the size of the file at 'path' as a human-readable string.
    Example: "13MB", "177KB", "512B"
    """

    if not os.path.exists(path):
        return "0B"

    size_bytes = os.path.getsize(path)
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    # Remove trailing .0 for integers, keep one decimal otherwise
    if size_bytes == int(size_bytes):
        size_str = f"{int(size_bytes)}{units[i]}"
    else:
        size_str = f"{size_bytes:.1f}{units[i]}"
    return size_str
