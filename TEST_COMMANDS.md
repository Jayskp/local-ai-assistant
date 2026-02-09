# Quick Test Commands

Test the new enhancements with these commands in the popup:

## 🔍 Test New Probes

### Storage Diagnostics
```
check disk usage
how much temp storage
show disk space
```

### Network Diagnostics
```
check wifi status
is wifi working
show wifi details
```

### Windows Updates
```
check for windows updates
are there pending updates
show windows update status
```

### Battery Status (Laptops)
```
check battery
what's my battery level
show battery status
```

---

## ⚡ Test New Actions (with Confirmation)

### Storage Cleanup
```
clean temporary files
delete temp files
free up disk space
```
**Expected**: "Delete all temporary files?" [✓ Yes] [✕ No]

### Wi-Fi Control
```
turn off wifi
disable wifi
```
**Expected**: "Disable Wi-Fi?" [✓ Yes] [✕ No]

```
turn on wifi
enable wifi
```
**Expected**: "Enable Wi-Fi?" [✓ Yes] [✕ No]

### Windows Update
```
open windows update
check for updates
```
**Expected**: "Open Windows Update settings?" [✓ Yes] [✕ No]

### Disk Cleanup Tool
```
run disk cleanup
clean up disk
```
**Expected**: "Run Disk Cleanup tool?" [✓ Yes] [✕ No]

---

## 🧠 Test AI Reasoning

### Scenario 1: Slow Computer
```
my computer is running slow
optimize my pc
speed up my computer
```
**Expected**: LLM should:
1. Run cpu_mem probe
2. Run top_processes probe
3. Check temp_files_size
4. Suggest cleanup if temp files are large
5. Show confirmation for any changes

###Scenario 2: Network Issues
```
my internet isn't working
wifi problems
can't connect to internet
```
**Expected**: LLM should:
1. Run wifi_status probe
2. Run ping test
3. Run network_basic probe
4. Suggest wifi_on if disabled
5. Suggest flush_dns or winsock_reset if needed

### Scenario 3: Storage Issues
```
running out of space
disk almost full
need more storage
```
**Expected**: LLM should:
1. Run storage probe
2. Run disk_usage probe
3. Check temp_files_size
4. Suggest clean_temp_files
5. Suggest disk_cleanup

### Scenario 4: Battery Optimization
```
save battery
improve battery life
battery draining fast
```
**Expected**: LLM should:
1. Run battery_status probe
2. Run power_plan probe
3. Suggest power_plan_low
4. Show confirmation before changing

---

## 🎯 Expected Confirmation Messages

| Action | Expected Message |
|--------|------------------|
| clean_temp_files | "Delete all temporary files? This will free up disk space by removing files from temp folders." |
| wifi_off | "Disable Wi-Fi? You will lose wireless network connectivity." |
| wifi_on | "Enable Wi-Fi? This will turn on wireless connectivity." |
| check_windows_updates | "Open Windows Update settings?" |
| disk_cleanup | "Run Disk Cleanup tool? This will help free up disk space." |
| flush_dns | "Clear DNS cache? This will reset DNS resolver cache." |
| winsock_reset | "Reset network stack? This requires administrator privileges and may require a restart." |
| power_plan_high | "Switch to High Performance mode? This will increase power consumption." |
| power_plan_balanced | "Switch to Balanced mode? This balances performance and power consumption." |
| power_plan_low | "Switch to Power Saver mode? This will reduce performance to save battery." |

---

## ✅ UI Testing Checklist

When testing, verify:

- [ ] **Confirmation buttons appear** when action needs confirmation
- [ ] **Yes button is green** with gradient
- [ ] **No button is red** with gradient
- [ ] **Hover effects work** (buttons glow and lift slightly)
- [ ] **Yes executes action** and shows "✓ Done"
- [ ] **No cancels action** and shows "❌ Cancelled"
- [ ] **Buttons disappear** after clicking
- [ ] **Status updates** correctly throughout flow
- [ ] **Error handling** works if action fails

---

## 🐛 Known Issues to Watch For

1. **Admin Privileges**: Some actions (winsock_reset, disk_cleanup) may require admin rights
2. **Wi-Fi Interface Names**: wifi_on/off commands assume interface is named "Wi-Fi" (standard on Windows)
3. **Windows Update Automation**: COM-based update check may require specific permissions
4. **Battery Status**: Only works on laptops (desktops won't have battery info)

---

## 🔄 To Test in Exe Mode

1. Rebuild the executable:
```powershell
.\build.ps1
```

2. Run the exe:
```powershell
cd dist\main
.\main.exe
```

3. Press Ctrl+Space to open popup

4. Test any of the commands above

---

**Happy Testing!** 🚀
