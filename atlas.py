"""
Atlas - Independent file management module
================================================

A standalone, platform-independent file management system that works
seamlessly in both development and PyInstaller executable environments.

Author: Nils DONTOT
Github Repository: https://github.com/Nitr0xis/Atlas
Version: 1.0.0
License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0)

Usage:
    from file_manager import FileManager

    # Initialize with project name
    fm = FileManager(project_name="MyProject")

    # Use methods
    fm.create_folder('screenshots')
    fm.write_file('config.json', '{"setting": "value"}')
    content = fm.read_file('config.json', default='{}')
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Optional, Union, List


class FileManager:
    """
    Standalone file management system with automatic path resolution.

    Handles file operations in both development and PyInstaller environments,
    automatically choosing appropriate directories for user data.

    Attributes:
        project_name: Name of the project (used for Documents folder)
        dev_data_folder: Folder name for development mode (default: 'user_data')
        use_documents: Whether to use Documents folder in exe mode (default: True)
    """

    def __init__(self,
                 project_name: str = "MyProject",
                 dev_data_folder: str = "user_data",
                 use_documents: bool = True):
        """
        Initialize FileManager with project configuration.

        Args:
            project_name: Name of your project (used for Documents/ProjectName/)
            dev_data_folder: Folder name for dev mode (default: 'user_data')
            use_documents: If True, uses Documents folder in exe mode
                          If False, uses executable's directory

        Examples:
            > fm = FileManager(project_name="GravityEngine")
            > fm = FileManager(project_name="MyGame", dev_data_folder="data")
        """
        self.project_name = project_name
        self.dev_data_folder = dev_data_folder
        self.use_documents = use_documents

        # Detect execution mode
        self.is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

    def resource_path(self, relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and PyInstaller.

        Resolves paths to bundled resources (assets, fonts, etc.) that are
        included in the executable or present in the development directory.

        Args:
            relative_path: Path from project root (e.g., 'assets/font.ttf')

        Returns:
            Absolute path to the resource

        Examples:
            > fm.resource_path('assets/font.ttf')
            'C:/Projects/MyProject/assets/font.ttf'  # Dev
            'C:/Users/.../Temp/_MEI123/assets/font.ttf'  # PyInstaller
        """
        try:
            # PyInstaller mode: _MEIPASS is the extracted temp folder
            base_path = sys._MEIPASS
        except AttributeError:
            # Development mode: project root
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, os.path.normpath(relative_path))

    def user_data_path(self, relative_path: str = "") -> str:
        """
        Get path for user data that persists between sessions.

        Returns appropriate directory based on execution mode and configuration:
        - Development: ./user_data/ (or custom dev_data_folder)
        - PyInstaller + use_documents: Documents/ProjectName/
        - PyInstaller + not use_documents: ./ProjectName/

        Args:
            relative_path: Optional subdirectory/file within user data folder

        Returns:
            Absolute path to user data location

        Examples:
            > fm.user_data_path()
            './user_data/'  # Dev
            'C:/Users/Account/Documents/MyProject/'  # Exe

            > fm.user_data_path('screenshots/image.png')
            './user_data/screenshots/image.png'  # Dev
        """
        if self.is_frozen:
            # PyInstaller mode
            if self.use_documents:
                # Use Documents folder
                if os.name == 'nt':  # Windows
                    base_path = os.path.join(
                        os.path.expanduser("~"),
                        "Documents",
                        self.project_name
                    )
                elif sys.platform == 'darwin':  # macOS
                    base_path = os.path.join(
                        os.path.expanduser("~"),
                        "Documents",
                        self.project_name
                    )
                else:  # Linux
                    base_path = os.path.join(
                        os.path.expanduser("~"),
                        self.project_name
                    )
            else:
                # Use executable's directory
                base_path = os.path.join(
                    os.path.dirname(sys.executable),
                    self.project_name
                )
        else:
            # Development mode: use local data folder
            base_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                self.dev_data_folder
            )

        if relative_path:
            return os.path.join(base_path, os.path.normpath(relative_path))
        return base_path

    def create_folder(self,
                      path: str,
                      use_user_data: bool = True,
                      parents: bool = True,
                      exist_ok: bool = True) -> Optional[str]:
        """
        Create a folder (and optionally parent folders).

        Args:
            path: Relative or absolute path to folder
            use_user_data: If True, creates in user_data location
            parents: If True, creates parent directories as needed
            exist_ok: If True, doesn't raise error if folder exists

        Returns:
            Absolute path to created folder, or None on error

        Examples:
            > fm.create_folder('screenshots')
            './user_data/screenshots/'

            > fm.create_folder('C:/temp/test', use_user_data=False)
            'C:/temp/test/'
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if parents:
                os.makedirs(full_path, exist_ok=exist_ok)
            else:
                if not exist_ok and os.path.exists(full_path):
                    raise FileExistsError(f"Folder already exists: {path}")
                os.mkdir(full_path)

            return full_path

        except Exception as e:
            print(f"✗ Failed to create folder '{path}': {e}")
            return None

    def create_file(self,
                    path: str,
                    content: Union[str, bytes] = "",
                    use_user_data: bool = True,
                    encoding: str = 'utf-8',
                    create_parents: bool = True) -> Optional[str]:
        """
        Create a new file with optional content.

        Args:
            path: Relative or absolute path to file
            content: Content to write (string or bytes)
            use_user_data: If True, creates in user_data location
            encoding: Text encoding (default: 'utf-8')
            create_parents: If True, creates parent directories

        Returns:
            Absolute path to created file, or None on error

        Examples:
            > fm.create_file('config.txt', 'setting=value')
            './user_data/config.txt'

            > fm.create_file('data/save.json', '{"score": 100}')
            './user_data/data/save.json'
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            # Create parent directories if needed
            if create_parents:
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

            # Write content
            if isinstance(content, bytes):
                with open(full_path, 'wb') as f:
                    f.write(content)
            else:
                with open(full_path, 'w', encoding=encoding) as f:
                    f.write(content)

            return full_path

        except Exception as e:
            print(f"✗ Failed to create file '{path}': {e}")
            return None

    def write_file(self,
                   path: str,
                   content: Union[str, bytes],
                   mode: str = 'w',
                   use_user_data: bool = True,
                   encoding: str = 'utf-8',
                   create_parents: bool = True) -> Optional[str]:
        """
        Write content to a file.

        Args:
            path: Relative or absolute path to file
            content: Content to write (string or bytes)
            mode: Write mode - 'w' (overwrite), 'a' (append), 'wb' (binary)
            use_user_data: If True, uses user_data location
            encoding: Text encoding (default: 'utf-8')
            create_parents: If True, creates parent directories

        Returns:
            Absolute path to file, or None on error

        Examples:
            > fm.write_file('log.txt', 'New entry\\n', mode='a')
            './user_data/log.txt'

            > fm.write_file('config.json', json.dumps(data))
            './user_data/config.json'
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            # Create parent directories if needed
            if create_parents:
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

            # Write content
            if 'b' in mode:
                with open(full_path, mode) as f:
                    f.write(content)
            else:
                with open(full_path, mode, encoding=encoding) as f:
                    f.write(content)

            return full_path

        except Exception as e:
            print(f"✗ Failed to write file '{path}': {e}")
            return None

    def read_file(self,
                  path: str,
                  mode: str = 'r',
                  use_user_data: bool = True,
                  encoding: str = 'utf-8',
                  default: any = None) -> Union[str, bytes, any]:
        """
        Read content from a file.

        Args:
            path: Relative or absolute path to file
            mode: Read mode - 'r' (text), 'rb' (binary)
            use_user_data: If True, reads from user_data location
            encoding: Text encoding (default: 'utf-8')
            default: Value to return if file doesn't exist or error occurs

        Returns:
            File content (string or bytes), or default value on error

        Examples:
            > content = fm.read_file('config.txt')
            'setting=value'

            > data = fm.read_file('save.json', default='{}')
            '{}'  # If file doesn't exist
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                return default

            if 'b' in mode:
                with open(full_path, mode) as f:
                    return f.read()
            else:
                with open(full_path, mode, encoding=encoding) as f:
                    return f.read()

        except Exception as e:
            print(f"✗ Failed to read file '{path}': {e}")
            return default

    def remove_file(self,
                    path: str,
                    use_user_data: bool = True,
                    missing_ok: bool = True) -> bool:
        """
        Delete a file.

        Args:
            path: Relative or absolute path to file
            use_user_data: If True, deletes from user_data location
            missing_ok: If True, doesn't raise error if file doesn't exist

        Returns:
            True if successful, False otherwise

        Examples:
            > fm.remove_file('old_save.json')
            True
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                if missing_ok:
                    return True
                print(f"⚠ File not found: '{path}'")
                return False

            if not os.path.isfile(full_path):
                print(f"✗ Not a file: '{path}'")
                return False

            os.remove(full_path)
            return True

        except Exception as e:
            print(f"✗ Failed to remove file '{path}': {e}")
            return False

    def remove_folder(self,
                      path: str,
                      use_user_data: bool = True,
                      recursive: bool = False,
                      missing_ok: bool = True) -> bool:
        """
        Delete a folder.

        Args:
            path: Relative or absolute path to folder
            use_user_data: If True, deletes from user_data location
            recursive: If True, deletes folder and all contents
            missing_ok: If True, doesn't raise error if folder doesn't exist

        Returns:
            True if successful, False otherwise

        Examples:
            > fm.remove_folder('temp', recursive=True)
            True  # Deletes folder and contents

            > fm.remove_folder('empty_folder')
            True  # Deletes only if empty
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                if missing_ok:
                    return True
                print(f"⚠ Folder not found: '{path}'")
                return False

            if not os.path.isdir(full_path):
                print(f"✗ Not a folder: '{path}'")
                return False

            if recursive:
                shutil.rmtree(full_path)
            else:
                os.rmdir(full_path)

            return True

        except Exception as e:
            print(f"✗ Failed to remove folder '{path}': {e}")
            return False

    def file_exists(self, path: str, use_user_data: bool = True) -> bool:
        """
        Check if a file exists.

        Args:
            path: Relative or absolute path to file
            use_user_data: If True, checks in user_data location

        Returns:
            True if file exists, False otherwise

        Examples:
            > if fm.file_exists('config.json'):
            ...     config = fm.read_file('config.json')
        """
        full_path = self.user_data_path(path) if use_user_data else path
        return os.path.isfile(full_path)

    def folder_exists(self, path: str, use_user_data: bool = True) -> bool:
        """
        Check if a folder exists.

        Args:
            path: Relative or absolute path to folder
            use_user_data: If True, checks in user_data location

        Returns:
            True if folder exists, False otherwise

        Examples:
            > if not fm.folder_exists('screenshots'):
            ...     fm.create_folder('screenshots')
        """
        full_path = self.user_data_path(path) if use_user_data else path
        return os.path.isdir(full_path)

    def list_files(self,
                   path: str = "",
                   use_user_data: bool = True,
                   extension: Optional[str] = None,
                   include_hidden: bool = False,
                   absolute_paths: bool = False) -> List[str]:
        """
        List all files in a folder.

        Args:
            path: Relative or absolute path to folder (empty = root)
            use_user_data: If True, lists from user_data location
            extension: Optional filter by extension (e.g., '.json')
            include_hidden: If True, includes hidden files (starting with .)
            absolute_paths: If True, returns absolute paths instead of names

        Returns:
            List of filenames (or paths), or empty list on error

        Examples:
            > fm.list_files('screenshots')
            ['screenshot_001.png', 'screenshot_002.png']

            > fm.list_files('saves', extension='.json')
            ['save_1.json', 'save_2.json']

            > fm.list_files('screenshots', absolute_paths=True)
            ['C:/path/screenshots/screenshot_001.png', ...]
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                return []

            files = []
            for item in os.listdir(full_path):
                # Skip hidden files if not requested
                if not include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(full_path, item)
                if os.path.isfile(item_path):
                    # Filter by extension if specified
                    if extension is None or item.endswith(extension):
                        if absolute_paths:
                            files.append(item_path)
                        else:
                            files.append(item)

            return sorted(files)

        except Exception as e:
            print(f"✗ Failed to list files in '{path}': {e}")
            return []

    def list_folders(self,
                     path: str = "",
                     use_user_data: bool = True,
                     include_hidden: bool = False,
                     absolute_paths: bool = False) -> List[str]:
        """
        List all folders in a directory.

        Args:
            path: Relative or absolute path to folder (empty = root)
            use_user_data: If True, lists from user_data location
            include_hidden: If True, includes hidden folders (starting with .)
            absolute_paths: If True, returns absolute paths instead of names

        Returns:
            List of folder names (or paths), or empty list on error

        Examples:
            > fm.list_folders()
            ['screenshots', 'saves', 'logs']

            > fm.list_folders(absolute_paths=True)
            ['C:/path/screenshots', 'C:/path/saves', 'C:/path/logs']
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                return []

            folders = []
            for item in os.listdir(full_path):
                # Skip hidden folders if not requested
                if not include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    if absolute_paths:
                        folders.append(item_path)
                    else:
                        folders.append(item)

            return sorted(folders)

        except Exception as e:
            print(f"✗ Failed to list folders in '{path}': {e}")
            return []

    def get_file_size(self, path: str, use_user_data: bool = True) -> Optional[int]:
        """
        Get file size in bytes.

        Args:
            path: Relative or absolute path to file
            use_user_data: If True, checks in user_data location

        Returns:
            File size in bytes, or None if file doesn't exist

        Examples:
            > size = fm.get_file_size('config.json')
            1024  # bytes
        """
        try:
            full_path = self.user_data_path(path) if use_user_data else path

            if not os.path.exists(full_path):
                return None

            return os.path.getsize(full_path)

        except Exception as e:
            print(f"✗ Failed to get file size '{path}': {e}")
            return None

    def copy_file(self,
                  src: str,
                  dst: str,
                  use_user_data_src: bool = True,
                  use_user_data_dst: bool = True) -> bool:
        """
        Copy a file from source to destination.

        Args:
            src: Source file path
            dst: Destination file path
            use_user_data_src: If True, src is relative to user_data
            use_user_data_dst: If True, dst is relative to user_data

        Returns:
            True if successful, False otherwise

        Examples:
            > fm.copy_file('config.json', 'config_backup.json')
            True
        """
        try:
            src_path = self.user_data_path(src) if use_user_data_src else src
            dst_path = self.user_data_path(dst) if use_user_data_dst else dst

            # Create destination parent directories
            dst_parent = os.path.dirname(dst_path)
            if dst_parent:
                os.makedirs(dst_parent, exist_ok=True)

            shutil.copy2(src_path, dst_path)
            return True

        except Exception as e:
            print(f"✗ Failed to copy file '{src}' to '{dst}': {e}")
            return False

    def move_file(self,
                  src: str,
                  dst: str,
                  use_user_data_src: bool = True,
                  use_user_data_dst: bool = True) -> bool:
        """
        Move/rename a file.

        Args:
            src: Source file path
            dst: Destination file path
            use_user_data_src: If True, src is relative to user_data
            use_user_data_dst: If True, dst is relative to user_data

        Returns:
            True if successful, False otherwise

        Examples:
            > fm.move_file('old_name.txt', 'new_name.txt')
            True
        """
        try:
            src_path = self.user_data_path(src) if use_user_data_src else src
            dst_path = self.user_data_path(dst) if use_user_data_dst else dst

            # Create destination parent directories
            dst_parent = os.path.dirname(dst_path)
            if dst_parent:
                os.makedirs(dst_parent, exist_ok=True)

            shutil.move(src_path, dst_path)
            return True

        except Exception as e:
            print(f"✗ Failed to move file '{src}' to '{dst}': {e}")
            return False
