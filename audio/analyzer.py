"""
High-level audio analyzer.
Sits on top of PCMBuffer (projectM port) and adds beat detection + mel bands.
The render thread calls read_frame() every frame; the audio thread calls push_samples().
"""

import threading
from dataclasses import dataclass, field
import numpy as np
from collections import deque
from .pcm_buffer import PCMBuffer, WAVEFORM_SAMPLES, SPECTRUM_SAMPLES

SAMPLE_RATE = 44100
HOP_SIZE = 512
BEAT_HISTORY = 43       # ~1 second at 512-sample hops
BEAT_THRESHOLD = 1.5    # energy ratio to trigger beat
BEAT_COOLDOWN_FRAMES = 8
MEL_BANDS = 64


class AudioAnalyzer:
    def __init__(self):
        self._pcm = PCMBuffer()
        self._lock = threading.Lock()
        self._frame = FrameData()

        self._energy_history = deque([0.0] * BEAT_HISTORY, maxlen=BEAT_HISTORY)
        self._beat_cooldown = 0

    # ------------------------------------------------------------------
    # Audio thread
    # ------------------------------------------------------------------

    def push_samples(self, samples: np.ndarray):
        """Called from audio source with float32 mono or stereo chunk."""
        if samples.ndim > 1:
            self._pcm.add_float(samples.flatten(), samples.shape[1])
        else:
            self._pcm.add_mono(samples)

    # ------------------------------------------------------------------
    # Render thread
    # ------------------------------------------------------------------

    def update(self):
        """
        Call once per render frame (on render thread).
        Runs the PCM→FFT pipeline and updates the shared FrameData.
        """
        wave_l, wave_r, spec_l, spec_r = self._pcm.update_frame()

        # Average stereo spectrum
        spectrum = (spec_l + spec_r) * 0.5

        freqs = np.linspace(0, SAMPLE_RATE / 2, SPECTRUM_SAMPLES, dtype=np.float32)

        bass = self._band_mean(spectrum, freqs, 20, 250)
        mid = self._band_mean(spectrum, freqs, 250, 4000)
        treble = self._band_mean(spectrum, freqs, 4000, 16000)
        rms = float(np.sqrt(np.mean(wave_l ** 2)))

        # Beat detection
        self._energy_history.append(bass)
        mean_e = np.mean(self._energy_history) + 1e-9
        beat = False
        if self._beat_cooldown == 0 and bass > BEAT_THRESHOLD * mean_e and rms > 0.01:
            beat = True
            self._beat_cooldown = BEAT_COOLDOWN_FRAMES
        elif self._beat_cooldown > 0:
            self._beat_cooldown -= 1

        # Mel bands (64) — log-spaced, normalized
        mel = self._mel_bands(spectrum, freqs, MEL_BANDS)

        with self._lock:
            self._frame = FrameData(
                waveform=wave_l,
                spectrum=mel,
                raw_spectrum=spectrum,
                bass=bass,
                mid=mid,
                treble=treble,
                rms=rms,
                beat=beat,
            )

    def read_frame(self) -> "FrameData":
        with self._lock:
            return self._frame

    # ------------------------------------------------------------------

    @staticmethod
    def _band_mean(spec, freqs, lo, hi):
        mask = (freqs >= lo) & (freqs < hi)
        return float(np.mean(spec[mask])) if mask.any() else 0.0

    @staticmethod
    def _mel_bands(spec: np.ndarray, freqs: np.ndarray, n: int = 64) -> np.ndarray:
        """Map linear spectrum to n log-spaced mel bands, normalized 0-1."""
        mel_min = 2595 * np.log10(1 + 20 / 700)
        mel_max = 2595 * np.log10(1 + 16000 / 700)
        pts = np.linspace(mel_min, mel_max, n + 2)
        hz = 700 * (10 ** (pts / 2595) - 1)
        bands = np.zeros(n, dtype=np.float32)
        for i in range(n):
            mask = (freqs >= hz[i]) & (freqs < hz[i + 2])
            if mask.any():
                bands[i] = float(np.mean(spec[mask]))
        peak = bands.max()
        if peak > 0 and np.isfinite(peak):
            bands /= peak
        return bands


def _zero_wave():
    return np.zeros(WAVEFORM_SAMPLES, dtype=np.float32)

def _zero_mel():
    return np.zeros(MEL_BANDS, dtype=np.float32)

def _zero_spec():
    return np.zeros(SPECTRUM_SAMPLES, dtype=np.float32)


@dataclass
class FrameData:
    """Snapshot of one audio frame, shared between audio and render threads."""
    waveform: np.ndarray = field(default_factory=_zero_wave)
    spectrum: np.ndarray = field(default_factory=_zero_mel)
    raw_spectrum: np.ndarray = field(default_factory=_zero_spec)
    bass: float = 0.0
    mid: float = 0.0
    treble: float = 0.0
    rms: float = 0.0
    beat: bool = False

    def is_silent(self) -> bool:
        return self.rms < 0.001

    def band_energy(self, band: str) -> float:
        """Return energy for 'bass', 'mid', or 'treble'."""
        return {"bass": self.bass, "mid": self.mid, "treble": self.treble}.get(band, 0.0)
