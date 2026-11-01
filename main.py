import sys
from PyQt6.QtCore import Qt, QCoreApplication, QSettings, pyqtSignal
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QSlider, QHBoxLayout
import matplotlib.pyplot as plt
from fft_plot import FFTPlot
from note_table import NoteTable
from binding_handler import AudioBindingHandler


class MainWindow(QMainWindow):
    cells_update_signal = pyqtSignal(set)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        plt.ion()

        press_threshold_slider = self.create_threshold_slider()
        release_threshold_slider = self.create_threshold_slider()

        self.settings = QSettings()
        press_threshold = self.settings.value("press_threshold")
        press_threshold_slider.setValue(int(press_threshold) if press_threshold else 10)
        release_threshold = self.settings.value("release_threshold")
        release_threshold_slider.setValue(int(release_threshold) if release_threshold else 8)

        self.binding_handler = AudioBindingHandler(press_threshold_slider, release_threshold_slider)
        note_table = NoteTable(self.binding_handler.bindings)
        self.binding_handler.cells_update.connect(note_table.set_highlighted_cells)
        layout.addWidget(note_table, 1)

        plot_layout = QHBoxLayout()
        layout.addLayout(plot_layout)

        self.fft_plot = FFTPlot(
            self.binding_handler.window_length, self.binding_handler.sample_rate)
        self.binding_handler.fft_update_signal.connect(self.fft_plot.update_plot)
        press_threshold_slider.valueChanged.connect(self.fft_plot.update_press_threshold)
        press_threshold_slider.valueChanged.connect(lambda value: self.settings.setValue("press_threshold", value))
        release_threshold_slider.valueChanged.connect(self.fft_plot.update_release_threshold)
        release_threshold_slider.valueChanged.connect(lambda value: self.settings.setValue("release_threshold", value))
        self.fft_plot.update_press_threshold(press_threshold_slider.value())
        self.fft_plot.update_release_threshold(release_threshold_slider.value())
        plot_layout.addWidget(self.fft_plot)

        plot_layout.addWidget(press_threshold_slider)
        plot_layout.addWidget(release_threshold_slider)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_threshold_slider(self):
        threshold_slider = QSlider()
        threshold_slider.setMaximum(40)
        threshold_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return threshold_slider

    def closeEvent(self, event):
        self.binding_handler.stop_thread()


def main():
    QCoreApplication.setOrganizationName("meanwhile131")
    QCoreApplication.setApplicationName("Microphone Controller")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
