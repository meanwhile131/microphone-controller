import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QMainWindow, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import music
import numpy as np
import pyaudio
from threading import Thread

app = QApplication(sys.argv)


class NoteTable(QTableWidget):
    bindings: dict

    def __init__(self, bindings={}):
        super().__init__()
        self.setRowCount(music.note_count)
        self.setColumnCount(music.octave_count)
        self.setHorizontalHeaderLabels(list(map(str, music.octaves)))
        self.setVerticalHeaderLabels(music.notes)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setWindowTitle("Microphone Controller")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bindings = bindings

        for octave in range(music.octave_count):
            for note_i, note in enumerate(music.notes):
                note_cell = QTableWidgetItem()
                note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(note_i, octave, note_cell)
                self.update_cell_text((note_i, octave))

        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def keyPressEvent(self, event: QKeyEvent):
        selected_items = self.selectedItems()
        if not selected_items:
            return super().keyPressEvent(event)
        # there can only be one because of QTableWidget.SingleSelection
        cell = selected_items[0]
        cell_location = (cell.row(), cell.column())
        if event.isAutoRepeat() or cell is None:
            return super().keyPressEvent(event)

        key = event.key()
        if key == 0 or key == Qt.Key.Key_Escape:
            self.bindings.pop(cell_location, None)
        else:
            self.bindings[cell_location] = key
        self.update_cell_text(cell_location)
        self.clearSelection()

    def update_cell_text(self, cell_location: tuple[int, int]):
        note_i, octave = cell_location
        cell: QTableWidgetItem = self.item(note_i, octave)
        text = f"{music.note_to_freq[octave][music.notes[note_i]]:.1f}"

        if cell_location in self.bindings:
            bind_key = self.bindings[cell_location]
            key_sequence = QKeySequence(bind_key).toString()
            text += f" ({key_sequence})"
        cell.setText(text)


class FFTPlot(FigureCanvasQTAgg):
    __stop = False

    def __init__(self, bindings: dict, audio: pyaudio.PyAudio, sample_rate=44100):
        self.bindings = bindings
        self.sample_rate = sample_rate
        self.window_length = sample_rate // 4
        self.stream = audio.open(sample_rate, 1, pyaudio.paFloat32, input=True)
        self.all_freq = np.fft.rfftfreq(
            self.window_length, 1./self.sample_rate)

        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        self.ln, = self.axes.plot(self.all_freq, np.zeros(self.all_freq.shape))
        super().__init__(self.fig)

        self.__thread = Thread(target=self.handler_thread)
        self.__thread.start()

    def handler_thread(self):
        self.stream.start_stream()
        while not self.__stop:
            chunk = self.stream.read(self.window_length)
            audio_data = np.frombuffer(chunk, np.float32)
            fft_data = abs(np.fft.rfft(audio_data))

            self.ln.set_ydata(fft_data)
            self.axes.relim()
            self.axes.autoscale_view()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        self.stream.stop_stream()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()


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
