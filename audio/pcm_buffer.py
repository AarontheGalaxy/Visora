"""
Direct Python port of projectM's PCM.cpp ring-buffer + spectrum pipeline.
Original: Copyright (C) 2003-2024 projectM Team (LGPL v2.1)
Source: ornekuygulamalar/projectm/src/libprojectM/Audio/PCM.cpp

Double-buffered ring buffer with mutex — safe between audio thread (writer)
and render thread (reader). Mirrors projectM's UpdateFrameAudioData flow.
"""

import threading
import numpy as np
from .milkdrop_fft import MilkdropFFT

AUDIO_BUFFER_SAMPLES = 2048   # matches projectM AudioConstants.hpp
WAVEFORM_SAMPLES = 512        # matches projectM WaveformSamples
SPECTRUM_SAMPLES = 512


class PCMBuffer:
    def __init__(self):
        self._mutex = threading.Lock()

        # Ring buffers (stereo)
        self._input_l = np.zeros(AUDIO_BUFFER_SAMPLES, dtype=np.float32)
        self._input_r = np.zeros(AUDIO_BUFFER_SAMPLES, dtype=np.float32)
        self._start = 0

        # Working copies (updated each frame)
        self._wave_l = np.zeros(WAVEFORM_SAMPLES, dtype=np.float32)
        self._wave_r = np.zeros(WAVEFORM_SAMPLES, dtype=np.float32)
        self._spec_l = np.zeros(SPECTRUM_SAMPLES, dtype=np.float32)
        self._spec_r = np.zeros(SPECTRUM_SAMPLES, dtype=np.float32)

        self._fft = MilkdropFFT(
            samples_in=AUDIO_BUFFER_SAMPLES,
            samples_out=SPECTRUM_SAMPLES,
            equalize=True,
            envelope_power=1.0,
        )

    # ------------------------------------------------------------------
    # Audio thread API
    # ------------------------------------------------------------------

    def add_float(self, samples: np.ndarray, channels: int):
        """Push float32 samples. Mirrors PCM::Add(float*, channels, count)."""
        if channels < 1:
            return
        # Discard any incomplete trailing frame to prevent index overrun
        usable = (len(samples) // channels) * channels
        count = usable // channels
        with self._mutex:
            ring_indices = (self._start + np.arange(count)) % AUDIO_BUFFER_SAMPLES
            src_l = np.arange(count) * channels
            self._input_l[ring_indices] = samples[src_l]
            r_offset = 1 if channels > 1 else 0
            self._input_r[ring_indices] = samples[src_l + r_offset]
            self._start = (self._start + count) % AUDIO_BUFFER_SAMPLES

    def add_mono(self, samples: np.ndarray):
        """Convenience wrapper for mono float32."""
        n = len(samples)
        with self._mutex:
            ring_indices = (self._start + np.arange(n)) % AUDIO_BUFFER_SAMPLES
            self._input_l[ring_indices] = samples
            self._input_r[ring_indices] = samples
            self._start = (self._start + n) % AUDIO_BUFFER_SAMPLES

    # ------------------------------------------------------------------
    # Render thread API  (mirrors PCM::UpdateFrameAudioData)
    # ------------------------------------------------------------------

    def update_frame(self):
        """
        Called once per render frame.
        1. Copy ring buffer → waveform arrays (locked)
        2. Run FFT on waveform → spectrum
        Returns (wave_l, wave_r, spec_l, spec_r) as float32 arrays.
        """
        with self._mutex:
            wave_l = self._copy_waveform(self._input_l)
            wave_r = self._copy_waveform(self._input_r)

        spec_l = self._fft.time_to_freq(wave_l)
        spec_r = self._fft.time_to_freq(wave_r)

        self._wave_l = wave_l
        self._wave_r = wave_r
        self._spec_l = spec_l[:SPECTRUM_SAMPLES]
        self._spec_r = spec_r[:SPECTRUM_SAMPLES]

        return wave_l, wave_r, self._spec_l, self._spec_r

    def _copy_waveform(self, ring: np.ndarray) -> np.ndarray:
        """Read last WAVEFORM_SAMPLES from ring buffer in chronological order."""
        start = (self._start - WAVEFORM_SAMPLES) % AUDIO_BUFFER_SAMPLES
        end = start + WAVEFORM_SAMPLES
        if end <= AUDIO_BUFFER_SAMPLES:
            return ring[start:end].copy()
        return np.concatenate([ring[start:], ring[:end - AUDIO_BUFFER_SAMPLES]])
