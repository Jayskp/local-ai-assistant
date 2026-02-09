"""
Modern glassmorphism popup using PyWebView
Beautiful, native Windows UI with HTML/CSS - PyInstaller compatible!
"""

import webview
import sys
from core.commands import parse_fast
from core.llm_parser import answer_with_llm
from core.executor import execute_command
from memory.logger import log_command, get_recent_history


# Global window reference
_window = None


class AIAssistantAPI:
    """Backend API for the webview popup"""
    
    def __init__(self):
        self.pending_action = None  # Store action pending confirmation
    
    def execute_command(self, command):
        """Execute a user command"""
        print(f"[API] execute_command called with: {command}")
        result = {"status": "success", "message": "", "needs_confirmation": False}
        
        try:
            # Try fast parsing first
            actions = parse_fast(command)
            
            # Keyword mapping fallback
            if actions is None:
                actions = self._keyword_map(command)
            
            # Execute actions
            if actions:
                last_result = ""
                for action in actions:
                    exec_result = execute_command(action)
                    last_result = exec_result
                    
                    # Check if confirmation is needed
                    if "Pending confirmation" in last_result:
                        self.pending_action = action
                        result["needs_confirmation"] = True
                        result["status"] = "pending"
                        result["message"] = self._format_confirmation_message(action)
                        return result
                
                result["message"] = last_result
                log_command(command, actions)
            else:
                # Q&A fallback
                answer = answer_with_llm(command)
                result["message"] = answer
                log_command(command, [{"type": "answer", "action": "answer", "params": {}}])
                
        except Exception as e:
            result = {"status": "error", "message": str(e)}
        
        return result
    
    def execute_with_confirmation(self, confirmed):
        """Execute pending action with user confirmation"""
        print(f"[API] execute_with_confirmation called with: {confirmed}")
        
        if not self.pending_action:
            return {"status": "error", "message": "No pending action"}
        
        if not confirmed:
            self.pending_action = None
            return {"status": "cancelled", "message": "Action cancelled"}
        
        # Set confirm=True and execute
        action = self.pending_action
        action["params"]["confirm"] = True
        
        try:
            result_message = execute_command(action)
            self.pending_action = None
            return {"status": "success", "message": result_message}
        except Exception as e:
            self.pending_action = None
            return {"status": "error", "message": str(e)}
    
    def _format_confirmation_message(self, action):
        """Format a user-friendly confirmation message"""
        change = action.get("params", {}).get("change", "unknown")
        
        messages = {
            "flush_dns": "Clear DNS cache? This will reset DNS resolver cache.",
            "winsock_reset": "Reset network stack? This requires administrator privileges and may require a restart.",
            "power_plan_high": "Switch to High Performance mode? This will increase power consumption.",
            "power_plan_balanced": "Switch to Balanced mode? This balances performance and power consumption.",
            "power_plan_low": "Switch to Power Saver mode? This will reduce performance to save battery.",
            "clean_temp_files": "Delete all temporary files? This will free up disk space by removing files from temp folders.",
            "wifi_off": "Disable Wi-Fi? You will lose wireless network connectivity.",
            "wifi_on": "Enable Wi-Fi? This will turn on wireless connectivity.",
            "check_windows_updates": "Open Windows Update settings?",
            "disk_cleanup": "Run Disk Cleanup tool? This will help free up disk space.",
        }
        
        return messages.get(change, f"Apply change: {change}?")
    
    def get_history(self):
        """Get recent command history"""
        print("[API] get_history called")
        history = get_recent_history(limit=10)
        commands = []
        seen = set()
        for entry in reversed(history):
            cmd = entry.get("command", "")
            if cmd and cmd not in seen:
                seen.add(cmd)
                commands.append(cmd)
            if len(commands) >= 6:
                break
        return commands
    
    def close_window(self):
        """Close the popup window"""
        print("[API] close_window called")
        try:
            global _window
            if _window:
                _window.destroy()
            # Fallback to exit
            sys.exit(0)
        except Exception as e:
            print(f"[API] Error closing: {e}")
            sys.exit(0)
    
    def minimize_window(self):
        """Minimize the popup window"""
        print("[API] minimize_window called")
        try:
            global _window
            if _window:
                _window.minimize()
                return {"status": "success"}
        except Exception as e:
            print(f"[API] Error minimizing: {e}")
        return {"status": "error", "message": "Minimize not available"}
    
    def _keyword_map(self, command):
        """Map common keywords to actions without LLM"""
        lowered = command.lower()
        actions = []
        
        if "system info" in lowered or "system information" in lowered or "my system" in lowered:
            actions.append({"type": "system", "action": "system_info", "params": {}})
        if "network" in lowered or "internet" in lowered:
            actions.append({"type": "system", "action": "network_info", "params": {}})
        if "slow" in lowered or "lag" in lowered or "performance" in lowered:
            actions.append({"type": "system", "action": "optimize_performance", "params": {"confirm": False}})
        
        return actions if actions else None


