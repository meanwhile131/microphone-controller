from threading import Thread
import music
import numpy as np
import pyaudio
from evdev import UInput, ecodes
from PySide6.QtCore import Qt, Signal, QObject


QT_TO_EVDEV_MAP = {
    # Alphanumeric keys
    Qt.Key.Key_A: ecodes.KEY_A,
    Qt.Key.Key_B: ecodes.KEY_B,
    Qt.Key.Key_C: ecodes.KEY_C,
    Qt.Key.Key_D: ecodes.KEY_D,
    Qt.Key.Key_E: ecodes.KEY_E,
    Qt.Key.Key_F: ecodes.KEY_F,
    Qt.Key.Key_G: ecodes.KEY_G,
    Qt.Key.Key_H: ecodes.KEY_H,
    Qt.Key.Key_I: ecodes.KEY_I,
    Qt.Key.Key_J: ecodes.KEY_J,
    Qt.Key.Key_K: ecodes.KEY_K,
    Qt.Key.Key_L: ecodes.KEY_L,
    Qt.Key.Key_M: ecodes.KEY_M,
    Qt.Key.Key_N: ecodes.KEY_N,
    Qt.Key.Key_O: ecodes.KEY_O,
    Qt.Key.Key_P: ecodes.KEY_P,
    Qt.Key.Key_Q: ecodes.KEY_Q,
    Qt.Key.Key_R: ecodes.KEY_R,
    Qt.Key.Key_S: ecodes.KEY_S,
    Qt.Key.Key_T: ecodes.KEY_T,
    Qt.Key.Key_U: ecodes.KEY_U,
    Qt.Key.Key_V: ecodes.KEY_V,
    Qt.Key.Key_W: ecodes.KEY_W,
    Qt.Key.Key_X: ecodes.KEY_X,
    Qt.Key.Key_Y: ecodes.KEY_Y,
    Qt.Key.Key_Z: ecodes.KEY_Z,

    # Number keys (main keyboard)
    Qt.Key.Key_0: ecodes.KEY_0,
    Qt.Key.Key_1: ecodes.KEY_1,
    Qt.Key.Key_2: ecodes.KEY_2,
    Qt.Key.Key_3: ecodes.KEY_3,
    Qt.Key.Key_4: ecodes.KEY_4,
    Qt.Key.Key_5: ecodes.KEY_5,
    Qt.Key.Key_6: ecodes.KEY_6,
    Qt.Key.Key_7: ecodes.KEY_7,
    Qt.Key.Key_8: ecodes.KEY_8,
    Qt.Key.Key_9: ecodes.KEY_9,

    # Function keys
    Qt.Key.Key_F1: ecodes.KEY_F1,
    Qt.Key.Key_F2: ecodes.KEY_F2,
    Qt.Key.Key_F3: ecodes.KEY_F3,
    Qt.Key.Key_F4: ecodes.KEY_F4,
    Qt.Key.Key_F5: ecodes.KEY_F5,
    Qt.Key.Key_F6: ecodes.KEY_F6,
    Qt.Key.Key_F7: ecodes.KEY_F7,
    Qt.Key.Key_F8: ecodes.KEY_F8,
    Qt.Key.Key_F9: ecodes.KEY_F9,
    Qt.Key.Key_F10: ecodes.KEY_F10,
    Qt.Key.Key_F11: ecodes.KEY_F11,
    Qt.Key.Key_F12: ecodes.KEY_F12,

    # Special keys
    Qt.Key.Key_Space: ecodes.KEY_SPACE,
    Qt.Key.Key_Enter: ecodes.KEY_ENTER,
    Qt.Key.Key_Return: ecodes.KEY_ENTER,
    Qt.Key.Key_Escape: ecodes.KEY_ESC,
    Qt.Key.Key_Tab: ecodes.KEY_TAB,
    Qt.Key.Key_Backspace: ecodes.KEY_BACKSPACE,
    Qt.Key.Key_Delete: ecodes.KEY_DELETE,
    Qt.Key.Key_Insert: ecodes.KEY_INSERT,
    Qt.Key.Key_Home: ecodes.KEY_HOME,
    Qt.Key.Key_End: ecodes.KEY_END,
    Qt.Key.Key_PageUp: ecodes.KEY_PAGEUP,

    # Arrow keys
    Qt.Key.Key_Up: ecodes.KEY_UP,
    Qt.Key.Key_Down: ecodes.KEY_DOWN,
    Qt.Key.Key_Left: ecodes.KEY_LEFT,
    Qt.Key.Key_Right: ecodes.KEY_RIGHT,

    # Modifier keys (assuming left variants for simplicity; specific left/right keys exist in evdev)
    Qt.Key.Key_Shift: ecodes.KEY_LEFTSHIFT,
    Qt.Key.Key_Control: ecodes.KEY_LEFTCTRL,
    Qt.Key.Key_Alt: ecodes.KEY_LEFTALT,
    Qt.Key.Key_Meta: ecodes.KEY_LEFTMETA,

    # Punctuation and symbols
    Qt.Key.Key_Minus: ecodes.KEY_MINUS,
    Qt.Key.Key_Equal: ecodes.KEY_EQUAL,
    Qt.Key.Key_BracketLeft: ecodes.KEY_LEFTBRACE,
    Qt.Key.Key_BracketRight: ecodes.KEY_RIGHTBRACE,
    Qt.Key.Key_Semicolon: ecodes.KEY_SEMICOLON,
    Qt.Key.Key_Apostrophe: ecodes.KEY_APOSTROPHE,
    Qt.Key.Key_Backslash: ecodes.KEY_BACKSLASH,
    Qt.Key.Key_Comma: ecodes.KEY_COMMA,
    Qt.Key.Key_Period: ecodes.KEY_DOT,
    Qt.Key.Key_Slash: ecodes.KEY_SLASH,
    Qt.Key.Key_CapsLock: ecodes.KEY_CAPSLOCK,
    Qt.Key.Key_NumLock: ecodes.KEY_NUMLOCK,
    Qt.Key.Key_ScrollLock: ecodes.KEY_SCROLLLOCK,
}


