"""
File Management Utilities for Chunk Monkey

This module provides utility functions for file operations, path management,
and I/O operations. It handles common file tasks like reading, writing,
directory management, and file validation.

Key Features:
- Safe file operations with error handling
- Path validation and normalization
- Directory management
- File type detection and validation
- Backup and cleanup operations
- Cross-platform path handling

Author: Chunk Monkey Team
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import mimetypes
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class FileManager:
    """
    File management utility class with methods for safe file operations,
    path handling, and directory management.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file manager with optional base path.

        Args:
            base_path: Optional base directory for relative operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_extensions = {
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }

    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, creating it if necessary.

        Args:
            path: Directory path to ensure

        Returns:
            Path object for the directory

        Raises:
            PermissionError: If directory cannot be created
        """
        dir_path = Path(path)

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")
            return dir_path
        except PermissionError as e:
            logger.error(f"Permission denied creating directory {dir_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            raise

    def validate_file_path(self, file_path: Union[str, Path], must_exist: bool = True) -> Path:
        """
        Validate and normalize file path.

        Args:
            file_path: File path to validate
            must_exist: Whether file must already exist

        Returns:
            Validated Path object

        Raises:
            FileNotFoundError: If file doesn't exist and must_exist is True
            ValueError: If path is invalid
        """
        path = Path(file_path)

        # Make absolute if relative
        if not path.is_absolute():
            path = self.base_path / path

        # Resolve any symbolic links and relative components
        try:
            path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {file_path}, {e}")

        if must_exist and not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return path

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        path = self.validate_file_path(file_path)

        try:
            stat = path.stat()

            info = {
                'path': str(path),
                'name': path.name,
                'stem': path.stem,
                'suffix': path.suffix,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'mime_type': self.get_mime_type(path),
                'hash_md5': self.get_file_hash(path) if path.is_file() else None
            }

            return info

        except Exception as e:
            logger.error(f"Error getting file info for {path}: {e}")
            raise

    def get_mime_type(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Get MIME type for a file.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string or None if unknown
        """
        path = Path(file_path)

        # Check our supported extensions first
        suffix = path.suffix.lower()
        if suffix in self.supported_extensions:
            return self.supported_extensions[suffix]

        # Fall back to system detection
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type

    def get_file_hash(self, file_path: Union[str, Path], algorithm: str = 'md5') -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')

        Returns:
            Hex string of file hash
        """
        path = self.validate_file_path(file_path)

        hash_obj = hashlib.new(algorithm)

        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            logger.error(f"Error calculating hash for {path}: {e}")
            raise

    def read_text_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """
        Safely read text file content.

        Args:
            file_path: Path to the text file
            encoding: Text encoding to use

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If encoding is incorrect
        """
        path = self.validate_file_path(file_path)

        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            logger.debug(f"Read text file: {path} ({len(content)} characters)")
            return content

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {path}: {e}")
            # Try with different encodings
            for fallback_encoding in ['latin1', 'cp1252', 'utf-16']:
                try:
                    with open(path, 'r', encoding=fallback_encoding) as f:
                        content = f.read()
                    logger.warning(f"Used fallback encoding {fallback_encoding} for {path}")
                    return content
                except UnicodeDecodeError:
                    continue
            raise
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            raise

    def write_text_file(self, file_path: Union[str, Path], content: str,
                       encoding: str = 'utf-8', backup: bool = False) -> None:
        """
        Safely write text content to file.

        Args:
            file_path: Path for the output file
            content: Text content to write
            encoding: Text encoding to use
            backup: Whether to backup existing file

        Raises:
            PermissionError: If file cannot be written
        """
        path = self.validate_file_path(file_path, must_exist=False)

        # Create backup if requested and file exists
        if backup and path.exists():
            self.backup_file(path)

        # Ensure parent directory exists
        self.ensure_directory(path.parent)

        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            logger.debug(f"Wrote text file: {path} ({len(content)} characters)")

        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            raise

    def read_json_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read and parse JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data as dictionary

        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        path = self.validate_file_path(file_path)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.debug(f"Read JSON file: {path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON file {path}: {e}")
            raise

    def write_json_file(self, file_path: Union[str, Path], data: Dict[str, Any],
                       indent: int = 4, backup: bool = False) -> None:
        """
        Write data to JSON file with formatting.

        Args:
            file_path: Path for the output JSON file
            data: Data to serialize to JSON
            indent: JSON indentation spaces
            backup: Whether to backup existing file

        Raises:
            TypeError: If data is not JSON serializable
        """
        path = self.validate_file_path(file_path, must_exist=False)

        # Create backup if requested and file exists
        if backup and path.exists():
            self.backup_file(path)

        # Ensure parent directory exists
        self.ensure_directory(path.parent)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            logger.debug(f"Wrote JSON file: {path}")

        except TypeError as e:
            logger.error(f"Data not JSON serializable for {path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error writing JSON file {path}: {e}")
            raise

    def backup_file(self, file_path: Union[str, Path], backup_dir: Optional[str] = None) -> Path:
        """
        Create a backup copy of a file.

        Args:
            file_path: Path to file to backup
            backup_dir: Optional directory for backups (defaults to same directory)

        Returns:
            Path to the backup file

        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        source_path = self.validate_file_path(file_path)

        # Determine backup location
        if backup_dir:
            backup_parent = self.ensure_directory(backup_dir)
        else:
            backup_parent = source_path.parent

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = backup_parent / backup_name

        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"Created backup: {source_path} -> {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Error creating backup of {source_path}: {e}")
            raise

    def list_files(self, directory: Union[str, Path], pattern: str = "*",
                   recursive: bool = False) -> List[Path]:
        """
        List files in a directory matching a pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        dir_path = self.validate_file_path(directory)

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")

        try:
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))

            # Filter to only include files (not directories)
            files = [f for f in files if f.is_file()]

            logger.debug(f"Found {len(files)} files in {dir_path} with pattern '{pattern}'")
            return files

        except Exception as e:
            logger.error(f"Error listing files in {dir_path}: {e}")
            raise

    def clean_directory(self, directory: Union[str, Path], pattern: str = "*",
                       max_age_days: Optional[int] = None) -> int:
        """
        Clean files from a directory based on pattern and age.

        Args:
            directory: Directory to clean
            pattern: Glob pattern for files to clean
            max_age_days: Maximum age in days (None = all matching files)

        Returns:
            Number of files cleaned

        Raises:
            PermissionError: If files cannot be deleted
        """
        dir_path = self.validate_file_path(directory)
        files = self.list_files(dir_path, pattern)

        cleaned_count = 0
        cutoff_time = None

        if max_age_days is not None:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)

        for file_path in files:
            try:
                # Check age if specified
                if cutoff_time is not None:
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime > cutoff_time:
                        continue  # File is too new

                file_path.unlink()
                cleaned_count += 1
                logger.debug(f"Cleaned file: {file_path}")

            except Exception as e:
                logger.warning(f"Could not clean file {file_path}: {e}")

        logger.info(f"Cleaned {cleaned_count} files from {dir_path}")
        return cleaned_count

    def copy_file(self, source: Union[str, Path], destination: Union[str, Path],
                  overwrite: bool = False) -> None:
        """
        Copy a file to a new location.

        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files

        Raises:
            FileExistsError: If destination exists and overwrite is False
        """
        source_path = self.validate_file_path(source)
        dest_path = self.validate_file_path(destination, must_exist=False)

        # Check if destination exists
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {dest_path}")

        # Ensure destination directory exists
        self.ensure_directory(dest_path.parent)

        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied file: {source_path} -> {dest_path}")

        except Exception as e:
            logger.error(f"Error copying file {source_path} to {dest_path}: {e}")
            raise

    def move_file(self, source: Union[str, Path], destination: Union[str, Path],
                  overwrite: bool = False) -> None:
        """
        Move a file to a new location.

        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files

        Raises:
            FileExistsError: If destination exists and overwrite is False
        """
        source_path = self.validate_file_path(source)
        dest_path = self.validate_file_path(destination, must_exist=False)

        # Check if destination exists
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {dest_path}")

        # Ensure destination directory exists
        self.ensure_directory(dest_path.parent)

        try:
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved file: {source_path} -> {dest_path}")

        except Exception as e:
            logger.error(f"Error moving file {source_path} to {dest_path}: {e}")
            raise

    def get_available_filename(self, file_path: Union[str, Path]) -> Path:
        """
        Get an available filename by adding numbers if file exists.

        Args:
            file_path: Desired file path

        Returns:
            Available file path (may have number suffix)
        """
        path = Path(file_path)

        if not path.exists():
            return path

        # Add numbers until we find an available name
        counter = 1
        while True:
            new_name = f"{path.stem}_{counter}{path.suffix}"
            new_path = path.parent / new_name

            if not new_path.exists():
                return new_path

            counter += 1


# Convenience functions for direct use
def ensure_directory(path: Union[str, Path]) -> Path:
    """Convenience function to ensure directory exists."""
    manager = FileManager()
    return manager.ensure_directory(path)


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Convenience function to read JSON file."""
    manager = FileManager()
    return manager.read_json_file(file_path)


def write_json_file(file_path: Union[str, Path], data: Dict[str, Any],
                   indent: int = 4) -> None:
    """Convenience function to write JSON file."""
    manager = FileManager()
    return manager.write_json_file(file_path, data, indent)


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Convenience function to get file information."""
    manager = FileManager()
    return manager.get_file_info(file_path)