def get_html():
    """Generate the HTML/CSS/JS for the popup"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0c1324 0%, #101a2f 100%);
            height: 100vh;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .glass-card {
            width: 680px;
            height: 520px;
            background: rgba(10, 15, 30, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            padding: 24px;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .title-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .ai-orb {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #7dd3fc;
            box-shadow: 0 0 16px rgba(125, 211, 252, 0.6);
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 8px rgba(125, 211, 252, 0.4); }
            50% { box-shadow: 0 0 20px rgba(125, 211, 252, 0.8); }
        }
        
        h1 {
            color: #e2e8f0;
            font-size: 20px;
            font-weight: 600;
        }
        
        .badge {
            background: #7dd3fc;
            color: #0b1220;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .window-controls {
            display: flex;
            gap: 8px;
        }
        
        .window-btn {
            width: 32px;
            height: 32px;
            border: none;
            background: transparent;
            color: #94a3b8;
            font-size: 18px;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .window-btn:hover {
            background: rgba(125, 211, 252, 0.1);
            color: #7dd3fc;
        }
        
        .input-section {
            margin-bottom: 16px;
        }
        
        .input-label {
            color: #94a3b8;
            font-size: 12px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .history-btn {
            background: transparent;
            border: none;
            color: #64748b;
            font-size: 11px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .history-btn:hover {
            background: rgba(125, 211, 252, 0.1);
            color: #7dd3fc;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        #commandInput {
            width: 100%;
            padding: 18px 20px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(125, 211, 252, 0.15);
            border-radius: 12px;
            color: #e2e8f0;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
        }
        
        #commandInput:focus {
            border-color: #7dd3fc;
            box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.1);
        }
        
        #commandInput::placeholder {
            color: rgba(148, 163, 184, 0.5);
        }
        
        .status {
            text-align: center;
            color: #7dd3fc;
            font-size: 12px;
            margin: 8px 0;
            min-height: 20px;
        }
        
        .details-panel {
            flex: 1;
            background: rgba(15, 23, 42, 0.3);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            overflow-y: auto;
        }
        
        .details-title {
            color: #64748b;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        
        .details-content {
            color: #94a3b8;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .quick-actions {
            margin-bottom: 16px;
        }
        
        .quick-title {
            color: #e2e8f0;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .quick-subtitle {
            color: #64748b;
            font-size: 11px;
            margin-bottom: 12px;
        }
        
        .quick-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .quick-btn {
            padding: 10px 16px;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(125, 211, 252, 0.1);
            border-radius: 8px;
            color: #e2e8f0;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-btn:hover {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(125, 211, 252, 0.3);
            transform: translateY(-2px);
        }
        
        .confirmation-section {
            margin-bottom: 16px;
            padding: 12px;
        }
        
        .confirmation-buttons {
            display: flex;
            gap: 12px;
            justify-content: center;
        }
        
        .confirm-btn {
            padding: 10px 28px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .confirm-yes {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        
        .confirm-yes:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        .confirm-no {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }
        
        .confirm-no:hover {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }
        
        .footer {
            text-align: center;
            color: #64748b;
            font-size: 11px;
        }
        
        .history-dropdown {
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            right: 0;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(125, 211, 252, 0.2);
            border-radius: 8px;
            padding: 8px;
            display: none;
            z-index: 1000;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .history-dropdown.show {
            display: block;
        }
        
        .history-item {
            padding: 8px 12px;
            color: #e2e8f0;
            font-size: 11px;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
        }
        
        .history-item:hover {
            background: rgba(125, 211, 252, 0.2);
        }
    </style>
</head>
<body>
    <div class="glass-card">
        <div class="header">
            <div class="title-section">
                <div class="ai-orb" id="aiOrb"></div>
                <h1>Local AI Assistant</h1>
                <span class="badge">Now</span>
            </div>
            <div class="window-controls">
                <button class="window-btn" onclick="minimizeWindow()">—</button>
                <button class="window-btn" onclick="closeWindow()">✕</button>
            </div>
        </div>
        
        <div class="input-section">
            <div class="input-label">
                <span>What would you like to do?</span>
                <button class="history-btn" onclick="toggleHistory()">
                    <span>📜</span>
                    <span>History</span>
                </button>
            </div>
            <div class="input-wrapper">
                <input type="text" id="commandInput" 
                       placeholder="Ask me to open apps, change settings, or automate your workflow…"
                       onkeypress="handleKeyPress(event)">
                <div class="history-dropdown" id="historyDropdown"></div>
            </div>
        </div>
        
        <div class="status" id="status"></div>
        
        <!-- Confirmation Buttons (hidden by default) -->
        <div class="confirmation-section" id="confirmationSection" style="display: none;">
            <div class="confirmation-buttons">
                <button class="confirm-btn confirm-yes" onclick="handleConfirmation(true)">✓ Yes</button>
                <button class="confirm-btn confirm-no" onclick="handleConfirmation(false)">✕ No</button>
            </div>
        </div>
        
        <div class="details-panel">
            <div class="details-title">Details</div>
            <div class="details-content" id="detailsContent">I'll show what I plan to do here.</div>
        </div>
        
        <div class="quick-actions">
            <div class="quick-title">Quick Actions</div>
            <div class="quick-subtitle">Jump into frequent tasks instantly.</div>
            <div class="quick-buttons">
                <button class="quick-btn" onclick="executeQuick('open chrome')">🌐 Chrome</button>
                <button class="quick-btn" onclick="executeQuick('open vscode')">💻 VS Code</button>
                <button class="quick-btn" onclick="executeQuick('organize downloads')">📁 Organize</button>
                <button class="quick-btn" onclick="executeQuick('system info')">⚡ System</button>
            </div>
        </div>
        
        <div class="footer">
            💡 Press Ctrl+Space to summon  •  ESC to close
        </div>
    </div>
    
    <script>
        const input = document.getElementById('commandInput');
        const status = document.getElementById('status');
        const details = document.getElementById('detailsContent');
        const historyDropdown = document.getElementById('historyDropdown');
        const confirmationSection = document.getElementById('confirmationSection');
        
        // Wait for pywebview API to be ready
        window.addEventListener('pywebviewready', function() {
            console.log('[JS] pywebview API ready');
            input.focus();
        });
        
        // Focus input on load
        window.addEventListener('load', () => {
            setTimeout(() => {
                input.focus();
            }, 100);
        });
        
        // ESC to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeWindow();
            }
        });
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                executeCommand();
            }
        }
        
        async function executeCommand() {
            const command = input.value.trim();
            if (!command) return;
            
            input.disabled =true;
            status.textContent = '⏳ Processing...';
            details.textContent = 'Working on it...';
            confirmationSection.style.display = 'none';  // Hide confirmation buttons
            
            try {
                const result = await pywebview.api.execute_command(command);
                
                if (result.needs_confirmation) {
                    // Show confirmation buttons
                    status.textContent = '❓ Confirmation Required';
                    details.textContent = result.message;
                    confirmationSection.style.display = 'block';
                } else if (result.status === 'success') {
                    status.textContent = '✓ Done';
                    details.textContent = result.message || 'Completed successfully';
                } else {
                    status.textContent = '❌ Error';
                    details.textContent = result.message;
                }
            } catch (error) {
                status.textContent = '❌ Error';
                details.textContent = error.toString();
            } finally {
                input.disabled = false;
                input.focus();
            }
        }
        
        async function handleConfirmation(confirmed) {
            console.log(`[JS] Confirmation: ${confirmed}`);
            confirmationSection.style.display = 'none';
            status.textContent = '⏳ Processing...';
            
            try {
                const result = await pywebview.api.execute_with_confirmation(confirmed);
                
                if (result.status === 'success') {
                    status.textContent = '✓ Done';
                    details.textContent = result.message;
                } else if (result.status === 'cancelled') {
                    status.textContent = '❌ Cancelled';
                    details.textContent = result.message;
                } else {
                    status.textContent = '❌ Error';
                    details.textContent = result.message;
                }
            } catch (error) {
                status.textContent = '❌ Error';
                details.textContent = error.toString();
            }
        }
        
        async function executeQuick(command) {
            input.value = command;
            await executeCommand();
        }
        
        async function toggleHistory() {
            if (historyDropdown.classList.contains('show')) {
                historyDropdown.classList.remove('show');
            } else {
                const history = await pywebview.api.get_history();
                historyDropdown.innerHTML = '';
                
                if (history.length === 0) {
                    historyDropdown.innerHTML = '<div class="history-item" style="opacity: 0.5;">No history yet</div>';
                } else {
                    history.forEach(cmd => {
                        const item = document.createElement('div');
                        item.className = 'history-item';
                        item.textContent = cmd.length > 50 ? cmd.substring(0, 50) + '...' : cmd;
                        item.onclick = () => {
                            input.value = cmd;
                            historyDropdown.classList.remove('show');
                            input.focus();
                        };
                        historyDropdown.appendChild(item);
                    });
                }
                
                historyDropdown.classList.add('show');
            }
        }
        
        function closeWindow() {
            console.log('[JS] Close button clicked');
            pywebview.api.close_window().then(() => {
                console.log('[JS] Close called successfully');
            }).catch(e => {
                console.error('[JS] Close error:', e);
            });
        }
        
        function minimizeWindow() {
            console.log('[JS] Minimize button clicked');
            pywebview.api.minimize_window().then(result => {
                console.log('[JS] Minimize result:', result);
            }).catch(e => {
                console.error('[JS] Minimize error:', e);
            });
        }
        
        // Close history dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-wrapper') && !e.target.closest('.history-btn')) {
                historyDropdown.classList.remove('show');
            }
        });
    </script>
</body>
</html>
    '''


def show_popup():
    """Launch the pywebview glassmorphism popup"""
    global _window
    
    _window = webview.create_window(
        'Local AI Assistant',
        html=get_html(),
        width=680,
        height=520,
        resizable=False,
        frameless=True,
        on_top=True,
        background_color='#0c1324',
        js_api=AIAssistantAPI()
    )
    
    print("[POPUP] Window created, starting webview...")
    webview.start(debug=False)
    print("[POPUP] Webview stopped")


if __name__ == "__main__":
    show_popup()
