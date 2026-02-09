# Universal App & File Launcher

## ✅ What Was Added

Your AI Assistant can now open **ANY app or file** on your PC!

## 🚀 How to Use

Just say **"open [app/file name]"**

### Examples

#### Open Built-in Windows Apps
```
open notepad
open calculator
open paint
open cmd
open powershell
open terminal
```

#### Open Installed Apps
```
open spotify
open discord
open slack
open teams
open zoom
open photoshop
open obs
open steam
```

#### Open Microsoft Office
```
open word
open excel
open powerpoint
open outlook
```

#### Open Any File
```
open C:\Users\Admin\Documents\report.pdf
open myfile.txt
open presentation.pptx
```

#### Fuzzy Matching
You don't need exact names:
```
open note           → Opens Notepad
open calc           → Opens Calculator  
open spot           → Opens Spotify
open disc           → Opens Discord
```

---

## 🔍 How It Works

### 1. **Smart Search (Updated)**

The system now uses advanced Windows API (via PowerShell) to find **any installed app**:

1.  **Apps Index Search**: Queries the Windows Start Menu index directly. This finds:
    *   **Store Apps**: WhatsApp, Spotify, Netflix, Instagram
    *   **Win32 Apps**: Steam, Discord, VS Code, Office
    *   **Built-in Apps**: Settings, Calculator, Photos
2.  **Cache**: Instant access for previously opened items.
3.  **Manual Search**: Scans Program Files & Desktop for portable apps not in the index.
4.  **Common Apps**: Hardcoded fast-paths for Notepad, Calculator, CMD, Explorer, Task Manager.

### 2. **Deep Linking Specifics**

For Microsoft Store apps (UWP) and Office, it retrieves the unique **AppUserModelID** (like `5319275A.WhatsAppDesktop_...!App` or `Microsoft.Excel_...`) and launches it properly via the Windows Shell. This fixes issues where the app executable might not be in the system PATH.

### 3. **File Support**

Can open any file with its default app:
- **Documents**: .pdf, .docx, .xlsx, .txt
- **Images**: .jpg, .png, .gif
- **Videos**: .mp4, .mkv, .avi
- **Code**: .py, .js, .java, .cpp
- **Any file**: Uses Windows file association

---

## ⚡ Speed Optimization

### Common Apps (Instant)
These open immediately without search:
- notepad, calculator, paint
- explorer, cmd, powershell, terminal
- edge, word, excel, powerpoint, outlook

### Cached Apps (Fast)
Once you open an app, it's cached for instant future access.

### New Apps (Slower)
First-time searches may take 1-2 seconds as it scans your PC.

---

## 📝 Command Formats

All these work:

```
✅ open notepad
✅ Open Notepad
✅ OPEN NOTEPAD
✅ open "Notepad"
✅ open note          (fuzzy match)
```

### Full Paths
```
✅ open C:\path\to\file.txt
✅ open "C:\My Documents\file.pdf"
```

---

## 🎯 What Gets Searched

### Application Types
- `.exe` - Executable files
- `.lnk` - Shortcuts
- `.bat` - Batch files

### Search Locations
1. `C:\ProgramData\Microsoft\Windows\Start Menu\Programs`
2. `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs`
3. `C:\Program Files`
4. `C:\Program Files (x86)`
5. `%USERPROFILE%\AppData\Local\Programs`
6. `%USERPROFILE%\AppData\Roaming`
7. `C:\Windows\System32`
8. `%USERPROFILE%\Desktop`

---

## 🛠️ Advanced Usage

### Clear Cache (if app moved/deleted)
```python
from automations.universal_launcher import clear_cache
clear_cache()
```

### Direct API Call
```python
from automations.universal_launcher import open_app_or_file

result = open_app_or_file("spotify")
print(result)  # ✅ Opened 'spotify'
```

---

## 🐛 Troubleshooting

### "Could not find 'AppName'"

**Solutions**:
1. Try fuzzy matching: "open spot" instead of "open spotify"
2. Use full path: "open C:\Program Files\Spotify\Spotify.exe"
3. Clear cache and retry
4. Check if app is actually installed

### Slow First Search

**Normal**: First-time searches scan your entire PC
**Solution**: Common apps and cached apps are instant

### Multiple Apps Found

The system picks the **first match** found. To be specific:
- Use more characters: "open discord" not "open disc"
- Use full path for exact control

---

## 📊 Performance

| Scenario | Speed | Details |
|----------|-------|---------|
| Common apps (notepad, calc) | Instant | Hardcoded paths |
| Cached apps | Instant | From cache file |
| First-time search | 1-2 sec | Full PC scan |
| File paths | Instant | Direct open |

---

## 💡 Tips

### Make Your Favorites Instant
Open them once, they'll be cached forever (until you clear cache or move the app).

### Use Short Names
- "open note" works for Notepad
- "open calc" works for Calculator
- "open spot" might work for Spotify

### Files Work Too
- "open report.pdf" (if in current directory)
- "open C:\path\to\file.txt" (full path)

---

## 🔮 Future Enhancements

Planned features:
- [ ] Alias support ("open browser" → "open chrome")
- [ ] Recently used apps list
- [ ] App categories (browsers, editors, etc.)
- [ ] Voice app names ("open Chrome browser")
- [ ] Multi-instance handling

---

## ✅ Testing Checklist

Try these commands in your popup:

- [ ] `open notepad`
- [ ] `open calculator`
- [ ] `open spotify` (if installed)
- [ ] `open discord` (if installed)
- [ ] `open word` (if Office installed)
- [ ] `open C:\path\to\file.txt` (any file)
- [ ] `open desktop` (opens explorer at desktop)

---

**Now you can open ANYTHING with a simple voice command!** 🎉

Just say:
> "Open [app name]"

And it works! ✨