class AudioBindingHandler(QObject):
    __stop = False
    fft_update_signal = Signal(np.ndarray)

    def __init__(self, audio: pyaudio.PyAudio, threshold_slider: QSlider, bindings: dict[tuple[int, int]: int] = {}, sample_rate=44100, cells_update_callback=lambda highlighted_cells: None):
        super().__init__()
        self.bindings = bindings
        self.cells_update_callback = cells_update_callback
        self.sample_rate = sample_rate
        self.window_length = sample_rate // 4
        self.buffer_size = sample_rate // 100
        self.stream = audio.open(sample_rate, 1, pyaudio.paFloat32, input=True,
                                 frames_per_buffer=self.buffer_size)
        self.pressed_keys = set()
        self.threshold_slider = threshold_slider

        self.ui = UInput()

        self.__thread = Thread(target=self.handler_thread)
        self.__thread.start()

    def handler_thread(self):
        window = np.zeros(self.window_length, dtype=np.float32)
        self.stream.start_stream()
        while not self.__stop:
            chunk = self.stream.read(self.buffer_size,
                                     exception_on_overflow=False)
            audio_data = np.frombuffer(chunk, np.float32)
            window = np.concatenate((window[len(audio_data):], audio_data))
            fft_data = abs(np.fft.rfft(window))
            self.fft_update_signal.emit(fft_data)

            highlighted_cells = set()
            for note_i, octave in self.bindings:  # only check bound notes
                note = music.notes[note_i]
                freq = music.note_to_freq[octave][note]
                fft_i = round(freq / self.sample_rate * self.window_length)
                key = QT_TO_EVDEV_MAP[self.bindings[(note_i, octave)]]
                if fft_data[fft_i] > self.threshold_slider.value():
                    highlighted_cells.add((note_i, octave))
                    if key not in self.pressed_keys:
                        self.ui.write(ecodes.EV_KEY, key, 1)
                        self.ui.syn()
                        self.pressed_keys.add(key)
                    continue
                if key in self.pressed_keys:
                    self.ui.write(ecodes.EV_KEY, key, 0)
                    self.ui.syn()
                    self.pressed_keys.remove(key)
            self.cells_update_callback(highlighted_cells)

        self.stream.stop_stream()
        self.ui.close()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()
