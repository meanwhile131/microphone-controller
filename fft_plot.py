from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import numpy as np
from matplotlib.figure import Figure


class FFTPlot(FigureCanvasQTAgg):
    def __init__(self, window_len: int, sample_rate: int):
        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        all_freq = np.fft.rfftfreq(window_len, d=1/sample_rate)[1:250]
        self.ln, = self.axes.plot(all_freq, np.zeros((len(all_freq,))))
        self.axes.set_ylim(bottom=0, top=40)
        self.press_threshold_line = self.axes.axhline(0, color='red')
        self.release_threshold_line = self.axes.axhline(0, color='green')
        super().__init__(self.fig)

    def update_plot(self, fft_data):
        self.ln.set_ydata(fft_data[1:250])
        self.fig.canvas.draw_idle()

    def update_press_threshold(self, threshold):
        self.press_threshold_line.set_ydata([threshold, threshold])
        self.fig.canvas.draw_idle()

    def update_release_threshold(self, threshold):
        self.release_threshold_line.set_ydata([threshold, threshold])
        self.fig.canvas.draw_idle()
