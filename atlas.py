"""
Atlas - Independent file management module
================================================

A standalone, platform-independent file management system that works
seamlessly in both development and PyInstaller executable environments.

Author: Nils DONTOT
Github Repository: https://github.com/Nitr0xis/Atlas
Version: 1.1.0
License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0)

Changelog v1.1.0:
    - Added project_root parameter for flexible root directory configuration
    - Auto-detects project root by default (goes up from module location)
    - Allows manual override for custom project structures

Usage:
    from atlas import FileManager

    # Auto-detect project root (default)
    fm = FileManager(project_name="MyProject")

    # Manual project root (custom structure)
    fm = FileManager(project_name="MyProject", project_root="/custom/path")

    # Use methods
    fm.create_folder('screenshots')
    fm.write_file('config.json', '{"setting": "value"}')
    content = fm.read_file('config.json', default='{}')
"""

import os
import sys
import shutil
from typing import Optional, Union, List


class FileManager:
    """
    Standalone file management system with automatic path resolution.

    Handles file operations in both development and PyInstaller environments,
    automatically choosing appropriate directories for user data.

    Attributes:
        project_name: Name of the project (used for Documents folder)
        project_root: Root directory of the project (auto-detected or manual)
        dev_data_folder: Folder name for development mode (default: 'user_data')
        use_documents: Whether to use Documents folder in exe mode (default: True)
    """

    def __init__(self,
                 project_name: str = "MyProject",
                 project_root: Optional[str] = None,
                 dev_data_folder: str = "user_data",
                 use_documents: bool = True):
        """
        Initialize FileManager with project configuration.

        Args:
            project_name: Name of your project (used for Documents/ProjectName/)
            project_root: Root directory of project (auto-detected if None)
                         Auto-detection: goes up from atlas.py location
                         Manual: provide absolute path to project root
            dev_data_folder: Folder name for dev mode (default: 'user_data')
            use_documents: If True, uses Documents folder in exe mode
                          If False, uses executable's directory

        Examples:
            >>> # Auto-detect (atlas.py in src/, goes to parent)
            >>> fm = FileManager(project_name="GravityEngine")
            
            >>> # Manual root (custom structure)
            >>> fm = FileManager(
            ...     project_name="MyGame",
            ...     project_root="/custom/project/path"
            ... )
            
            >>> # Custom data folder
            >>> fm = FileManager(
            ...     project_name="MyGame",
            ...     dev_data_folder="data"
            ... )
        """
        self.project_name = project_name
        self.dev_data_folder = dev_data_folder
        self.use_documents = use_documents

        # Detect execution mode
        self.is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

        # Set project root
        if project_root is not None:
            # Manual override
            self.project_root = os.path.dirname(os.path.abspath(project_root))
        else:
            # Auto-detect: go up one level from atlas.py location
            # __file__ = C:/Project/src/atlas.py
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
            >>> fm.resource_path('assets/font.ttf')
            'C:/Projects/MyProject/assets/font.ttf'  # Dev
            'C:/Users/.../Temp/_MEI123/assets/font.ttf'  # PyInstaller
        """
        try:
            # PyInstaller mode: _MEIPASS is the extracted temp folder
            base_path = sys._MEIPASS
        except AttributeError:
            # Development mode: use configured project root
            base_path = self.project_root

        return os.path.join(base_path, os.path.normpath(relative_path))

    def user_data_path(self, relative_path: str = "") -> str:
        """
        Get path for user data that persists between sessions.

        Returns appropriate directory based on execution mode and configuration:
        - Development: <project_root>/<dev_data_folder>/
        - PyInstaller + use_documents: Documents/ProjectName/
        - PyInstaller + not use_documents: ./ProjectName/

        Args:
            relative_path: Optional subdirectory/file within user data folder

        Returns:
            Absolute path to user data location

        Examples:
            >>> fm.user_data_path()
            'C:/Project/user_data/'  # Dev
            'C:/Users/Account/Documents/MyProject/'  # Exe

            >>> fm.user_data_path('screenshots/image.png')
            'C:/Project/user_data/screenshots/image.png'  # Dev
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
            # Development mode: use configured project root + data folder
            base_path = os.path.join(self.project_root, self.dev_data_folder)

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
                          If False, creates at absolute path or relative to project root
            parents: If True, creates parent directories as needed
            exist_ok: If True, doesn't raise error if folder exists

        Returns:
            Absolute path to created folder, or None on error

        Examples:
            >>> # Create in user_data
            >>> fm.create_folder('screenshots')
            'C:/Project/user_data/screenshots/'

            >>> # Create relative to project root
            >>> fm.create_folder('logs', use_user_data=False)
            'C:/Project/logs/'

            >>> # Create at absolute path
            >>> fm.create_folder('C:/temp/test', use_user_data=False)
            'C:/temp/test/'
        """
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                # If absolute path, use as-is; if relative, join with project root
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

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
                          If False, creates at absolute path or relative to project root
            encoding: Text encoding (default: 'utf-8')
            create_parents: If True, creates parent directories

        Returns:
            Absolute path to created file, or None on error

        Examples:
            >>> # Create in user_data
            >>> fm.create_file('config.txt', 'setting=value')
            'C:/Project/user_data/config.txt'

            >>> # Create relative to project root
            >>> fm.create_file('README.md', '# Project', use_user_data=False)
            'C:/Project/README.md'
        """
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

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
        """Write content to a file."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

            if create_parents:
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

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
        """Read content from a file."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

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
        """Delete a file."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

            if not os.path.exists(full_path):
                return missing_ok

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
        """Delete a folder."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

            if not os.path.exists(full_path):
                return missing_ok

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
        """Check if a file exists."""
        if use_user_data:
            full_path = self.user_data_path(path)
        else:
            if os.path.isabs(path):
                full_path = path
            else:
                full_path = os.path.join(self.project_root, path)
        return os.path.isfile(full_path)

    def folder_exists(self, path: str, use_user_data: bool = True) -> bool:
        """Check if a folder exists."""
        if use_user_data:
            full_path = self.user_data_path(path)
        else:
            if os.path.isabs(path):
                full_path = path
            else:
                full_path = os.path.join(self.project_root, path)
        return os.path.isdir(full_path)

    def list_files(self,
                   path: str = "",
                   use_user_data: bool = True,
                   extension: Optional[str] = None,
                   include_hidden: bool = False,
                   absolute_paths: bool = False) -> List[str]:
        """List all files in a folder."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path) if path else self.project_root

            if not os.path.exists(full_path):
                return []

            files = []
            for item in os.listdir(full_path):
                if not include_hidden and item.startswith('.'):
                    continue
                item_path = os.path.join(full_path, item)
                if os.path.isfile(item_path):
                    if extension is None or item.endswith(extension):
                        files.append(item_path if absolute_paths else item)

            return sorted(files)

        except Exception as e:
            print(f"✗ Failed to list files in '{path}': {e}")
            return []

    def list_folders(self,
                     path: str = "",
                     use_user_data: bool = True,
                     include_hidden: bool = False,
                     absolute_paths: bool = False) -> List[str]:
        """List all folders in a directory."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path) if path else self.project_root

            if not os.path.exists(full_path):
                return []

            folders = []
            for item in os.listdir(full_path):
                if not include_hidden and item.startswith('.'):
                    continue
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    folders.append(item_path if absolute_paths else item)

            return sorted(folders)

        except Exception as e:
            print(f"✗ Failed to list folders in '{path}': {e}")
            return []

    def get_file_size(self, path: str, use_user_data: bool = True) -> Optional[int]:
        """Get file size in bytes."""
        try:
            if use_user_data:
                full_path = self.user_data_path(path)
            else:
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(self.project_root, path)

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
        """Copy a file from source to destination."""
        try:
            if use_user_data_src:
                src_path = self.user_data_path(src)
            else:
                src_path = src if os.path.isabs(src) else os.path.join(self.project_root, src)

            if use_user_data_dst:
                dst_path = self.user_data_path(dst)
            else:
                dst_path = dst if os.path.isabs(dst) else os.path.join(self.project_root, dst)

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
        """Move/rename a file."""
        try:
            if use_user_data_src:
                src_path = self.user_data_path(src)
            else:
                src_path = src if os.path.isabs(src) else os.path.join(self.project_root, src)

            if use_user_data_dst:
                dst_path = self.user_data_path(dst)
            else:
                dst_path = dst if os.path.isabs(dst) else os.path.join(self.project_root, dst)

            dst_parent = os.path.dirname(dst_path)
            if dst_parent:
                os.makedirs(dst_parent, exist_ok=True)

            shutil.move(src_path, dst_path)
            return True

        except Exception as e:
            print(f"✗ Failed to move file '{src}' to '{dst}': {e}")
            return False
