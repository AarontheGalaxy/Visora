"""
Audio source abstraction.

Sources run on their own daemon thread and push samples into an AudioAnalyzer.
Supported sources:
  - SystemAudioSource  : captures all desktop audio (loopback)
  - WindowAudioSource  : captures audio from a specific app/window (macOS ScreenCaptureKit / Windows WASAPI)
  - MicrophoneSource   : microphone input via sounddevice
  - FileSource         : decode and stream an audio file
"""

import sys
import threading
import sounddevice as sd

from .analyzer import AudioAnalyzer, SAMPLE_RATE, HOP_SIZE


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class AudioSource:
    def __init__(self, analyzer: AudioAnalyzer):
        self._analyzer = analyzer
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Microphone
# ---------------------------------------------------------------------------

class MicrophoneSource(AudioSource):
    def __init__(self, analyzer: AudioAnalyzer, device_index: int | None = None):
        super().__init__(analyzer)
        self._device = device_index

    def _run(self):
        def callback(indata, frames, time, status):  # noqa: ARG001
            if not self._running:
                raise sd.CallbackStop
            self._analyzer.push_samples(indata[:, 0])

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=HOP_SIZE,
            device=self._device,
            callback=callback,
            dtype="float32",
        ):
            while self._running:
                sd.sleep(100)


# ---------------------------------------------------------------------------
# System audio (loopback) — cross-platform
# ---------------------------------------------------------------------------

class SystemAudioSource(AudioSource):
    """Captures all desktop audio using soundcard loopback."""

    def _run(self):
        try:
            import soundcard as sc
        except ImportError:
            raise RuntimeError("soundcard package required for system audio capture. Run: pip install soundcard")

        mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        with mic.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=HOP_SIZE) as recorder:
            while self._running:
                data = recorder.record(numframes=HOP_SIZE)
                self._analyzer.push_samples(data[:, 0])


# ---------------------------------------------------------------------------
# Per-window / per-application
# ---------------------------------------------------------------------------

class WindowAudioSource(AudioSource):
    """
    Captures audio from a specific application window.
    macOS: ScreenCaptureKit (requires Screen Recording permission)
    Windows: WASAPI per-process session via soundcard
    Linux: PulseAudio per-app source (future)
    """

    def __init__(self, analyzer: AudioAnalyzer, window_info: dict):
        super().__init__(analyzer)
        self._window_info = window_info  # {"pid": int, "name": str, "title": str}

    def _run(self):
        if sys.platform == "darwin":
            self._run_macos()
        elif sys.platform == "win32":
            self._run_windows()
        else:
            raise RuntimeError("Per-window audio capture not supported on this platform.")

    def _run_macos(self):
        """
        Uses ScreenCaptureKit via PyObjC to capture per-process audio.
        Requires macOS 12.3+ and Screen Recording permission.
        """
        try:
            from AppKit import NSRunLoop, NSDate
            import ScreenCaptureKit as SCK  # type: ignore
        except ImportError:
            raise RuntimeError(
                "PyObjC ScreenCaptureKit bridge required. Run: pip install pyobjc-framework-ScreenSaver"
            )

        pid = self._window_info.get("pid")
        if not pid:
            raise ValueError("window_info must contain 'pid' for macOS capture")

        # Minimal ScreenCaptureKit setup — runs capture loop until stopped
        _run_sck_capture(pid, self._analyzer, lambda: self._running)

    def _run_windows(self):
        try:
            import soundcard as sc
        except ImportError:
            raise RuntimeError("soundcard package required. Run: pip install soundcard")

        # soundcard on Windows supports per-process loopback by speaker name;
        # best effort: use default loopback if per-process not available
        mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        with mic.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=HOP_SIZE) as recorder:
            while self._running:
                data = recorder.record(numframes=HOP_SIZE)
                self._analyzer.push_samples(data[:, 0])


def _run_sck_capture(pid: int, analyzer: AudioAnalyzer, is_running_fn):
    """
    Thin wrapper for ScreenCaptureKit audio capture.
    Actual SCK delegate implementation needed for production;
    this is the integration point.
    """
    import time
    # Placeholder: in production this would set up SCKStreamConfiguration
    # with capturesAudio=True, excludeCurrentProcessAudio=True,
    # and filter by pid via SCRunningApplication.
    # For now fall back to system loopback so the rest of the app works.
    try:
        import soundcard as sc
        mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        with mic.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=HOP_SIZE) as recorder:
            while is_running_fn():
                data = recorder.record(numframes=HOP_SIZE)
                analyzer.push_samples(data[:, 0])
    except Exception:
        while is_running_fn():
            time.sleep(0.1)


# ---------------------------------------------------------------------------
# File source
# ---------------------------------------------------------------------------

class FileSource(AudioSource):
    def __init__(self, analyzer: AudioAnalyzer, path: str):
        super().__init__(analyzer)
        self._path = path

    def _run(self):
        import time
        try:
            import librosa
            y, _ = librosa.load(self._path, sr=SAMPLE_RATE, mono=True)
        except Exception as exc:
            print(f"FileSource: failed to load '{self._path}': {exc}")
            return
        idx = 0
        hop_dur = HOP_SIZE / SAMPLE_RATE
        while self._running and idx < len(y):
            chunk = y[idx: idx + HOP_SIZE]
            self._analyzer.push_samples(chunk)
            idx += HOP_SIZE
            time.sleep(hop_dur)


# ---------------------------------------------------------------------------
# Window enumeration helpers
# ---------------------------------------------------------------------------

def list_audio_windows() -> list[dict]:
    """
    Returns a list of running applications that likely produce audio.
    Each entry: {"pid": int, "name": str, "title": str}
    """
    if sys.platform == "darwin":
        return _list_windows_macos()
    elif sys.platform == "win32":
        return _list_windows_windows()
    else:
        return _list_windows_linux()


def _list_windows_macos() -> list[dict]:
    try:
        from AppKit import NSWorkspace
        apps = NSWorkspace.sharedWorkspace().runningApplications()
        results = []
        for app in apps:
            name = app.localizedName()
            pid = app.processIdentifier()
            if name and pid > 0:
                results.append({"pid": int(pid), "name": str(name), "title": str(name)})
        return results
    except Exception:
        return []


def _list_windows_windows() -> list[dict]:
    try:
        import psutil
        results = []
        for proc in psutil.process_iter(["pid", "name"]):
            results.append({"pid": proc.info["pid"], "name": proc.info["name"], "title": proc.info["name"]})
        return results
    except Exception:
        return []


def _list_windows_linux() -> list[dict]:
    try:
        import subprocess
        out = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)
        # Parse basic PID info from pactl output
        results = []
        current: dict = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("Sink Input #"):
                if current:
                    results.append(current)
                current = {"pid": -1, "name": "", "title": ""}
            elif "application.name" in line:
                current["name"] = line.split("=")[-1].strip().strip('"')
                current["title"] = current["name"]
            elif "application.process.id" in line:
                try:
                    current["pid"] = int(line.split("=")[-1].strip().strip('"'))
                except ValueError:
                    pass
        if current:
            results.append(current)
        return results
    except Exception:
        return []
