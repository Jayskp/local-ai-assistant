# System automation utilities

import os
import subprocess

def get_system_info():
    """Get basic system information."""
    return {
        "os": os.name,
        "cpu_count": os.cpu_count(),
        "user": os.getlogin()
    }

def shutdown():
    """Shutdown the computer."""
    os.system("shutdown /s /t 0")

def restart():
    """Restart the computer."""
    os.system("shutdown /r /t 0")

def sleep():
    """Put the computer to sleep."""
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def lock_screen():
    """Lock the screen."""
    os.system("rundll32.exe user32.dll,LockWorkStation")

def set_volume(level):
    """Set system volume (requires nircmd or similar)."""
    # Placeholder - requires additional tools
    pass
