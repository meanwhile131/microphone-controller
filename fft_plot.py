from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import pyaudio
import numpy as np
from threading import Thread
from matplotlib.figure import Figure


class FFTPlot(FigureCanvasQTAgg):
    __stop = False

    def __init__(self, bindings: dict, audio: pyaudio.PyAudio, sample_rate=44100):
        self.bindings = bindings
        self.sample_rate = sample_rate
        self.window_length = sample_rate // 4
        self.stream = audio.open(sample_rate, 1, pyaudio.paFloat32, input=True)
        self.all_freq = np.fft.rfftfreq(
            self.window_length, 1./self.sample_rate)

        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        self.ln, = self.axes.plot(self.all_freq, np.zeros(self.all_freq.shape))
        self.noise_floor_line = self.axes.axhline(
            y=0, color='r', linestyle='-')
        super().__init__(self.fig)

        self.__thread = Thread(target=self.handler_thread)
        self.__thread.start()

    def handler_thread(self):
        self.stream.start_stream()
        while not self.__stop:
            chunk = self.stream.read(self.window_length)
            audio_data = np.frombuffer(chunk, np.float32)
            fft_data = abs(np.fft.rfft(audio_data))

            self.ln.set_ydata(fft_data)
            noise_floor = sum(fft_data) / len(fft_data)
            self.noise_floor_line.set_ydata([noise_floor, noise_floor])
            self.axes.relim()
            self.axes.autoscale_view()
            self.fig.canvas.draw()

        self.stream.stop_stream()

    def stop_thread(self):
        self.__stop = True
        self.__thread.join()
