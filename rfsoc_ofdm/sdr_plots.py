__author__ = "David Northcote"
__organisation__ = "The Univeristy of Strathclyde"
__support__ = "https://github.com/strath-sdr/rfsoc_radio"

import numpy as np
import plotly.graph_objs as go
import ipywidgets as ipw
from contextlib import contextmanager

from rfsoc_ofdm.peak import Peaks
from .quick_widgets import UserInput

import plotly.io as pio

pio.templates.default = "seaborn"
                
class SpectrumAnalyser():
    def __init__(self,
                 data,
                 fs,
                 animation_period=50,
                 width=800,
                 height=600,
                 autosize=True):
        """Create a new Spectrum Analyser object for plotting frequency against power."""
        
        self._fs = fs
        self._window = np.array(np.blackman(len(data))[:])
        self._data = self._data = [{'y' : self._compute_spectrum(data),
                                    'name' : 'IQ Spectrum',
                                    'showlegend' : True}]
        self._animation_period = animation_period
        self._width = width
        self._height = height
        self._yaxisrange = [-100, 10]
        lim = int(self._fs/2)
        self._xaxisrange = [-lim, lim - (self._fs/len(data))]
        self._autosize = autosize
        self._complex = isinstance(data[0], complex)
        self._yrange_counter = 0
        
        self._layout = {
            'height' : self._height,
            'width' : self._width,
            'autosize' : True,
            'xaxis' : {
                'range' : self._xaxisrange,
                'title' : 'Frequency (Hz)',
            },
            'yaxis' : {
                'range' : self._yaxisrange,
                'title' : 'Normalised Amplitude (dB)',
            },
            'title' : 'Frequency Spectrum'
        }
        
        self._plot = go.FigureWidget(
            layout = self._layout,
            data = self._data
        )
        
        self._plot.layout.xaxis.range = self._xaxisrange
        self._plot.data[0].x = [x for x in np.arange(-lim, lim, (self._fs/len(data)))]   
        
    def _update_yrange(self):
        if self._yrange_counter > 4:
            min_data = min(self._data)
            max_data = max(self._data)
            self._yaxisrange = [min_data-10, max_data+10]
            self._plot.layout.yaxis.range = self._yaxisrange
            self._yrange_counter = 0
        else:
            self._yrange_counter += 1
        
    def _compute_spectrum(self, data):
        data = data * self._window
        data = np.fft.fftshift(np.fft.fft(data))
        with np.errstate(divide='ignore', invalid='ignore'):
            data = abs(data)/max(abs(data))
        return 20*np.where(data > 0, np.log10(data), 0)
        
    def set_frequency(self, fs):
        self._fs = fs
    
    def update_data(self, data):
        self._window = np.array(np.blackman(len(data))[:])
        lim = int(self._fs/2)
        self._xaxisrange = [-lim, lim - (self._fs/len(data))]
        self._plot.layout.xaxis.range = self._xaxisrange
        self._data = self._compute_spectrum(data)
        self._update_yrange()
        self._plot.data[0].y = self._data
        self._plot.data[0].x = [x for x in np.arange(-lim, lim, (self._fs/len(data)))]
            
    def get_widget(self):
        return self._plot    
        

