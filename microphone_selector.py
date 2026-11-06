from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
import sounddevice as sd


class MicrophoneSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Microphone selection")

        layout = QVBoxLayout()
        self.setLayout(layout)

        microphone_selector = QComboBox()
        layout.addWidget(microphone_selector)
        input_devices = filter(lambda device: device["max_input_channels"] > 0, sd.query_devices())
        for device in input_devices:
            microphone_selector.addItem(device["name"])

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons, self)
        layout.addWidget(self.button_box)
        
        self.button_box.rejected.connect(lambda: self.close())
        self.button_box.accepted.connect(self.lock_in)

    def lock_IN
