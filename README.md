# Atlas - File Management Module

**Version:** 1.0.0  
**Author:** Nils DONTOT  
**License:** CC BY-NC-SA 4.0

---

## Overview

**Atlas** is a standalone, platform-independent file management module designed to work seamlessly in both **development (.py)** and **PyInstaller executable (.exe)** environments.

### Key Features

**Dual-mode operation** - Works in .py and .exe without code changes  
**Automatic path resolution** - Handles Documents/, user_data/, and executable paths  
**Cross-platform** - Windows, macOS, Linux support  
**Zero external dependencies** - Only Python standard library  
**Type-hinted** - Full type annotations for better IDE support  
**Production-ready** - Robust error handling and logging  

---

## Quick Start

### Installation

Simply place `atlas.py` in your project directory:

```
YourProject/
├── atlas.py          ← Place module here
├── main.py
└── assets/
```

### Basic Usage

```python
from atlas import FileManager

# Initialize
fm = FileManager(project_name="MyProject")

# Create folders
fm.create_folder('screenshots')
fm.create_folder('saves')

# Write files
fm.write_file('config.json', '{"setting": "value"}')
fm.write_file('log.txt', 'Log entry\n', mode='a')

# Read files
config = fm.read_file('config.json', default='{}')

# Check existence
if fm.file_exists('config.json'):
    config = fm.read_file('config.json')

# List files
screenshots = fm.list_files('screenshots', extension='.png')
```

---

## How It Works

### Development Mode (.py)

```
YourProject/
├── atlas.py
├── main.py
└── user_data/              ← Created automatically
    ├── screenshots/
    ├── saves/
    └── config.json
```

### Executable Mode (.exe)

**Windows:**
```
C:/Users/YourName/Documents/
└── MyProject/              ← Created automatically
    ├── screenshots/
    ├── saves/
    └── config.json
```

**macOS:**
```
~/Documents/MyProject/
```

**Linux:**
```
~/MyProject/
```

---

## 🔧 Configuration

### Initialize with Options

```python
fm = FileManager(
    project_name="MyGame",          # Folder name in Documents/
    dev_data_folder="user_data",    # Folder for dev mode
    use_documents=True              # Use Documents/ in .exe mode
)
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `project_name` | `"MyProject"` | Project folder name |
| `dev_data_folder` | `"user_data"` | Dev mode data folder |
| `use_documents` | `True` | Use Documents folder in .exe |

---

## API Reference

### Path Methods

#### `resource_path(relative_path: str) -> str`
Get absolute path to bundled resources (assets, fonts, etc.)

```python
font_path = fm.resource_path('assets/font.ttf')
# Dev:  C:/YourProject/assets/font.ttf
# Exe:  C:/Users/.../Temp/_MEI123/assets/font.ttf
```

#### `user_data_path(relative_path: str = "") -> str`
Get absolute path to user data directory

```python
data_path = fm.user_data_path()
# Dev:  C:/YourProject/user_data/
# Exe:  C:/Users/Name/Documents/MyProject/

screenshot_path = fm.user_data_path('screenshots/image.png')
# Dev:  C:/YourProject/user_data/screenshots/image.png
```

### Folder Operations

#### `create_folder(path, use_user_data=True, parents=True, exist_ok=True) -> Optional[str]`
Create a folder (and parent folders if needed)

```python
fm.create_folder('screenshots')
fm.create_folder('saves/backup')
fm.create_folder('C:/temp/test', use_user_data=False)
```

**Parameters:**
- `path`: Relative or absolute path
- `use_user_data`: Use user_data location (default: True)
- `parents`: Create parent directories (default: True)
- `exist_ok`: Don't error if exists (default: True)

#### `folder_exists(path, use_user_data=True) -> bool`
Check if a folder exists

```python
if not fm.folder_exists('screenshots'):
    fm.create_folder('screenshots')
```

#### `list_folders(path="", use_user_data=True, include_hidden=False, absolute_paths=False) -> List[str]`
List all folders in a directory

```python
folders = fm.list_folders()
# ['screenshots', 'saves', 'logs']

