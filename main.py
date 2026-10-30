import sys
from PySide6.QtCore import Qt, QStandardPaths, QCoreApplication, QSettings, Signal
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QSlider, QHBoxLayout
import matplotlib.pyplot as plt
from fft_plot import FFTPlot
from note_table import NoteTable
from binding_handler import AudioBindingHandler

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    cells_update_signal = Signal(set)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        plt.ion()

        threshold_slider = QSlider()
        threshold_slider.setMaximum(40)
        threshold_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.settings = QSettings()
        threshold = self.settings.value("threshold")
        threshold_slider.setValue(int(threshold) if threshold else 10)

        self.binding_handler = AudioBindingHandler(threshold_slider)
        note_table = NoteTable(self.binding_handler.bindings)
        self.binding_handler.cells_update.connect(note_table.set_highlighted_cells)
        layout.addWidget(note_table, 1)

        plot_layout = QHBoxLayout()
        layout.addLayout(plot_layout)

        self.fft_plot = FFTPlot(
            self.binding_handler.window_length, self.binding_handler.sample_rate)
        self.binding_handler.cells_update = note_table.set_highlighted_cells
        self.binding_handler.fft_update_signal.connect(self.fft_plot.update_plot)
        threshold_slider.valueChanged.connect(self.fft_plot.update_threshold)
        threshold_slider.valueChanged.connect(lambda value: self.settings.setValue("threshold", value))
        self.fft_plot.update_threshold(threshold_slider.value())
        plot_layout.addWidget(self.fft_plot)

        plot_layout.addWidget(threshold_slider)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def stop(self):
        self.binding_handler.stop_thread()


def main():
    QCoreApplication.setOrganizationName("meanwhile131")
    QCoreApplication.setApplicationName("Microphone Controller")
    window = MainWindow()
    window.show()
    app.exec()
    window.stop()


if __name__ == "__main__":
    main()
