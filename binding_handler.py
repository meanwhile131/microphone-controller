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
        self.stream = None
        self.start_processing(self.settings.value("microphone"))

    def start_processing(self, device_id=None):
        try:
            if self.stream:
                self.stream.stop()
            self.stream = sd.InputStream(device=device_id, callback=self.handle_audio, channels=1)
            if device_id is not None:
                self.settings.setValue("microphone", device_id)
            print(f'Opened audio for device {device_id}')
            self.sample_rate = int(self.stream.samplerate)
            self.window_length = self.sample_rate // 4
            self.window = np.zeros(self.window_length, dtype=np.float32)
            fft_frequencies = np.fft.rfftfreq(len(self.window), d=1/self.sample_rate)
            self.pink_noise_correction = np.ones(len(fft_frequencies))
            self.pink_noise_correction[1:] = np.sqrt(fft_frequencies[1:])
            self.pink_noise_correction[1:] /= np.mean(self.pink_noise_correction[1:])
            self.stream.start()
        except (sd.PortAudioError, ValueError) as e:
            print(f"failed to open audio for device {device_id}: {e}")
            if device_id is not None:
                saved = self.settings.value("microphone")
                if saved == device_id:
                    self.settings.remove("microphone")
                    saved = None
                self.start_processing(saved)

    def handle_audio(self, audio_data, frames, time, status):
        self.window = np.concatenate((self.window[len(audio_data):], audio_data[:, 0]))
        fft_data = abs(np.fft.rfft(self.window)) * self.pink_noise_correction
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

    def stop_thread(self):
        self.stream.stop()
