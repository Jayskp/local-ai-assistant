"""
Universal app and file launcher for Windows
Finds and opens any installed application or file
"""
import os
import subprocess
import json
from pathlib import Path


# Cache file for app locations
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".ai_assistant", "app_cache.json")


def open_app_or_file(name: str) -> str:
    """
    Universal opener - tries to open app or file
    
    Args:
        name: App name (e.g., "notepad", "spotify") or file path
        
    Returns:
        Success/error message
    """
    name_lower = name.lower().strip()
    
    # Check if it's a file path
    if os.path.exists(name):
        return _open_file(name)
    
    # Try to find and open as application
    app_path = find_app(name_lower)
    
    if app_path:
        return _launch_app(app_path, name)
    
    # Last resort: try Windows start command
    try:
        subprocess.Popen(["start", "", name], shell=True)
        return f"✅ Launched '{name}'"
    except Exception as e:
        return f"❌ Could not find or open '{name}': {e}"


def find_app(app_name: str) -> str | None:
    """
    Find application by name using robust Windows search
    """
    # 1. Try generic Windows Apps search (Start Menu index)
    # This covers both Store Apps (WhatsApp) and Win32 Apps
    app_id = _find_app_id_powershell(app_name)
    if app_id:
        return f"__APPS_FOLDER__:{app_id}"

    # 2. Try cache (for file paths)
    cache = _load_cache()
    if app_name in cache:
        path = cache[app_name]
        if os.path.exists(path):
            return path
    
    # 3. Manual file search (fallback for portable apps not in Start Menu)
    locations = _get_search_locations()
    for location in locations:
        result = _search_directory(location, app_name)
        if result:
            _save_to_cache(app_name, result)
            return result
    
    return None


def _find_app_id_powershell(app_name: str) -> str | None:
    """
    Use PowerShell to find the AppUserModelID (AUMID) for any installed app.
    This works for Microsoft Store apps (WhatsApp, Spotify) and standard apps.
    """
    try:
        # Use Get-StartApps to utilize Windows native app index
        # We look for a name match and return the AppID
        # We handle quotes in app_name by escaping them or using simple matching
        safe_name = app_name.replace("'", "''")
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Get-StartApps | Where-Object {{ $_.Name -like '*{safe_name}*' }} | Select-Object -First 1 -ExpandProperty AppID"
        ]
        
        # Don't show a window for this check
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            startupinfo=startupinfo,
            timeout=5
        )
        
        app_id = result.stdout.strip()
        if app_id:
            return app_id
            
    except Exception:
        pass
        
    return None


def _launch_app(app_path: str, app_name: str) -> str:
    """Launch application from path or AppID"""
    try:
        # Handle Windows Apps (Store/Start Menu)
        if app_path.startswith("__APPS_FOLDER__:"):
            app_id = app_path.replace("__APPS_FOLDER__:", "")
            # Launch using shell:AppsFolder which is robust for UWP/Store apps
            subprocess.Popen(f'explorer.exe shell:AppsFolder\\{app_id}', shell=True)
            return f"✅ Launched '{app_name}' via Windows Shell"

        # Handle .lnk shortcuts
        if app_path.endswith('.lnk'):
            os.startfile(app_path)
        else:
            subprocess.Popen([app_path], shell=True)
        
        return f"✅ Opened '{app_name}'"
    except Exception as e:
        return f"❌ Failed to launch '{app_name}': {e}"


def _search_directory(directory: str, app_name: str, max_depth: int = 3) -> str | None:
    """Recursively search directory for app"""
    if not os.path.exists(directory):
        return None
        
    try:
        # Look for .exe, .lnk, .bat files
        for root, dirs, files in os.walk(directory):
            # Limit depth
            depth = root[len(directory):].count(os.sep)
            if depth > max_depth:
                continue
            
            for file in files:
                file_lower = file.lower()
                
                # Check if filename matches
                if app_name in file_lower:
                    if file_lower.endswith(('.exe', '.lnk', '.bat')):
                        full_path = os.path.join(root, file)
                        # Prefer exact matches to avoid partial noise
                        if file_lower.startswith(app_name):
                            return full_path
                        # Store as potential match
                        return full_path
    except (PermissionError, OSError):
        pass
    
    return None


def _get_search_locations() -> list:
    """Get common Windows app installation locations"""
    user_profile = os.path.expanduser("~")
    
    return [
        # Start Menu (most likely)
        os.path.join(user_profile, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join("C:\\ProgramData", "Microsoft", "Windows", "Start Menu", "Programs"),
        
        # Program Files
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        
        # User AppData
        os.path.join(user_profile, "AppData", "Local", "Programs"),
        os.path.join(user_profile, "AppData", "Roaming"),
        
        # Common app locations
        "C:\\Windows\\System32",
        os.path.join(user_profile, "Desktop"),
        
        # Users Public Desktop
        "C:\\Users\\Public\\Desktop",
    ]


def _open_file(file_path: str) -> str:
    """Open file with default application"""
    try:
        os.startfile(file_path)
        filename = os.path.basename(file_path)
        return f"✅ Opened '{filename}'"
    except Exception as e:
        return f"❌ Failed to open file: {e}"


def _load_cache() -> dict:
    """Load app cache"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def _save_to_cache(app_name: str, path: str):
    """Save app location to cache"""
    cache = _load_cache()
    cache[app_name] = path
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except:
        pass


def clear_cache():
    """Clear the app cache (useful if apps moved)"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    return "✅ App cache cleared"


# Predefined common app mappings (for speed)
COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",  # Windows Terminal
    "taskmgr": "taskmgr.exe",
    # Office apps removed from here to use robust Start Menu search instead
}


def open_common_app(app_name: str) -> str | None:
    """Quick launch for common Windows apps"""
    app_lower = app_name.lower()
    
    if app_lower in COMMON_APPS:
        try:
            subprocess.Popen([COMMON_APPS[app_lower]], shell=True)
            return f"✅ Opened {app_name}"
        except:
            pass
    
    return None
