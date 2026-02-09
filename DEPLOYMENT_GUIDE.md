# Quick Deployment Guide

## Build Both Executables

### 1. Build Main App
```powershell
cd "C:\Users\Admin\Personalized Local AI Assistant for Windows (Privacy-First, Modular LLM Orchestrator)\local-ai-assistant"
pyinstaller main.spec
```
**Output**: `dist\main\main.exe` (+ supporting files in `dist\main\`)

### 2. Build Popup
```powershell
pyinstaller popup.spec
```
**Output**: `dist\popup.exe`

### 3. Copy Popup to Main Directory
```powershell
Copy-Item "dist\popup.exe" -Destination "dist\main\popup.exe" -Force
```

## Deploy to Users

Distribute the entire `dist\main\` folder, which now contains:
```
dist/main/
├── main.exe          # Main application
├── popup.exe         # Popup window executable
├── _internal/        # Supporting DLLs and dependencies
└── (other files)
```

## User Instructions

1. **Extract** the `main` folder to any location
2. **Run** `main.exe`
3. **System tray icon** appears (may be hidden - check overflow)
4. **Press** `Ctrl+Space` to open the AI assistant popup
5. **Type** commands and press Enter

## How to Use the Assistant

### Quick Actions (Click buttons)
- 🌐 **Chrome** - Opens Google Chrome
- 💻 **VS Code** - Opens Visual Studio Code
- 📁 **Organize** - Organizes downloads folder
- ⚡ **System** - Shows system information

### Custom Commands (Type in input field)
- "open notepad"
- "what is my IP address"
- "clean temporary files"
- "show system info"

### Hotkeys
- **Ctrl+Space** - Open popup from anywhere
- **Enter** - Execute command
- **ESC** - Close popup
- **✕ button** - Close popup
- **— button** - Minimize popup

## Testing the Build

### Test Popup Directly
```powershell
cd dist\main
.\popup.exe
```
Should open the glassmorphism popup window.

### Test Full Integration
```powershell
cd dist\main
.\main.exe
# Wait 2-3 seconds for initialization
# Press Ctrl+Space
```
Popup should appear when you press Ctrl+Space.

### Test Tray Icon
1. Run `main.exe`
2. Find system tray icon
3. Right-click → "Open Assistant"
4. Popup should appear

## Troubleshooting

### Popup doesn't appear
- Check if `popup.exe` exists in the same folder as `main.exe`
- Run `popup.exe` directly to test
- Check `startup_error.log` for errors

### Ctrl+Space doesn't work
- Check if another app is using Ctrl+Space
- Try clicking tray icon → "Open Assistant"
- Check if main app is running (look for tray icon)

### Close button doesn't work
- Press ESC key instead
- Check console for JavaScript errors
- Verify you rebuilt popup.exe after fixing the code

## File Sizes (Approximate)
- `main.exe`: ~20-30 MB
- `popup.exe`: ~15-20 MB
- Total distribution: ~50-80 MB

## Requirements
- **Windows 11** (for Edge WebView2, built-in)
- **Windows 10** may need WebView2 Runtime installed
- No Python installation required for end users

---

**All set!** 🎉 Your AI Assistant is ready for production use.
