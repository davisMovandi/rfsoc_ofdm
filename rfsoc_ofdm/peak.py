import numpy as np


class Peaks:
    """
    Find the strongest spectral peaks from time-domain data.

    Outputs:
      - mag_peaks   : peak magnitudes (in dB by default, aligned with freq_peaks)
      - freq_peaks  : peak frequencies in Hz (aligned with mag_peaks)
      - peak_bins   : FFT bin indices corresponding to those peaks
    """

    def __init__(self,
                 data,
                 fs,
                 num_peaks=5,
                 threshold=0.1,
                 return_db=True,
                 eps=1e-12):

        self._fs = float(fs)
        self._n = int(len(data))
        self._eps = float(eps)
        self._return_db = bool(return_db)

        # Window
        self._window = np.blackman(self._n)

        # Spectra + frequency axis
        self._fft, self._mag_lin, self._mag_db = self._compute_spectrum(data)
        self._freq_axis = np.fft.fftshift(np.fft.fftfreq(self._n, d=1.0 / self._fs))

        # Peaks (indices + values)
        self.peak_bins, self.mag_peaks, self.freq_peaks = self._get_peaks(
            mag_lin=self._mag_lin,
            mag_db=self._mag_db,
            freq_axis=self._freq_axis,
            num_peaks=num_peaks,
            threshold=threshold
        )

    def _compute_spectrum(self, data):
        """Compute fftshifted FFT, plus normalized magnitude in linear and dB."""
        x = np.asarray(data)
        xw = x * self._window

        X = np.fft.fftshift(np.fft.fft(xw))
        mag = np.abs(X)

        # Normalize to max (avoid divide-by-zero)
        mag_max = np.max(mag)
        if mag_max > 0:
            mag_lin = mag / mag_max
        else:
            mag_lin = mag.copy()

        mag_db = 20.0 * np.log10(mag_lin + self._eps)
        return X, mag_lin, mag_db

    def _get_peaks(self, mag_lin, mag_db, freq_axis, num_peaks=5, threshold=0.1):
        """
        Pick the top-N FFT bins by magnitude (not strictly local maxima).
        threshold is a linear fraction of the max (since mag_lin is normalized 0..1).
        """
        mag_lin = np.asarray(mag_lin)
        freq_axis = np.asarray(freq_axis)

        # Candidates above threshold
        if threshold is None:
            cand = np.arange(mag_lin.size)
        else:
            cand = np.flatnonzero(mag_lin >= float(threshold))

        if cand.size == 0:
            # Nothing above threshold: return empty arrays
            empty = np.array([], dtype=float)
            return np.array([], dtype=int), empty, empty

        # If fewer candidates than requested, just take all
        k = min(int(num_peaks), cand.size)

        # Take top-k candidates by linear magnitude
        cand_mags = mag_lin[cand]
        top_rel = np.argpartition(cand_mags, -k)[-k:]          # indices into cand
        top_bins = cand[top_rel]                               # FFT bin indices

        # Sort descending by magnitude
        order = np.argsort(mag_lin[top_bins])[::-1]
        peak_bins = top_bins[order]

        # Aligned outputs
        freq_peaks = freq_axis[peak_bins]
        mag_peaks = (mag_db[peak_bins] if self._return_db else mag_lin[peak_bins])

        return peak_bins.astype(int), mag_peaks.astype(float), freq_peaks.astype(float)

    @property
    def spectrum_db(self):
        return self._mag_db

    @property
    def spectrum_lin(self):
        return self._mag_lin

    @property
    def freq_axis(self):
        return self._freq_axis
