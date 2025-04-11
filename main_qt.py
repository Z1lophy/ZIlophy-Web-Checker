import sys
import os
import threading
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QHBoxLayout, QLineEdit, QStackedWidget, QMessageBox, QFileDialog, QFileDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QPixmap, QIcon, QMouseEvent, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from scanner import run_full_scan

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # for PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# =========================
# 🔄 AUTO-UPDATER SETTINGS
# =========================
CURRENT_VERSION = "1.1.0"
UPDATE_URL = "https://github.com/Z1lophy/ZIlophy-Web-Checker"
VERSION_FILE_URL = "https://raw.githubusercontent.com/Z1lophy/ZIlophy-Web-Checker/main/version.txt"

def check_for_update(parent=None):
    try:
        with urllib.request.urlopen(VERSION_FILE_URL, timeout=5) as response:
            latest_version = response.read().decode("utf-8").strip()
        if latest_version != CURRENT_VERSION:
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Update Available")
            msg.setText(f"A new version ({latest_version}) is available!")
            msg.setInformativeText("Would you like to open the download page?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg.exec() == QMessageBox.StandardButton.Yes:
                import webbrowser
                webbrowser.open(UPDATE_URL)
    except Exception as e:
        print("Update check failed:", e)

# =========================
# 🔐 PIN + MAIN APP SCREENS
# =========================

APP_PIN = "1337"

class DraggableStackedWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        self._start_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._start_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._start_pos = None

class BackgroundWidget(QWidget):
    def __init__(self, bg_image_path, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap(bg_image_path))
        self.bg_label.setGeometry(0, 0, width, height)
        self.bg_label.lower()

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(10)

        title = QLabel("ZILOPHY Anti-Cheat")
        title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title)
        layout.addStretch()

        minimize_btn = QPushButton("-")
        minimize_btn.setFixedSize(20, 20)
        minimize_btn.setStyleSheet("background-color: #222; color: white; border: none;")
        minimize_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(minimize_btn)

        close_btn = QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("background-color: #b00020; color: white; border: none;")
        close_btn.clicked.connect(parent.close)
        layout.addWidget(close_btn)

class LoginScreen(BackgroundWidget):
    def __init__(self, stacked_widget):
        super().__init__(resource_path("assets/background.jpg"), 560, 249)
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(CustomTitleBar(stacked_widget))

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setFixedWidth(200)
        self.pin_input.setPlaceholderText("Enter Pin")
        self.pin_input.setStyleSheet("""
            QLineEdit {
                background-color: #111;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 16px;
            }
        """)

        login_btn = QPushButton("Unlock")
        login_btn.setFixedWidth(200)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #d62828;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e63946;
            }
        """)
        login_btn.clicked.connect(self.check_pin)

        center_layout.addWidget(self.pin_input)
        center_layout.addWidget(login_btn)
        layout.addLayout(center_layout)

    def check_pin(self):
        if self.pin_input.text() == APP_PIN:
            widget = self.stacked_widget
            widget.animation = QPropertyAnimation(widget, b"windowOpacity")
            widget.animation.setDuration(600)
            widget.animation.setStartValue(1.0)
            widget.animation.setEndValue(0.0)
            widget.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            def switch_and_restore():
                widget.setCurrentIndex(1)
                widget.setWindowOpacity(0.0)
                fade_in = QPropertyAnimation(widget, b"windowOpacity")
                fade_in.setDuration(600)
                fade_in.setStartValue(0.0)
                fade_in.setEndValue(1.0)
                fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
                fade_in.start()
                widget.fade_in = fade_in

            widget.animation.finished.connect(switch_and_restore)
            widget.animation.start()
        else:
            QMessageBox.critical(self, "Access Denied", "Incorrect PIN.")

class AntiCheatApp(BackgroundWidget):
    def __init__(self, stacked_widget):
        super().__init__(resource_path("assets/background.jpg"), 560, 249)
        self.stacked_widget = stacked_widget
        self.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        layout.addWidget(CustomTitleBar(self.stacked_widget))

        self.output_box = QTextEdit()
        self.output_box.setFont(QFont("Courier", 9))
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("""
        QTextEdit {
            background-color: #111;
            color: white;
            border-radius: 6px;
            padding: 6px;
        }
        QScrollBar:vertical {
            border: none;
            background: #111;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #d62828;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setColor(QColor("#AA3333"))
        shadow.setOffset(0, 0)
        self.output_box.setGraphicsEffect(shadow)
        layout.addWidget(self.output_box)

        button_layout = QHBoxLayout()

        self.scan_button = QPushButton("Run Browser Scan")
        self.scan_button.clicked.connect(self.run_scan)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #d62828;
                color: white;
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e63946;
            }
        """)

        self.save_button = QPushButton("Save Log")
        self.save_button.clicked.connect(self.save_log)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #d62828;
                color: white;
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e63946;
            }
        """)

        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def run_scan(self):
        self.output_box.clear()
        self.output_box.append("🔍 Scanning browsers... Please wait...\n")
        self.scan_button.setEnabled(False)

        def background_task():
            import traceback
            try:
                results = run_full_scan()
                if results:
                    self.output_box.append("\n".join(results))
                else:
                    self.output_box.append("✅ No matches found for target strings.")
            except Exception as e:
                tb = traceback.format_exc()
                self.output_box.append(f"❌ Error during scan:\n{tb}")
                print(tb)
            finally:
                self.scan_button.setEnabled(True)

        threading.Thread(target=background_task, daemon=True).start()

    def save_log(self):
        log = self.output_box.toPlainText()
        if not log.strip():
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log", "scan_results.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(log)

def main():
    app = QApplication(sys.argv)
    stacked_widget = DraggableStackedWidget()
    login_screen = LoginScreen(stacked_widget)
    main_app = AntiCheatApp(stacked_widget)
    stacked_widget.addWidget(login_screen)
    stacked_widget.addWidget(main_app)
    stacked_widget.setCurrentIndex(0)
    stacked_widget.setFixedSize(560, 249)
    stacked_widget.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    stacked_widget.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
    stacked_widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
