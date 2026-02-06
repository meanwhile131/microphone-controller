from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import numpy as np
from matplotlib.figure import Figure


class FFTPlot(FigureCanvasQTAgg):
    def __init__(self, window_len: int, sample_rate: int):
        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        all_freq = np.fft.rfftfreq(window_len, d=1/sample_rate)[1:250]
        self.ln, = self.axes.plot(all_freq, np.zeros((len(all_freq,))))
        self.axes.set_ylim(bottom=0,top=40)
        super().__init__(self.fig)

    def update_plot(self, fft_data):
        self.ln.set_ydata(fft_data[1:250])
        self.fig.canvas.draw()
