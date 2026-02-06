import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget
import matplotlib.pyplot as plt
import pyaudio
from fft_plot import FFTPlot
from note_table import NoteTable
from binding_handler import AudioBindingHandler

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        portaudio = pyaudio.PyAudio()
        plt.ion()
        self.binding_handler = AudioBindingHandler(portaudio)
        note_table = NoteTable(self.binding_handler.bindings)
        self.fft_plot = FFTPlot(
            self.binding_handler.window_length, self.binding_handler.sample_rate)
        self.binding_handler.cells_update_callback = note_table.set_highlighted_cells
        self.binding_handler.fft_update_callback = self.fft_plot.update_plot

        layout.addWidget(note_table, 1)
        layout.addWidget(self.fft_plot, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def stop(self):
        self.binding_handler.stop_thread()


window = MainWindow()
window.show()
app.exec()
window.stop()