folders = fm.list_folders(absolute_paths=True)
# ['C:/path/screenshots', 'C:/path/saves', ...]
```

#### `remove_folder(path, use_user_data=True, recursive=False, missing_ok=True) -> bool`
Delete a folder

```python
fm.remove_folder('temp', recursive=True)  # Delete with contents
fm.remove_folder('empty_folder')         # Delete only if empty
```

### File Operations

#### `create_file(path, content="", use_user_data=True, encoding='utf-8', create_parents=True) -> Optional[str]`
Create a new file with optional content

```python
fm.create_file('config.txt', 'setting=value')
fm.create_file('data/save.json', '{"score": 100}')
```

#### `write_file(path, content, mode='w', use_user_data=True, encoding='utf-8', create_parents=True) -> Optional[str]`
Write content to a file

```python
fm.write_file('log.txt', 'New entry\n', mode='a')  # Append
fm.write_file('config.json', json.dumps(data))     # Overwrite
```

**Modes:**
- `'w'`: Overwrite (default)
- `'a'`: Append
- `'wb'`: Binary write

#### `read_file(path, mode='r', use_user_data=True, encoding='utf-8', default=None) -> Union[str, bytes, any]`
Read content from a file

```python
content = fm.read_file('config.txt')
data = fm.read_file('save.json', default='{}')  # Return '{}' if missing
```

#### `file_exists(path, use_user_data=True) -> bool`
Check if a file exists

```python
if fm.file_exists('config.json'):
    config = fm.read_file('config.json')
```

#### `list_files(path="", use_user_data=True, extension=None, include_hidden=False, absolute_paths=False) -> List[str]`
List all files in a folder

```python
screenshots = fm.list_files('screenshots')
# ['screenshot_001.png', 'screenshot_002.png']

saves = fm.list_files('saves', extension='.json')
# ['save_1.json', 'save_2.json']

full_paths = fm.list_files('screenshots', absolute_paths=True)
# ['C:/path/screenshots/screenshot_001.png', ...]
```

#### `remove_file(path, use_user_data=True, missing_ok=True) -> bool`
Delete a file

```python
fm.remove_file('old_save.json')  # Returns True if successful
```

#### `get_file_size(path, use_user_data=True) -> Optional[int]`
Get file size in bytes

```python
size = fm.get_file_size('config.json')
print(f"Size: {size} bytes")
```

#### `copy_file(src, dst, use_user_data_src=True, use_user_data_dst=True) -> bool`
Copy a file

```python
fm.copy_file('config.json', 'config_backup.json')
fm.copy_file('saves/save1.json', 'backups/save1_backup.json')
```

#### `move_file(src, dst, use_user_data_src=True, use_user_data_dst=True) -> bool`
Move or rename a file

```python
fm.move_file('old_name.txt', 'new_name.txt')
fm.move_file('temp/file.txt', 'archive/file.txt')
```

---

## Usage Examples

### Screenshot System

```python
from atlas import FileManager
import pygame
from datetime import datetime

fm = FileManager(project_name="MyGame")

def take_screenshot(screen):
    # Create folder if needed
    fm.create_folder('screenshots')
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    
    # Save screenshot
    filepath = fm.user_data_path(f'screenshots/{filename}')
    pygame.image.save(screen, filepath)
    
    print(f"✓ Screenshot saved: {filename}")
```

### Save/Load System

```python
import json
from datetime import datetime

fm = FileManager(project_name="MyGame")

def save_game(game_state):
    fm.create_folder('saves')
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "level": game_state.level,
        "score": game_state.score,
        "player": {
            "x": game_state.player.x,
            "y": game_state.player.y
        }
    }
    
    filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    fm.write_file(f'saves/{filename}', json.dumps(data, indent=2))
    print(f"✓ Game saved: {filename}")

def load_game(filename):
    content = fm.read_file(f'saves/{filename}', default=None)
    if content is None:
        print("✗ Save file not found")
        return None
    
    try:
        data = json.loads(content)
        print(f"✓ Game loaded: {filename}")
        return data
    except json.JSONDecodeError:
        print("✗ Invalid save file")
        return None

def list_saves():
    return fm.list_files('saves', extension='.json')
```

### Configuration System

```python
import json

fm = FileManager(project_name="MyGame")

