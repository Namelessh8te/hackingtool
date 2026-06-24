#!/usr/bin/env python3
"""
GUI version of tool manager using PyQt6 for cross-platform compatibility.
Run with: python3 tools/tool_manager_gui.py
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QDialog, QMessageBox, QTabWidget,
    QGroupBox, QFormLayout, QComboBox, QCheckBox, QSpinBox, QProgressBar,
    QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import APP_INSTALL_DIR, APP_BIN_PATH, USER_CONFIG_DIR, REPO_URL


class CommandExecutor(QThread):
    """Run shell commands in a background thread to avoid freezing the GUI."""
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)  # exit code

    def __init__(self, command: str):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.stdout:
                self.output_signal.emit(result.stdout)
            if result.stderr:
                self.error_signal.emit(result.stderr)
            self.finished_signal.emit(result.returncode)
        except subprocess.TimeoutExpired:
            self.error_signal.emit("⚠️  Command timed out after 5 minutes")
            self.finished_signal.emit(1)
        except Exception as e:
            self.error_signal.emit(f"❌ Error: {str(e)}")
            self.finished_signal.emit(1)


class UpdateDialog(QDialog):
    """Dialog for updating system or hackingtool."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Tool or System")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.executor: Optional[CommandExecutor] = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Update Options")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Buttons
        button_layout = QHBoxLayout()
        
        update_sys_btn = QPushButton("🔄 Update System")
        update_sys_btn.clicked.connect(self.update_system)
        update_sys_btn.setMinimumHeight(50)
        button_layout.addWidget(update_sys_btn)

        update_ht_btn = QPushButton("🔄 Update Hackingtool")
        update_ht_btn.clicked.connect(self.update_hackingtool)
        update_ht_btn.setMinimumHeight(50)
        button_layout.addWidget(update_ht_btn)

        layout.addLayout(button_layout)

        # Output text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier", 9))
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_text)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(0)  # Indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def update_system(self):
        self.output_text.clear()
        self.output_text.append("🔄 Fetching package manager...\n")
        
        try:
            from os_detect import CURRENT_OS, PACKAGE_UPDATE_CMDS
            mgr = CURRENT_OS.pkg_manager
            cmd = PACKAGE_UPDATE_CMDS.get(mgr)
            
            if cmd:
                priv = "" if (CURRENT_OS.system == "macos" or os.geteuid() == 0) else "sudo "
                full_cmd = f"{priv}{cmd}"
                self.execute_command(full_cmd)
            else:
                QMessageBox.warning(self, "Error", "Unknown package manager. Please update manually.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to detect OS: {str(e)}")

    def update_hackingtool(self):
        self.output_text.clear()
        
        if not APP_INSTALL_DIR.exists():
            QMessageBox.warning(
                self, "Error",
                f"Install directory not found: {APP_INSTALL_DIR}\nRun install.py first."
            )
            return

        self.output_text.append(f"🔄 Pulling latest code from {REPO_URL}...\n")
        
        cmd = f'cd "{APP_INSTALL_DIR}" && git pull --rebase'
        self.execute_command(cmd)

    def execute_command(self, command: str):
        self.progress.setVisible(True)
        self.executor = CommandExecutor(command)
        self.executor.output_signal.connect(self.append_output)
        self.executor.error_signal.connect(self.append_error)
        self.executor.finished_signal.connect(self.on_finished)
        self.executor.start()

    def append_output(self, text: str):
        self.output_text.append(f"✓ {text}")

    def append_error(self, text: str):
        self.output_text.append(f"✗ {text}")
        # Style error text
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

    def on_finished(self, exit_code: int):
        self.progress.setVisible(False)
        if exit_code == 0:
            self.output_text.append("\n✅ Update completed successfully!")
            QMessageBox.information(self, "Success", "Update completed successfully!")
        else:
            self.output_text.append(f"\n❌ Update failed with exit code {exit_code}")


