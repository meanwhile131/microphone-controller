import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QSlider, QHBoxLayout
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

        threshold_slider = QSlider()
        threshold_slider.setMaximum(40)

        self.binding_handler = AudioBindingHandler(portaudio, threshold_slider)
        note_table = NoteTable(self.binding_handler.bindings)
        layout.addWidget(note_table, 1)

        plot_layout = QHBoxLayout()
        layout.addLayout(plot_layout)

        self.fft_plot = FFTPlot(
            self.binding_handler.window_length, self.binding_handler.sample_rate)
        self.binding_handler.cells_update_callback = note_table.set_highlighted_cells
        self.binding_handler.fft_update_signal.connect(self.fft_plot.update_plot)
        threshold_slider.valueChanged.connect(self.fft_plot.update_threshold)
        plot_layout.addWidget(self.fft_plot, 1)

        plot_layout.addWidget(threshold_slider)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def stop(self):
        self.binding_handler.stop_thread()


def main():
    window = MainWindow()
    window.show()
    app.exec()
    window.stop()


if __name__ == "__main__":
    main()