class Config:
    def __init__(self):
        self.fps = 60
        self.volume = 0.5
        self.fullscreen = True
    
    def save(self):
        data = {
            "fps": self.fps,
            "volume": self.volume,
            "fullscreen": self.fullscreen
        }
        fm.write_file('config.json', json.dumps(data, indent=2))
    
    def load(self):
        content = fm.read_file('config.json', default=None)
        if content:
            try:
                data = json.loads(content)
                self.fps = data.get("fps", 60)
                self.volume = data.get("volume", 0.5)
                self.fullscreen = data.get("fullscreen", True)
            except json.JSONDecodeError:
                print("✗ Invalid config, using defaults")

# Usage
config = Config()
config.load()  # Load saved config or use defaults
```

### Logging System

```python
from datetime import datetime

fm = FileManager(project_name="MyGame")

class Logger:
    def __init__(self):
        fm.create_folder('logs')
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        today = datetime.now().strftime("%Y%m%d")
        fm.write_file(f'logs/log_{today}.txt', log_line, mode='a')

# Usage
logger = Logger()
logger.log("Game started")
logger.log("Level loaded", "INFO")
logger.log("Error loading texture", "ERROR")
```

---

## Building with PyInstaller

### Build Configuration

When building your executable with PyInstaller, `atlas.py` will be automatically included if imported. No special configuration needed!

```bash
# Simple build
pyinstaller --onefile main.py

# With icon
pyinstaller --onefile --icon=icon.ico main.py

# With assets
pyinstaller --onefile --add-data "assets;assets" main.py
```

### Important Notes

1. **`resource_path()` for bundled assets:**
   ```python
   # Use this for fonts, images, etc. bundled in .exe
   font_path = fm.resource_path('assets/font.ttf')
   ```

2. **`user_data_path()` for user files:**
   ```python
   # Use this for saves, screenshots, logs, etc.
   save_path = fm.user_data_path('saves/save1.json')
   ```

3. **atlas.py location:**
   - Place `atlas.py` in the same directory as your main script
   - It will be automatically bundled by PyInstaller

---

## Compatibility

### Verified Working

| Function | .py (Dev) | .exe (PyInstaller) |
|----------|-----------|-------------------|
| `resource_path()` | Y | Y |
| `user_data_path()` | Y | Y |
| `create_folder()` | Y | Y |
| `create_file()` | Y | Y |
| `write_file()` | Y | Y |
| `read_file()` | Y | Y |
| `remove_file()` | Y | Y |
| `remove_folder()` | Y | Y |
| `file_exists()` | Y | Y |
| `folder_exists()` | Y | Y |
| `list_files()` | Y | Y |
| `list_folders()` | Y | Y |
| `get_file_size()` | Y | Y |
| `copy_file()` | Y | Y |
| `move_file()` | Y | Y |

### Platform Support

- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian, Fedora)

---

## Troubleshooting

### Issue: "Module 'atlas' not found"

**Solution:** Make sure `atlas.py` is in the same directory as your main script.

```
YourProject/
├── atlas.py      ← Must be here
├── main.py
```

### Issue: Files not persisting after closing .exe

**Solution:** Make sure you're using `user_data_path()`, not `resource_path()`:

```python
# ✓ Correct (persistent)
fm.write_file('config.json', data)

# ✗ Wrong (not persistent in .exe)
path = fm.resource_path('config.json')
```

### Issue: Permission denied when creating files

**Solution:** The module automatically handles this by using appropriate directories:
- Dev: Local `user_data/` folder
- Exe: User's Documents folder (has write permissions)

---

## License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

Copyright (c) 2026 Nils DONTOT

You are free to:
- Share and adapt the code

Under these terms:
- **Attribution** - Credit the author
- **NonCommercial** - No commercial use
- **ShareAlike** - Distribute under same license

---

## Author

**Nils DONTOT** (age 15)  
Email: nils.dontot.pro@gmail.com  
GitHub: [@Nitr0xis](https://github.com/Nitr0xis)

---

## 🌟 Star this Module!

If you find Atlas useful, consider giving it a star on GitHub!

**Made with ❤️ by Nils DONTOT**

*Last updated: February 2026*  
*Version: 1.0.0*
