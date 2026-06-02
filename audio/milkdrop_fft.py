"""
Direct Python port of projectM's MilkdropFFT.cpp
Original: Copyright 2005-2013 Nullsoft, Inc. (BSD-style license)
Source: ornekuygulamalar/projectm/src/libprojectM/Audio/MilkdropFFT.cpp

Cooley-Tukey FFT with:
  - Sine-envelope windowing (reduces spectral leakage)
  - Optional log-scale equalization (boosts highs, mimics Milkdrop)
  - Bit-reversal permutation table
"""

import math
import numpy as np


class MilkdropFFT:
    def __init__(self, samples_in: int, samples_out: int,
                 equalize: bool = True, envelope_power: float = 1.0):
        self._samples_in = samples_in
        self._num_freq = samples_out * 2

        self._envelope = self._init_envelope(envelope_power)
        self._equalize = self._init_equalize(equalize)
        self._bit_rev = self._init_bit_rev()
        self._cos_sin = self._init_cos_sin()

    # ------------------------------------------------------------------
    def time_to_freq(self, waveform: np.ndarray) -> np.ndarray:
        """
        Transform waveform samples to frequency-domain magnitudes.
        Returns array of length samples_out (= num_freq / 2).
        """
        n = self._num_freq
        spectrum = np.zeros(n, dtype=np.complex64)

        # 1. Bit-reversal reorder + envelope window
        waveform_len = len(waveform)
        for i in range(n):
            idx = self._bit_rev[i]
            if idx < waveform_len:
                spectrum[i] = complex(waveform[idx] * self._envelope[idx], 0.0)

        # 2. Cooley-Tukey in-place FFT (ported 1:1 from MilkdropFFT.cpp)
        dft_size = 2
        octave = 0
        while dft_size <= n:
            wp = self._cos_sin[octave]
            w = complex(1.0, 0.0)
            hdft = dft_size >> 1
            for m in range(hdft):
                i = m
                while i < n:
                    j = i + hdft
                    tmp = spectrum[j] * w
                    spectrum[j] = spectrum[i] - tmp
                    spectrum[i] = spectrum[i] + tmp
                    i += dft_size
                w *= wp
            dft_size <<= 1
            octave += 1

        # 3. Magnitude + equalization
        half = n // 2
        magnitudes = np.abs(spectrum[:half]) * self._equalize
        return magnitudes.astype(np.float32)

    # ------------------------------------------------------------------
    def _init_envelope(self, power: float) -> np.ndarray:
        n = self._samples_in
        if power < 0.0:
            return np.ones(n, dtype=np.float32)
        multiplier = 2.0 * math.pi / n
        base = 0.5 + 0.5 * np.sin(np.arange(n, dtype=np.float32) * multiplier - math.pi * 0.5)
        if power == 1.0:
            return base.astype(np.float32)
        return np.power(base, power).astype(np.float32)

    def _init_equalize(self, equalize: bool) -> np.ndarray:
        half = self._num_freq // 2
        if not equalize:
            return np.ones(half, dtype=np.float32)
        scaling = -0.02
        inv = 1.0 / half
        eq = np.array([
            scaling * math.log(max((half - i) * inv, 1e-9))
            for i in range(half)
        ], dtype=np.float32)
        return eq

    def _init_bit_rev(self) -> list:
        n = self._num_freq
        table = list(range(n))
        j = 0
        for i in range(n):
            if j > i:
                table[i], table[j] = table[j], table[i]
            m = n >> 1
            while m >= 1 and j >= m:
                j -= m
                m >>= 1
            j += m
        return table

    def _init_cos_sin(self) -> list:
        table = []
        dft_size = 2
        while dft_size <= self._num_freq:
            theta = -2.0 * math.pi / dft_size
            table.append(complex(math.cos(theta), math.sin(theta)))
            dft_size <<= 1
        return table
