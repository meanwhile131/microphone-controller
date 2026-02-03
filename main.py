import sys
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
import music

app = QApplication(sys.argv)


class NoteTable(QTableWidget):
    binding_cell = None
    bindings = {}

    def __init__(self):
        super().__init__()
        self.setRowCount(music.note_count)
        self.setColumnCount(music.octave_count)
        self.setHorizontalHeaderLabels(list(map(str, music.octaves)))
        self.setVerticalHeaderLabels(music.notes)
        for octave in range(music.octave_count):
            for note_i, note in enumerate(music.notes):
                note_cell = QTableWidgetItem(
                    f"{music.note_to_freq[octave][note]:.2f} Hz")
                note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(note_i, octave, note_cell)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cellDoubleClicked.connect(self.doubleclick_handler)
        self.currentCellChanged.connect(self.stop_binding)

    @Slot()
    def doubleclick_handler(self, note_i: int, octave: int):
        note_cell: QTableWidgetItem = self.item(note_i, octave)
        note_cell.setText(
            f"{music.note_to_freq[octave][music.notes[note_i]]:.2f} Hz (?)")
        binding_cell = (note_i, octave)

    @Slot()
    def stop_binding(self, _newRow, _newCol, note_i: int, octave: int):
        note_cell: QTableWidgetItem = self.item(note_i, octave)
        note_cell.setText(
            f"{music.note_to_freq[octave][music.notes[note_i]]:.2f} Hz")
        binding_cell = None


note_table = NoteTable()
note_table.show()

sys.exit(app.exec())
