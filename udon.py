import sys
import subprocess
import time
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal


# Thread for device monitoring
class DeviceMonitor(QThread):
    device_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.monitor_active = True
        self.device_detected = False

    def run(self):
        while self.monitor_active:
            self.check_device()
            time.sleep(1)

    def check_device(self):
        try:
            result = subprocess.run(["./assets/odin4", "-l"], capture_output=True, text=True, timeout=1)
            output = result.stdout.strip()
            if output and "List of known devices" not in output:
                if not self.device_detected:
                    self.device_detected = True
                    self.device_signal.emit("Added!\n")
            else:
                if self.device_detected:
                    self.device_detected = False
                    self.device_signal.emit("Removed!\n")
        except:
            if self.device_detected:
                self.device_detected = False
                self.device_signal.emit("Removed!\n")


# Thread for running Odin4 commands
class CommandRunner(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        skip_initial_lines = True

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if skip_initial_lines:
                    if "Setup Connection" in output:
                        skip_initial_lines = False
                    continue
                if "/dev/bus/usb/" in output:
                    continue
                output = output.replace(".lz4", "")
                # Progress parsing
                if "(" in output and "%)" in output:
                    try:
                        progress = int(output.split("(")[1].split("%)")[0])
                        self.progress_signal.emit(progress)
                        continue
                    except:
                        pass
                self.log_signal.emit(output)
        self.finished_signal.emit()


#Main window
class Udon(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("assets/Udon.ui", self)  # Load your original .ui file

        # Connect file buttons
        self.APOpenButton.clicked.connect(lambda: self.browse_file(self.APPath))
        self.BLOpenButton.clicked.connect(lambda: self.browse_file(self.BLPath))
        self.CPOpenButton.clicked.connect(lambda: self.browse_file(self.CPPath))
        self.CSCOpenButton.clicked.connect(lambda: self.browse_file(self.CSCPath))

        # Connect main buttons
        self.StartButton.clicked.connect(self.start_flasher)
        self.RebootButton.clicked.connect(self.reboot_device)
        self.RebootDownloadButton.clicked.connect(self.reboot_download_device)

        # Device monitoring
        self.monitor_thread = DeviceMonitor()
        self.monitor_thread.device_signal.connect(self.log_output)
        self.monitor_thread.start()

        self.command_thread = None

        # Make text box read only and stuff
        self.plainTextEdit.setReadOnly(True)
        self.progressBar.setValue(0)
        self.setWindowTitle("Udon4Odin")


    # File selection dialog
    def browse_file(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            line_edit.setText(path)

    # Flashing
    def start_flasher(self):
        ap = self.APPath.text()
        bl = self.BLPath.text()
        cp = self.CPPath.text()
        csc = self.CSCPath.text()
        no_reboot = self.NoRebootCheckBox.isChecked()

        if not any([ap, bl, cp, csc]):
            self.log_output("Error: Select at least one file.\n")
            return

        command = ["pkexec", "./assets/odin4"]
        if ap: command.extend(["-a", ap])
        if bl: command.extend(["-b", bl])
        if cp: command.extend(["-c", cp])
        if csc: command.extend(["-s", csc])
        if no_reboot: command.append("--no-reboot")

        self.start_command(command)

    # Reboot
    def reboot_device(self):
        self.start_command(["pkexec", "./assets/odin4", "--reboot"])

    # Reboot Download
    def reboot_download_device(self):
        self.start_command(["pkexec", "./assets/odin4", "--redownload"])

    # Start command thread
    def start_command(self, command):
        if self.command_thread and self.command_thread.isRunning():
            self.log_output("A command is already running.\n")
            return

        self.progressBar.setValue(0)
        self.StartButton.setEnabled(False)
        self.command_thread = CommandRunner(command)
        self.command_thread.log_signal.connect(self.log_output)
        self.command_thread.progress_signal.connect(self.progressBar.setValue)
        self.command_thread.finished_signal.connect(lambda: self.StartButton.setEnabled(True))
        self.command_thread.start()

    # Logging helper
    def log_output(self, text):
        self.plainTextEdit.appendPlainText(text.strip())

    # Cleanup on close
    def closeEvent(self, event):
        self.monitor_thread.monitor_active = False
        if self.command_thread:
            self.command_thread.quit()
        event.accept()


# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Udon()
    window.show()
    sys.exit(app.exec())
