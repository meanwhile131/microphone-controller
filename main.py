import sys

from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
import music

binding_cell = None
bindings = {}

app = QApplication(sys.argv)
table = QTableWidget()
table.setRowCount(music.note_count)
table.setColumnCount(music.octave_count)
table.setHorizontalHeaderLabels(list(map(str, music.octaves)))
table.setVerticalHeaderLabels(music.notes)

@Slot()
def doubleclick_handler(note_i: int, octave: int):
    note_cell: QTableWidgetItem = table.item(note_i, octave)
    print(f'click at {octave} {music.notes[note_i]}')

for octave in range(music.octave_count):
    for note_i, note in enumerate(music.notes):
        note_cell = QTableWidgetItem(f"{music.note_to_freq[octave][note]:.2f} Hz")
        note_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(note_i, octave, note_cell)

table.setEditTriggers(QTableWidget.NoEditTriggers)
table.cellDoubleClicked.connect(doubleclick_handler)
table.show()

sys.exit(app.exec())