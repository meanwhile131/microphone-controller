from threading import Thread
import music
import numpy as np
import pyaudio


class AudioBindingHandler:
    __stop = False

    def __init__(self, audio: pyaudio.PyAudio, bindings: dict[tuple[int, int]: int] = {}, sample_rate=44100, cells_update_callback=lambda highlighted_cells: None, fft_update_callback=lambda fft_data: None):
        self.bindings = bindings
        self.cells_update_callback = cells_update_callback
        self.fft_update_callback = fft_update_callback
        self.sample_rate = sample_rate
        self.window_length = sample_rate // 4
        self.stream = audio.open(sample_rate, 1, pyaudio.paFloat32, input=True)

        self.__thread = Thread(target=self.handler_thread)
        self.__thread.start()

    def handler_thread(self):
        self.stream.start_stream()
        while not self.__stop:
            chunk = self.stream.read(self.window_length)
            audio_data = np.frombuffer(chunk, np.float32)
            fft_data = abs(np.fft.rfft(audio_data))
            self.fft_update_callback(fft_data)

            highlighted_cells = set()
            for note_i, octave in self.bindings:  # only check bound notes
                note = music.notes[note_i]
                freq = music.note_to_freq[octave][note]
                fft_i = round(freq / self.sample_rate * self.window_length)
                if fft_data[fft_i] > 20:
                    highlighted_cells.add((note_i, octave))
            self.cells_update_callback(highlighted_cells)

        self.stream.stop_stream()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()
