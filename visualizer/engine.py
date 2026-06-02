"""
Visualization engine — software renderer.
Uses pygame 2D (SDL2 Metal on macOS) with numpy pixel arrays.
No OpenGL required — works on macOS 16 where OpenGL is removed/broken.
"""

import os
import sys
import time

try:
    import pygame
except ImportError:
    raise ImportError("pygame is required. Run: pip install pygame")

import numpy as np
from audio.analyzer import AudioAnalyzer
from visualizer.modes.waveform import WaveformMode
from visualizer.modes.spectrum import SpectrumMode
from visualizer.modes.particles import ParticlesMode
from visualizer.modes.abstract import AbstractMode

MODE_CLASSES = {
    "Waveform":  WaveformMode,
    "Spectrum":  SpectrumMode,
    "Particles": ParticlesMode,
    "Abstract":  AbstractMode,
}

TARGET_FPS = 60


class _EngineState:
    def __init__(self):
        self.running = False
        self.pending_mode = None
        self.pending_preset = None
        self.show_overlay = False
        self.extra_frame_hook = None

    def queue_mode(self, mode: str, preset: dict):
        self.pending_mode = mode
        self.pending_preset = preset

    def consume_pending(self):
        if self.pending_mode is None:
            return None
        result = (self.pending_mode, self.pending_preset or {})
        self.pending_mode = None
        self.pending_preset = None
        return result


class VisualizerEngine:
    def __init__(self, analyzer: AudioAnalyzer, initial_config: dict):
        self._analyzer = analyzer
        self._config = initial_config
        self._mode_instance = None
        self._state = _EngineState()

    def run(self):
        pygame.init()

        w = self._config.get("width", 1280)
        h = self._config.get("height", 720)
        fullscreen = self._config.get("fullscreen", False)

        flags = pygame.FULLSCREEN if fullscreen else 0
        screen = pygame.display.set_mode((w, h), flags)
        pygame.display.set_caption("Music Visualizer")

        # Reusable surface for fast blit (avoids creating new surface every frame)
        surf = pygame.Surface((w, h))

        self._load_mode(self._config.get("mode", "Abstract"),
                        self._config.get("preset", {}), w, h)

        self._state.running = True
        hook = self._state.extra_frame_hook
        clock = pygame.time.Clock()

        while self._state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._state.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            if hook:
                hook()

            pending = self._state.consume_pending()
            if pending:
                mode_name, preset = pending
                self._load_mode(mode_name, preset, w, h)

            frame_data = self._analyzer.read_frame()
            rgb = self._mode_instance.render(
                frame_data, self._config.get("preset", {}))

            # rgb: HxWx3 uint8 → transpose to WxHx3 for pygame surfarray
            pygame.surfarray.blit_array(surf, rgb.swapaxes(0, 1))
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            clock.tick(TARGET_FPS)

        self._cleanup()

    def _handle_key(self, key: int):
        if key == pygame.K_ESCAPE:
            self._state.running = False
        elif key == pygame.K_f:
            self._state.show_overlay = not self._state.show_overlay
        elif key == pygame.K_TAB:
            modes = list(MODE_CLASSES.keys())
            current = self._config.get("mode", "Abstract")
            try:
                idx = modes.index(current)
            except ValueError:
                idx = 0
            nxt = (idx + 1) % len(modes)
            self.set_mode(modes[nxt], self._config.get("preset", {}))

    def set_mode(self, mode_name: str, preset: dict):
        self._state.queue_mode(mode_name, preset)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def update_preset(self, preset: dict):
        self._config["preset"] = preset

    def stop(self):
        self._state.running = False

    def set_frame_hook(self, hook):
        self._state.extra_frame_hook = hook

    def _load_mode(self, mode_name: str, preset: dict, w: int, h: int):
        if self._mode_instance is not None:
            self._mode_instance.cleanup()
        cls = MODE_CLASSES.get(mode_name, AbstractMode)
        self._mode_instance = cls(w, h)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def _cleanup(self):
        if self._mode_instance:
            self._mode_instance.cleanup()
        pygame.quit()