class TimePlot():
    def __init__(self,
                 data,
                 animation_period=50,
                 width=800,
                 height=600,
                 autosize=True):
        """Create a new plot object for plotting data against time."""
        
        self._data = np.empty(len(data))
        self._animation_period = animation_period
        self._width = width
        self._height = height
        self._yaxisrange = [-0.3, 0.3]
        self._xaxisrange = [-0.5, len(data)-0.5]
        self._autosize = autosize
        self._complex = isinstance(data[0], complex)
        self._yrange_counter = 0
        
        if self._complex:
            self._data = [{'y' : np.real(data),
                           'name' : 'Real Signal'},
                          {'y' : np.imag(data),
                           'name' : 'Imag Signal'}]
        else:
            self._data = [{'y' : data, 'name' : 'Time Signal'}]
        
        self._layout = {
            'height' : self._height,
            'width' : self._width,
            'autosize' : True,
            'xaxis' : {
                'range' : self._xaxisrange,
                'title' : 'Samples',
            },
            'yaxis' : {
                'range' : self._yaxisrange,
                'title' : 'Amplitude',
            },
            'title' : 'Time Domain Signal'
        }
        
        self._plot = go.FigureWidget(
            layout = self._layout,
            data = self._data
        )
        
    def _update_yrange(self):
        if self._yrange_counter > 4:
            if self._complex:
                min_data = min(self._plot.data[0].y)
                max_data = max(self._plot.data[0].y)
            else:
                min_data = min(self._plot.data[0].y)
                max_data = max(self._plot.data[0].y)
            self._yaxisrange = [min_data-0.05, max_data+0.05]
            self._plot.layout.yaxis.range = self._yaxisrange
            self._yrange_counter = 0
        else:
            self._yrange_counter += 1
        
    def set_axisrange(self, axisrange):
        self._yaxisrange = axisrange
        self._plot.layout.yaxis.range = axisrange
        
    def update_data(self, data):
        """Update the frame of data currently on the canvas
        """
        self._xaxisrange = len(data)
        self._plot.layout.xaxis.range = [-0.5, self._xaxisrange-0.5]
        self._update_yrange()
        
        if self._complex:
            self._data = [{'y' : np.real(data)},
                          {'y' : np.imag(data)}]
        else:
            self._data = [{'y' : data}]

        self._plot.data[0].y = self._data[0].get('y')
        if self._complex:
            self._plot.data[1].y = self._data[1].get('y')
                
    def get_widget(self):
        return self._plot

class EVMPlot():
    def __init__(self,
                 data,
                 animation_period=50,
                 width=800,
                 height=600,
                 autosize=True):
        """Create a new plot object for plotting data against time."""
        
        self._data = np.empty(len(data))
        self._animation_period = animation_period
        self._width = width
        self._height = height
        self._yaxisrange = [-60, -20]
        self._xaxisrange = [-0.5, len(data)-0.5]
        self._autosize = autosize
        self._complex = False # isinstance(data[0], complex)
        self._yrange_counter = 0
        
        if self._complex:
            self._data = [{'y' : np.real(data),
                           'name' : 'Real Signal'}]
        else:
            self._data = [{'y' : np.real(data), 'name' : 'EVM Data'}]
        
        self._layout = {
            'height' : self._height,
            'width' : self._width,
            'autosize' : False,
            'xaxis' : {
                'range' : self._xaxisrange,
                'title' : 'Symbols per subcarrier (not Syncronized)',
            },
            'yaxis' : {
                'range' : self._yaxisrange,
                'title' : 'EVM (dB)',
            },
            'title' : 'EVM Plot'
        }
        
        self._plot = go.FigureWidget(
            layout = self._layout,
            data = self._data
        )
        
    def _update_yrange(self):
        if self._yrange_counter > 4:
            if self._complex:
                min_data = min(self._plot.data[0].y)
                max_data = max(self._plot.data[0].y)
            else:
                min_data = min(self._plot.data[0].y)
                max_data = max(self._plot.data[0].y)
            self._yaxisrange = [min_data-0.05, max_data+0.05]
            self._plot.layout.yaxis.range = self._yaxisrange
            self._yrange_counter = 0
        else:
            self._yrange_counter += 1
        
    def set_axisrange(self, axisrange):
        self._yaxisrange = axisrange
        self._plot.layout.yaxis.range = axisrange
        
    def update_data(self, data):
        """Update the frame of data currently on the canvas
        """
        self._xaxisrange = len(data)
        self._plot.layout.xaxis.range = [-0.5, self._xaxisrange-0.5]
        # self._update_yrange()
        
        if self._complex:
            self._data = [{'y' : (data)}]
        else:
            self._data = [{'y' : data}]

        self._plot.data[0].y = self._data[0].get('y')
        if self._complex:
            self._plot.data[1].y = self._data[1].get('y')
                
    def get_widget(self):
        return self._plot

