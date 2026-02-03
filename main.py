import sys
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
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
                    f"{music.note_to_freq[octave][note]:.1f}")
                note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(note_i, octave, note_cell)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cellDoubleClicked.connect(self.doubleclick_handler)
        self.currentCellChanged.connect(self.stop_binding)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat() or self.binding_cell is None:
            return super().keyPressEvent(event)

        key = event.key()
        self.bindings[self.binding_cell] = key
        self.stop_binding()

    @Slot()
    def doubleclick_handler(self, note_i: int, octave: int):
        note_cell: QTableWidgetItem = self.item(note_i, octave)
        note_cell.setText(
            f"{music.note_to_freq[octave][music.notes[note_i]]:.1f} (?)")
        self.binding_cell = (note_i, octave)

    @Slot()
    def cell_focus_change(self, _newRow, _newCol, _note, _octave):
        self.stop_binding()

    def stop_binding(self):
        if self.binding_cell is None:
            return
        note_i, octave = self.binding_cell
        note_cell: QTableWidgetItem = self.item(note_i, octave)
        text = f"{music.note_to_freq[octave][music.notes[note_i]]:.1f}"

        if self.binding_cell in self.bindings:
            bind_key = self.bindings[self.binding_cell]
            key_sequence = QKeySequence(bind_key).toString()
            text += f" ({key_sequence})"
        note_cell.setText(text)
        self.binding_cell = None


note_table = NoteTable()
note_table.show()

sys.exit(app.exec())
