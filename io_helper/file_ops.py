# omnipy/io/file_ops.py
from pathlib import Path
from typing import Union, List, Optional
from core.logger import setup_logger

logger = setup_logger(__name__)

def list_files_in_directory(
    path: Optional[Union[str, Path]] = None,
    pattern: Optional[str] = None,
    show_hidden: bool = False,
    return_paths: bool = False
) -> Union[List[str], List[Path]]:
    """
    List only FILES (not directories) in a given directory.
    If no path is provided, uses the current working directory.
    
    Args:
        path: Target directory path. Defaults to current working directory.
        pattern: Glob pattern (e.g., "*.log", "*.txt")
        show_hidden: Include hidden files (starting with .)
        return_paths: If True, return Path objects; else return names as strings
    
    Returns:
        List of filenames (str) or Path objects
    
    Raises:
        ValueError: If path is not a directory
        FileNotFoundError: If path does not exist
    """
    # Handle default: use current working directory if path is None
    if path is None:
        dir_path = Path.cwd()
    else:
        dir_path = Path(path).resolve()
    
    if not dir_path.exists():
        logger.error(f"Directory not found: {dir_path}")
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")
    
    if not dir_path.is_dir():
        logger.error(f"Path is not a directory: {dir_path}")
        raise ValueError(f"'{dir_path}' is not a directory.")

    # Get all items
    if pattern:
        items = list(dir_path.glob(pattern))
    else:
        items = list(dir_path.iterdir())
    
    # Filter only files
    files = [item for item in items if item.is_file()]
    
    # Exclude hidden if needed
    if not show_hidden:
        files = [f for f in files if not f.name.startswith(".")]
    
    # Sort by name
    files.sort(key=lambda x: x.name.lower())
    
    logger.info(f"Found {len(files)} files in '{dir_path}' (pattern: {pattern})")
    
    if return_paths:
        return files
    else:
        return [f.name for f in files]