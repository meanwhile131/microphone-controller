from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal, QSettings
import sounddevice as sd


class MicrophoneSelectionDialog(QDialog):
    microphone_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Microphone selection")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.microphone_selector = QComboBox()
        layout.addWidget(self.microphone_selector)
        input_devices = filter(lambda device: device["max_input_channels"] > 0, sd.query_devices())
        for device in input_devices:
            self.microphone_selector.addItem(device["name"], device["index"])
        saved = QSettings().value("microphone")
        if saved:
            device = sd.query_devices(saved)
            self.microphone_selector.setCurrentText(device["name"])

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons, self)
        layout.addWidget(self.button_box)

        self.button_box.rejected.connect(lambda: self.close())
        self.button_box.accepted.connect(self.select_microphone)

    def select_microphone(self):
        self.microphone_selected.emit(self.microphone_selector.currentData())
        self.close()