class UninstallDialog(QDialog):
    """Dialog for uninstalling hackingtool."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Uninstall HackingTool")
        self.setGeometry(100, 100, 500, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Warning message
        warning_label = QLabel("⚠️  This will remove hackingtool from your system.")
        warning_font = QFont()
        warning_font.setPointSize(11)
        warning_font.setBold(True)
        warning_label.setFont(warning_font)
        layout.addWidget(warning_label)

        # Checkboxes
        self.remove_data_cb = QCheckBox("Also remove user data at ~/.hackingtool/")
        layout.addWidget(self.remove_data_cb)

        # Info text
        info = QTextEdit()
        info.setReadOnly(True)
        info.setText(
            f"The following will be removed:\n"
            f"• Install directory: {APP_INSTALL_DIR}\n"
            f"• Launcher: {APP_BIN_PATH}\n"
            f"• User config (optional): {USER_CONFIG_DIR}"
        )
        layout.addWidget(info)

        # Buttons
        button_layout = QHBoxLayout()
        
        uninstall_btn = QPushButton("🗑️  Uninstall")
        uninstall_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        uninstall_btn.clicked.connect(self.confirm_uninstall)
        button_layout.addWidget(uninstall_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def confirm_uninstall(self):
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            "Are you sure you want to uninstall hackingtool? This cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.perform_uninstall()

    def perform_uninstall(self):
        import shutil
        
        try:
            # Remove install directory
            if APP_INSTALL_DIR.exists():
                shutil.rmtree(str(APP_INSTALL_DIR))
                QMessageBox.information(self, "Success", f"Removed {APP_INSTALL_DIR}")
            
            # Remove launcher
            if APP_BIN_PATH.exists():
                APP_BIN_PATH.unlink()
                QMessageBox.information(self, "Success", f"Removed launcher {APP_BIN_PATH}")
            
            # Remove user data if checked
            if self.remove_data_cb.isChecked():
                shutil.rmtree(str(USER_CONFIG_DIR), ignore_errors=True)
                QMessageBox.information(self, "Success", f"Removed {USER_CONFIG_DIR}")
            
            QMessageBox.information(
                self, "Complete",
                "Hackingtool has been successfully uninstalled!"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Uninstall failed: {str(e)}")


class ToolManagerGUI(QMainWindow):
    """Main GUI window for HackingTool Manager."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️  HackingTool Manager — v2.0.0")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()

        # Header
        header = QLabel("Update or Uninstall | Hackingtool")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        
        # Update Tab
        update_widget = self.create_update_tab()
        tabs.addTab(update_widget, "🔄 Update")
        
        # Uninstall Tab
        uninstall_widget = self.create_uninstall_tab()
        tabs.addTab(uninstall_widget, "🗑️  Uninstall")
        
        # Info Tab
        info_widget = self.create_info_tab()
        tabs.addTab(info_widget, "ℹ️  Info")
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)

    def create_update_tab(self) -> QWidget:
        """Create the update tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Group box
        group = QGroupBox("System Updates")
        group_layout = QFormLayout()

        # Update system
        sys_btn = QPushButton("🔄 Update System Packages")
        sys_btn.setMinimumHeight(50)
        sys_btn.clicked.connect(self.show_update_dialog)
        group_layout.addRow("System:", sys_btn)

        # Update hackingtool
        ht_btn = QPushButton("🔄 Update Hackingtool")
        ht_btn.setMinimumHeight(50)
        ht_btn.clicked.connect(lambda: self.run_update_ht())
        group_layout.addRow("Hackingtool:", ht_btn)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Info box
        info_box = QGroupBox("Update Information")
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "System Update:\n"
            "• Updates all installed packages on your system\n"
            "• Requires sudo/root privileges on Linux\n"
            "• Automatically detects your package manager\n\n"
            "Hackingtool Update:\n"
            "• Pulls the latest code from the repository\n"
            f"• Repository: {REPO_URL}\n"
            f"• Installation directory: {APP_INSTALL_DIR}\n"
            "• Re-installs dependencies from requirements.txt"
        )
        info_layout.addWidget(info_text)
        info_box.setLayout(info_layout)
        layout.addWidget(info_box)

        widget.setLayout(layout)
        return widget

    def create_uninstall_tab(self) -> QWidget:
        """Create the uninstall tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Warning
        warning_label = QLabel("⚠️  Uninstall Hackingtool")
        warning_font = QFont()
        warning_font.setPointSize(12)
        warning_font.setBold(True)
        warning_label.setFont(warning_font)
        layout.addWidget(warning_label)

        # Button
        uninstall_btn = QPushButton("🗑️  Uninstall Hackingtool")
        uninstall_btn.setMinimumHeight(60)
        uninstall_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold; font-size: 14px;")
        uninstall_btn.clicked.connect(self.show_uninstall_dialog)
        layout.addWidget(uninstall_btn)

        # Info
        info_box = QGroupBox("What will be removed?")
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            f"Install directory:\n{APP_INSTALL_DIR}\n\n"
            f"Launcher:\n{APP_BIN_PATH}\n\n"
            f"User configuration (optional):\n{USER_CONFIG_DIR}\n\n"
            "You will be asked before each removal."
        )
        info_layout.addWidget(info_text)
        info_box.setLayout(info_layout)
        layout.addWidget(info_box)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_info_tab(self) -> QWidget:
        """Create the information tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "🛠️  HackingTool Manager GUI v2.0.0\n\n"
            "All-in-One Security Research Framework\n\n"
            "Features:\n"
            "• 🔄 Easy system and tool updates\n"
            "• 🗑️  Safe uninstallation process\n"
            "• 🎯 Cross-platform support\n"
            "• 🔐 Security-focused tools collection\n\n"
            f"Repository: {REPO_URL}\n"
            f"Installation: {APP_INSTALL_DIR}\n"
            f"Configuration: {USER_CONFIG_DIR}\n\n"
            "© 2024 HackingTool Contributors"
        )
        layout.addWidget(info_text)
        widget.setLayout(layout)
        return widget

    def show_update_dialog(self):
        """Show the update dialog."""
        dialog = UpdateDialog(self)
        dialog.exec()

    def show_uninstall_dialog(self):
        """Show the uninstall dialog."""
        dialog = UninstallDialog(self)
        dialog.exec()

    def run_update_ht(self):
        """Run hackingtool update."""
        dialog = UpdateDialog(self)
        dialog.update_hackingtool()
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    window = ToolManagerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
