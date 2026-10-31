from threading import Thread
import music
import numpy as np
import sounddevice as sd
import keyboard
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSettings
from PyQt6.QtWidgets import QSlider
from PyQt6.QtGui import QKeySequence

_QT_TO_KEYBOARD = {
    "space": "space",
    "shift": "shift",
    "control": "ctrl",
    "alt": "alt",
    "meta": "windows",
    "return": "enter",
    "esc": "esc",
    "ins": "insert",
    "del": "delete",
    "capslock": "caps lock",
    "numlock": "num lock",
    "scrolllock": "scroll lock",
    "pgup": "page up",
    "pgdown": "page down",
    "home": "home",
    "end": "end",
    "menu": "menu",
    "help": "help",
    "backspace": "backspace",
    "tab": "tab",
}


class AudioBindingHandler(QObject):
    __stop = False
    fft_update_signal = pyqtSignal(np.ndarray)
    bindings: dict[tuple[int, int]: int]
    cells_update = pyqtSignal(set)

    def __init__(self, threshold_slider: QSlider):
        super().__init__()
        self.settings = QSettings()
        bindings = self.settings.value("bindings")
        self.bindings = bindings if bindings else {}
        self.pressed_keys = set()
        self.threshold_slider = threshold_slider

        try:
            self.stream = sd.Stream()
            self.sample_rate = int(self.stream.samplerate)
            self.window_length = self.sample_rate // 4
            self.buffer_size = self.sample_rate // 20
            self.__thread = Thread(target=self.handler_thread)
            self.__thread.start()
        except OSError as e:
            print(f"failed to open audio: {e}")

    def handler_thread(self):
        window = np.zeros(self.window_length, dtype=np.float32)
        self.stream.start()
        while not self.__stop:
            chunk = self.stream.read(self.buffer_size)[0]
            audio_data = np.frombuffer(chunk, np.float32)
            window = np.concatenate((window[len(audio_data):], audio_data))
            fft_data = abs(np.fft.rfft(window))
            self.fft_update_signal.emit(fft_data)

            highlighted_cells = set()
            for note_i, octave in list(self.bindings):  # only check bound notes
                note = music.notes[note_i]
                freq = music.note_to_freq[octave][note]
                fft_i = round(freq / self.sample_rate * self.window_length)
                key = QKeySequence(self.bindings[(note_i, octave)]).toString().lower()
                key = _QT_TO_KEYBOARD.get(key, key)
                if fft_data[fft_i] > self.threshold_slider.value():
                    highlighted_cells.add((note_i, octave))
                    if key not in self.pressed_keys:
                        keyboard.press(key)
                        self.pressed_keys.add(key)
                    continue
                if key in self.pressed_keys:
                    keyboard.release(key)
                    self.pressed_keys.remove(key)
            self.cells_update.emit(highlighted_cells)

        self.stream.stop()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()
