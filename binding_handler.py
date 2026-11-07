from threading import Thread
import music
import numpy as np
import sounddevice as sd
import keyboard
from PyQt6.QtCore import pyqtSignal, QObject, QSettings
from PyQt6.QtWidgets import QSlider, QMainWindow, QApplication
from PyQt6.QtGui import QKeySequence
import math

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
    fft_update_signal = pyqtSignal(np.ndarray)
    bindings: dict[tuple[int, int]: int]
    cells_update = pyqtSignal(set)

    def __init__(self, press_threshold_slider: QSlider, release_threshold_slider: QSlider):
        super().__init__()
        self.settings = QSettings()
        bindings = self.settings.value("bindings")
        self.bindings = bindings if bindings else {}
        self.pressed_keys = set()
        self.press_threshold_slider = press_threshold_slider
        self.release_threshold_slider = release_threshold_slider

        self.window_length = 10000
        self.sample_rate = 44100
        self.__thread = None
        self.start_processing(self.settings.value("microphone"))

    def start_processing(self, device_id=None):
        try:
            if self.__thread:
                self.stop_thread()
            self.stream = sd.InputStream(device=device_id)
            if device_id is not None:
                self.settings.setValue("microphone", device_id)
            self.__stop = False
            print(f'Opened audio for device {device_id}')
            self.sample_rate = int(self.stream.samplerate)
            self.window_length = self.sample_rate // 4
            self.buffer_size = self.sample_rate // 20
            self.__thread = Thread(target=self.handler_thread)
            self.__thread.start()
        except (sd.PortAudioError, ValueError) as e:
            print(f"failed to open audio for device {device_id}: {e}")
            if device_id is not None:
                saved = self.settings.value("microphone")
                if saved == device_id:
                    self.settings.remove("microphone")
                    saved = None
                self.start_processing(saved)

    def handler_thread(self):
        window = np.zeros(self.window_length, dtype=np.float32)
        self.stream.start()
        fft_frequencies = np.fft.rfftfreq(self.window_length, d=1/self.sample_rate)
        pink_noise_correction = np.ones(len(fft_frequencies))
        pink_noise_correction[1:] = np.sqrt(fft_frequencies[1:])
        pink_noise_correction[1:] /= np.mean(pink_noise_correction[1:])
        while not self.__stop:
            chunk = self.stream.read(self.buffer_size)[0]
            audio_data = np.frombuffer(chunk, np.float32)
            window = np.concatenate((window[len(audio_data):], audio_data))
            fft_data = abs(np.fft.rfft(window)) * pink_noise_correction
            self.fft_update_signal.emit(fft_data)

            highlighted_cells = set()
            for note_i, octave in list(self.bindings):  # only check bound notes
                note = music.notes[note_i]
                freq = music.note_to_freq[octave][note]
                fft_i = round(freq / self.sample_rate * self.window_length)
                value = fft_data[fft_i]
                key = QKeySequence(self.bindings[(note_i, octave)]).toString().lower()
                key = _QT_TO_KEYBOARD.get(key, key)

                pressThreshold = self.press_threshold_slider.value()
                abovePressThreshold = value > pressThreshold
                alreadyPressed = key in self.pressed_keys
                isFocused = QApplication.activeWindow() is not None
                if abovePressThreshold and not alreadyPressed:
                    if not isFocused:
                        keyboard.press(key)
                    self.pressed_keys.add(key)

                releaseThreshold = self.release_threshold_slider.value()
                belowReleaseThreshold = value < releaseThreshold
                if belowReleaseThreshold and alreadyPressed:
                    keyboard.release(key)
                    self.pressed_keys.remove(key)

                if key in self.pressed_keys:
                    highlighted_cells.add((note_i, octave))

            self.cells_update.emit(highlighted_cells)

        self.stream.stop()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()
