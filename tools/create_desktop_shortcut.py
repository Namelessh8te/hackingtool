#!/usr/bin/env python3
"""
Create desktop shortcuts for HackingTool GUI Manager.
Run with: python3 tools/create_desktop_shortcut.py
Supports Linux (XDG), macOS, and Windows.
"""

import os
import sys
import platform
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import APP_INSTALL_DIR, VERSION_DISPLAY


class DesktopShortcutCreator:
    """Create desktop shortcuts for different operating systems."""
    
    def __init__(self):
        self.system = platform.system()
        self.gui_script = Path(__file__).parent / "tool_manager_gui.py"
        self.icon_path = Path(__file__).parent.parent / "images" / "logo.svg"
        
    def create_linux_shortcut(self) -> bool:
        """Create .desktop file for Linux (XDG)."""
        print("🐧 Creating Linux desktop shortcut...")
        
        # Use XDG_DESKTOP_DIR if available, otherwise use ~/Desktop
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "hackingtool-gui.desktop"
        
        # Get the python executable path
        python_exe = sys.executable
        gui_script_abs = self.gui_script.resolve()
        
        # Create desktop entry
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=HackingTool Manager GUI
Comment=All-in-One Security Research Framework Manager
Exec={python_exe} {gui_script_abs}
Icon={self.icon_path.resolve() if self.icon_path.exists() else 'utilities-terminal'}
Categories=Development;Utility;
Terminal=false
StartupNotify=true
Keywords=hackingtool;security;tools;manager;
"""
        
        try:
            desktop_file.write_text(desktop_content)
            # Make it executable
            os.chmod(desktop_file, 0o755)
            print(f"✅ Desktop shortcut created: {desktop_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to create desktop shortcut: {e}")
            return False

    def create_macos_shortcut(self) -> bool:
        """Create .app bundle for macOS."""
        print("🍎 Creating macOS app shortcut...")
        
        app_dir = Path.home() / "Applications" / "HackingTool Manager.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        try:
            # Create directories
            macos_dir.mkdir(parents=True, exist_ok=True)
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            # Create launcher script
            launcher = macos_dir / "launcher"
            python_exe = sys.executable
            gui_script_abs = self.gui_script.resolve()
            
            launcher_content = f"""#!/bin/bash
{python_exe} {gui_script_abs}
"""
            launcher.write_text(launcher_content)
            os.chmod(launcher, 0o755)
            
            # Create Info.plist
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.hackingtool.manager</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>HackingTool Manager</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{VERSION_DISPLAY}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
"""
            plist_file = contents_dir / "Info.plist"
            plist_file.write_text(plist_content)
            
            print(f"✅ macOS app bundle created: {app_dir}")
            print(f"   You can now launch it from Spotlight or Applications folder")
            return True
        except Exception as e:
            print(f"❌ Failed to create macOS app: {e}")
            return False

    def create_windows_shortcut(self) -> bool:
        """Create .lnk shortcut for Windows."""
        print("🪟 Creating Windows shortcut...")
        
        try:
            import win32com.client
        except ImportError:
            print("⚠️  pywin32 not installed. Installing...")
            os.system(f"{sys.executable} -m pip install pywin32")
            try:
                import win32com.client
            except ImportError:
                print("❌ Failed to install pywin32. Creating batch file instead...")
                return self.create_windows_batch_shortcut()
        
        desktop_dir = Path.home() / "Desktop"
        shortcut_path = desktop_dir / "HackingTool Manager GUI.lnk"
        
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            python_exe = sys.executable
            gui_script = self.gui_script.resolve()
            
            shortcut.Targetpath = python_exe
            shortcut.Arguments = f'"{gui_script}"'
            shortcut.WorkingDirectory = str(self.gui_script.parent)
            shortcut.IconLocation = str(self.icon_path.resolve() if self.icon_path.exists() else python_exe)
            shortcut.Description = "HackingTool Manager GUI - All-in-One Security Research Framework"
            shortcut.save()
            
            print(f"✅ Windows shortcut created: {shortcut_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create Windows shortcut: {e}")
            return self.create_windows_batch_shortcut()

    def create_windows_batch_shortcut(self) -> bool:
        """Create batch file launcher for Windows."""
        print("📝 Creating Windows batch launcher...")
        
        desktop_dir = Path.home() / "Desktop"
        batch_file = desktop_dir / "HackingTool Manager GUI.bat"
        
        try:
            python_exe = sys.executable
            gui_script = self.gui_script.resolve()
            
            batch_content = f"""@echo off
"{python_exe}" "{gui_script}"
pause
"""
            batch_file.write_text(batch_content)
            print(f"✅ Windows batch launcher created: {batch_file}")
            print(f"   Right-click on it and create a shortcut for your taskbar/start menu")
            return True
        except Exception as e:
            print(f"❌ Failed to create batch file: {e}")
            return False

    def create_systemd_service(self) -> bool:
        """Create systemd service file for auto-start (optional)."""
        print("🔧 Creating systemd service file...")
        
        service_dir = Path.home() / ".config" / "systemd" / "user"
        service_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = service_dir / "hackingtool-gui.service"
        
        python_exe = sys.executable
        gui_script_abs = self.gui_script.resolve()
        
        service_content = f"""[Unit]
Description=HackingTool Manager GUI
After=display-manager.service

[Service]
Type=simple
ExecStart={python_exe} {gui_script_abs}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical-session.target
"""
        
        try:
            service_file.write_text(service_content)
            print(f"✅ Systemd service created: {service_file}")
            print(f"   Enable with: systemctl --user enable hackingtool-gui.service")
            print(f"   Start with: systemctl --user start hackingtool-gui.service")
            return True
        except Exception as e:
            print(f"⚠️  Failed to create systemd service: {e}")
            return False

    def create_menu_entry(self) -> bool:
        """Create application menu entry (XDG Applications)."""
        if self.system != "Linux":
            return False
        
        print("📂 Creating application menu entry...")
        
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = apps_dir / "hackingtool-gui.desktop"
        
        python_exe = sys.executable
        gui_script_abs = self.gui_script.resolve()
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=HackingTool Manager
Comment=All-in-One Security Research Framework Manager
Exec={python_exe} {gui_script_abs}
Icon={self.icon_path.resolve() if self.icon_path.exists() else 'utilities-terminal'}
Categories=Development;Utility;
Terminal=false
StartupNotify=true
Keywords=hackingtool;security;tools;manager;
"""
        
        try:
            desktop_file.write_text(desktop_content)
            os.chmod(desktop_file, 0o644)
            print(f"✅ Menu entry created: {desktop_file}")
            return True
        except Exception as e:
            print(f"⚠️  Failed to create menu entry: {e}")
            return False

    def run(self):
        """Create appropriate shortcuts for the current OS."""
        print(f"\n{'='*60}")
        print(f"🛠️  HackingTool Desktop Shortcut Creator {VERSION_DISPLAY}")
        print(f"{'='*60}\n")
        
        # Check if GUI script exists
        if not self.gui_script.exists():
            print(f"❌ GUI script not found: {self.gui_script}")
            return False
        
        success = False
        
        if self.system == "Linux":
            print("Detected Linux system\n")
            success = self.create_linux_shortcut()
            self.create_menu_entry()
            print("\n📌 Optional: Create systemd service for auto-start?")
            if input("Create systemd service? (y/n): ").lower() == 'y':
                self.create_systemd_service()
        
        elif self.system == "Darwin":
            print("Detected macOS system\n")
            success = self.create_macos_shortcut()
        
        elif self.system == "Windows":
            print("Detected Windows system\n")
            success = self.create_windows_shortcut()
        
        else:
            print(f"❌ Unsupported operating system: {self.system}")
            return False
        
        print(f"\n{'='*60}")
        if success:
            print("✅ Desktop shortcut creation completed!")
            print(f"\n🚀 You can now launch HackingTool Manager GUI from:")
            if self.system == "Linux":
                print("   • Desktop (double-click)")
                print("   • Application menu")
                print("   • Activities search")
            elif self.system == "Darwin":
                print("   • Applications folder")
                print("   • Spotlight (Cmd+Space)")
            elif self.system == "Windows":
                print("   • Desktop")
                print("   • Start menu")
        else:
            print("⚠️  Some errors occurred during shortcut creation")
        print(f"{'='*60}\n")
        
        return success


if __name__ == "__main__":
    creator = DesktopShortcutCreator()
    sys.exit(0 if creator.run() else 1)
