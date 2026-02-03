import sys
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QKeyEvent, QKeySequence, QFocusEvent
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
import music

app = QApplication(sys.argv)


class NoteTable(QTableWidget):
    bindings = {}

    def __init__(self):
        super().__init__()
        self.setRowCount(music.note_count)
        self.setColumnCount(music.octave_count)
        self.setHorizontalHeaderLabels(list(map(str, music.octaves)))
        self.setVerticalHeaderLabels(music.notes)
        self.setSelectionMode(QTableWidget.SingleSelection)

        for octave in range(music.octave_count):
            for note_i, note in enumerate(music.notes):
                note_cell = QTableWidgetItem(
                    f"{music.note_to_freq[octave][note]:.1f}")
                note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(note_i, octave, note_cell)

        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def keyPressEvent(self, event: QKeyEvent):
        cell = self.currentItem()
        cell_location = (cell.row(), cell.column())
        if event.isAutoRepeat() or cell is None:
            return super().keyPressEvent(event)

        key = event.key()
        if key == 0:
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


note_table = NoteTable()
note_table.show()

sys.exit(app.exec())
