# omnipy/io/file_ops.py
from pathlib import Path
from typing import Union, List, Optional
import os
import fnmatch
from core.logger import setup_logger

__all__ = ["list_files_in_directory"]

logger = setup_logger(__name__)


def list_files_in_directory(
    path: Optional[Union[str, Path]] = None,
    pattern: Optional[str] = None,
    show_hidden: bool = False,
    return_paths: bool = False,
) -> Union[List[str], List[Path]]:
    """Return files in ``path`` (non-recursive) with optional glob ``pattern``.

    This implementation uses ``os.scandir`` for better performance on large
    directories and avoids constructing ``Path`` objects unless requested.

    Args:
        path: Target directory path. Defaults to current working directory.
        pattern: Glob pattern (e.g. "*.log", "*.txt"). Matches file names only.
        show_hidden: Include hidden files (names starting with '.')
        return_paths: If True return :class:`pathlib.Path` objects, else names.

    Returns:
        List[str] or List[pathlib.Path]

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the path exists but is not a directory.
        PermissionError: If directory cannot be accessed.
    """

    if path is None:
        dir_path = Path.cwd()
    else:
        dir_path = Path(path).resolve()

    if not dir_path.exists():
        logger.error("Directory not found: %s", dir_path)
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")

    if not dir_path.is_dir():
        logger.error("Path is not a directory: %s", dir_path)
        raise ValueError(f"'{dir_path}' is not a directory.")

    results: Union[List[str], List[Path]] = []

    try:
        with os.scandir(dir_path) as it:
            for entry in it:
                # only regular files (skip directories, sockets, etc.)
                try:
                    if not entry.is_file(follow_symlinks=False):
                        continue
                except OSError:
                    # In some rare cases metadata access can fail; skip entry.
                    continue

                name = entry.name

                if not show_hidden and name.startswith("."):
                    continue

                if pattern and not fnmatch.fnmatch(name, pattern):
                    continue

                if return_paths:
                    results.append(Path(entry.path))
                else:
                    results.append(name)
    except PermissionError:
        logger.exception("Permission denied accessing directory: %s", dir_path)
        raise

    # Sort consistently (case-insensitive)
    results.sort(key=lambda x: x.name.lower() if isinstance(x, Path) else x.lower())

    logger.info("Found %d files in '%s' (pattern: %s)", len(results), dir_path, pattern)
    return results