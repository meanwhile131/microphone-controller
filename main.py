import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget
import matplotlib.pyplot as plt
import pyaudio
from fft_plot import FFTPlot
from note_table import NoteTable

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        bindings = {}
        layout = QVBoxLayout()

        portaudio = pyaudio.PyAudio()
        plt.ion()
        self.fft_plot = FFTPlot(bindings, portaudio)
        note_table = NoteTable(bindings)

        layout.addWidget(note_table, 1)
        layout.addWidget(self.fft_plot, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def stop(self):
        self.fft_plot.stop_thread()


window = MainWindow()
window.show()
app.exec()
window.stop()
