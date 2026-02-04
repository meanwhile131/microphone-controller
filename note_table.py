from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtCore import Qt
import music


class NoteTable(QTableWidget):
    bindings: dict

    def __init__(self, bindings={}):
        super().__init__()
        self.setRowCount(music.note_count)
        self.setColumnCount(music.octave_count)
        self.setHorizontalHeaderLabels(list(map(str, music.octaves)))
        self.setVerticalHeaderLabels(music.notes)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # disable editing
        self.setWindowTitle("Microphone Controller")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bindings = bindings

        for octave in range(music.octave_count):
            for note_i in range(music.note_count):
                note_cell = QTableWidgetItem()
                note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(note_i, octave, note_cell)
                self.update_cell_text((note_i, octave))

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