class PeakDataDisplay:
    def __init__(self,
                 data,
                 fs,
                 num_peaks=5,
                 animation_period=50,
                 height=200,
                 width=520,
                 autosize=True,
                 return_db=False):
        """Creates a live-updating table for peak frequency + magnitude."""

        def _callback_num_peaks(value):
            self._num_peaks = int(value)

        self._fs = float(fs)
        self._num_peaks = int(num_peaks)
        self._animation_period = int(animation_period)
        self._return_db = bool(return_db)

        # Build a grid table: header row + num_peaks rows
        self._grid = ipw.GridspecLayout(self._num_peaks + 1, 3)
        self._grid.layout = ipw.Layout(
            width=f"{width}px" if isinstance(width, (int, float)) else str(width),
            height=f"{height}px" if isinstance(height, (int, float)) else str(height),
        )
        # Column sizing (tweak as you like)
        self._grid.layout.grid_template_columns = "70px 180px 140px"
        self._grid.layout.grid_gap = "4px"

        # Header
        self._grid[0, 0] = ipw.HTML("<b>Peak</b>")
        self._grid[0, 1] = ipw.HTML("<b>Freq (MHz)</b>")
        self._grid[0, 2] = ipw.HTML("<b>Mag</b>" + (" <b>(dB)</b>" if self._return_db else " <b>(lin)</b>"))

        # Data cells (store references so updating is fast)
        self._cells = []
        for r in range(1, self._num_peaks + 1):
            c0 = ipw.HTML("—")
            c1 = ipw.HTML("—")
            c2 = ipw.HTML("—")
            self._grid[r, 0] = c0
            self._grid[r, 1] = c1
            self._grid[r, 2] = c2
            self._cells.append((c0, c1, c2))

        # Initial fill
        self.update_data(data)

        self.num_peaks_ui = UserInput(callback=_callback_num_peaks,
                                      value=5,
                                      min=1,
                                      max=10,
                                      step=1,
                                      readout_format='.0f',
                                      description='Number of Peaks: ')


    def set_frequency(self, fs):
        self._fs = float(fs)

    def update_data(self, data):
        """Recompute peaks from new time-domain data and update the table."""
        # Recompute peaks for the NEW data (this was missing before)
        peaks = Peaks(data, fs=self._fs, num_peaks=self._num_peaks, return_db=self._return_db)

        freqs = np.asarray(getattr(peaks, "freq_peaks", []), dtype=float)
        mags = np.asarray(getattr(peaks, "mag_peaks", []), dtype=float)

        n = min(self._num_peaks, len(freqs), len(mags))

        # Fill rows that have peaks
        for i in range(n):
            c0, c1, c2 = self._cells[i]
            c0.value = f"{i+1}"
            c1.value = f"{(freqs[i]/1e6):.5f}"
            c2.value = f"{mags[i]:.6g}" if not self._return_db else f"{mags[i]:.2f}"

        # Clear remaining rows (if fewer peaks returned)
        for i in range(n, self._num_peaks):
            c0, c1, c2 = self._cells[i]
            c0.value = "—"
            c1.value = "—"
            c2.value = "—"

    def get_widget(self):
        return self._grid

    
class ConstellationPlot():
    def __init__(self,
                 data,
                 animation_period=50,
                 height=600,
                 width=600,
                 autosize=True):
        """Creates a new plot object for plotting IQ constellations."""
        
        self._data = data
        self._animation_period = 50
        self._width = width
        self._height = height
        self._axisrange = [-1.5, 1.5]
        self._autosize = autosize
        self._complex = isinstance(self._data[0], complex)
        
        if not self._complex:
            raise Exception('Input data is not of type complex.')
        
        self._layout = {
            'hovermode' : 'closest',
            'height' : self._height,
            'width' : self._width,
            'autosize' : self._autosize,
            'xaxis' : {
                'range' : self._axisrange,
                'title' : 'In-phase Amplitude'
            },
            'yaxis' : {
                'range' : self._axisrange,
                'title' : 'Quadrature Amplitude'
            },
            'title' : 'Constellation Plot'
        }
        
        self._plot = go.FigureWidget(
            layout = self._layout,
            data = [{
                'mode' : 'markers',
                'x' : np.real(self._data),
                'y' : np.imag(self._data)
            }])
        
    def set_axisrange(self, axisrange):
        self._axisrange = axisrange
        self._plot.layout.yaxis.range = axisrange
        self._plot.layout.xaxis.range = axisrange
        
    def update_data(self, data):
        """Update the frame of data currently on the canvas
        """
        
        if not isinstance(data[0], complex):
            raise Exception('Input data is not of type complex.')
        self._data = data
        
        self._plot.data[0].update({'x' : np.real(self._data),
                                   'y' : np.imag(self._data)})        
        
    def get_widget(self):
        return self._plot
    
