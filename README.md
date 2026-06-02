# Visora

A real-time desktop music visualizer that reacts to any sound on your computer.
It captures system audio, microphone input, a specific application, or an audio
file, and renders GPU-accelerated animations synchronized to the music.

Built on top of the projectM audio analysis engine with a clean, accessible user
interface designed so that anyone — including first-time users — can get it
running in minutes.

---

## Table of Contents

1. [What This App Does](#what-this-app-does)
2. [System Requirements](#system-requirements)
3. [Installation — macOS](#installation--macos)
4. [Installation — Windows](#installation--windows)
5. [Installation — Linux](#installation--linux)
6. [Running the App](#running-the-app)
7. [Using the App](#using-the-app)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Presets and Favorites](#presets-and-favorites)
10. [Importing Milkdrop (.milk) Presets](#importing-milkdrop-milk-presets)
11. [Troubleshooting](#troubleshooting)
12. [Credits](#credits)

---

## What This App Does

When you open Visora you see a setup screen where you choose:

- **Audio Source** — what sound to listen to (your whole computer, one specific
  app, your microphone, or an audio file)
- **Visualization Mode** — the style of animation (Abstract plasma, Spectrum
  bars, Waveform, or Particles)
- **Preset** — a saved combination of colours and visual settings
- **Color Palette** — the main colour scheme
- **Window Size** — how large the visualizer window should be

Click **Launch** and a full-screen or windowed animation starts, reacting to the
music in real time.

---

## System Requirements

| | Minimum |
|---|---|
| Operating System | macOS 12 (Monterey) or newer, Windows 10, or Ubuntu 20.04 or newer |
| Python | 3.10 or newer (3.12 recommended) |
| GPU | Any GPU with OpenGL 3.3 Core Profile support |
| RAM | 4 GB |
| Disk space | 600 MB (includes all Python packages) |

> **Apple Silicon (M1 / M2 / M3 / M4) is fully supported.**
> Visora uses GLFW for window creation, which works natively on ARM Macs.

---

## Installation — macOS

This section assumes you have never installed Python or used the Terminal before.
Follow every step in order and do not skip any.

### Step 1 — Download Visora

You are reading this on the GitHub page for Visora.

Find the green button near the top of the page that says **Code**.
Click it, then click **Download ZIP**.

A file called `visora-main.zip` will download to your Downloads folder.
Go to your Downloads folder and double-click the file to unzip it.
You will get a folder called `visora-main`.

Move this folder somewhere easy to find again, such as your Desktop.

### Step 2 — Install Python

1. Open Safari or Chrome and go to: `https://www.python.org/downloads/`
2. Click the large yellow button that says **Download Python 3.x.x**.
   Any version 3.10 or higher is fine.
3. Open the `.pkg` file that downloaded and follow the installer steps.
4. When the installer finishes, a Finder window will open showing a file called
   **Install Certificates.command**. Double-click it and let it run.
   It opens a Terminal window and closes automatically when done.

To check Python is installed:

1. Press `Command + Space`, type `Terminal`, and press Enter.
2. Type the following and press Enter:

```
python3 --version
```

You should see something like `Python 3.12.4`. If you do, Python is ready.

### Step 3 — Install the required packages

In the Terminal, type this command exactly and press Enter:

```
python3 -m pip install moderngl PyOpenGL pyglet dearpygui numpy scipy librosa sounddevice soundcard Pillow
```

This downloads and installs all the software Visora needs. It can take two to
five minutes. When it finishes you will see `Successfully installed`.

If you see a warning about pip being out of date, you can safely ignore it.

### Step 4 — Grant macOS permissions (first run only)

macOS protects audio access. The first time Visora captures sound, macOS will
ask for permission.

- **System Audio** and **Window / App**: macOS will ask for **Screen Recording**
  permission. Click **Allow**.
- **Microphone**: macOS will ask for **Microphone** permission. Click **Allow**.

If you accidentally clicked "Don't Allow", go to:
**System Settings → Privacy & Security → Screen Recording** (or Microphone)
and turn on the toggle for Terminal.

You only need to do this once.

### Step 5 — Run Visora

In Terminal, navigate to the `visora-main` folder. If you put it on your
Desktop, type:

```
cd ~/Desktop/visora-main
```

Then start the app:

```
python3 main.py
```

The Visora setup window will appear on your screen.

---

## Installation — Windows

### Step 1 — Download Visora

On the GitHub page, click the green **Code** button near the top, then click
**Download ZIP**.

Open your Downloads folder. You will see a file called `visora-main.zip`.
Right-click it and select **Extract All**. When asked where to extract, choose
your Desktop and click **Extract**.

You will get a folder called `visora-main` on your Desktop.

### Step 2 — Install Python

1. Open your browser and go to: `https://www.python.org/downloads/windows/`
2. Click the top result that says **Python 3.x.x** (the latest version).
3. Scroll down to the **Files** section and click
   **Windows installer (64-bit)**.
4. Open the installer from your Downloads folder.

**Critical:** On the very first screen of the installer there is a small
checkbox at the bottom that says **Add Python to PATH**.
**Check that box before clicking anything else.**
If you miss it, Visora will not be able to run.

After checking the box, click **Install Now** and follow the remaining steps.

To verify Python installed correctly:

1. Press the Windows key, type `cmd`, and press Enter.
2. In the Command Prompt window, type:

```
python --version
```

You should see something like `Python 3.12.4`. If you see an error, reinstall
Python and make sure to check **Add Python to PATH**.

### Step 3 — Install the required packages

In Command Prompt, navigate to the `visora-main` folder. If you extracted it to
your Desktop, type:

```
cd %USERPROFILE%\Desktop\visora-main
```

Then install the packages:

```
python -m pip install moderngl PyOpenGL pyglet dearpygui numpy scipy librosa sounddevice soundcard Pillow
```

Wait until you see `Successfully installed` before continuing.

### Step 4 — Run Visora

In Command Prompt, from the `visora-main` folder, type:

```
python main.py
```

The Visora setup window will appear.

**About system audio on Windows:**
Visora uses Windows WASAPI loopback to capture desktop audio without any extra
software. If the visualizer does not react to sound, right-click the speaker
icon in the taskbar, open **Sound settings**, and confirm your speakers or
headphones are set as the default playback device.

---

## Installation — Linux

These instructions are for Ubuntu 20.04 and newer and other Debian-based
distributions. For Fedora, replace `apt` with `dnf`. For Arch Linux, use
`pacman`.

### Step 1 — Download Visora

If you have `git` installed:

```bash
git clone https://github.com/AarontheGalaxy/visora.git
cd visora
```

If not, download the ZIP from GitHub (click **Code** → **Download ZIP**), then:

```bash
cd ~/Downloads
unzip visora-main.zip
cd visora-main
```

### Step 2 — Install Python and system libraries

```bash
sudo apt update
```

```bash
sudo apt install python3 python3-pip python3-dev portaudio19-dev libsndfile1 ffmpeg libglfw3 libglfw3-dev
```

Verify Python:

```bash
python3 --version
```

### Step 3 — Set up PulseAudio

Visora uses PulseAudio to capture system-wide audio on Linux.

```bash
sudo apt install pulseaudio pulseaudio-utils
```

Make sure PulseAudio is running:

```bash
pulseaudio --check -v
```

If it says it is not running, start it:

```bash
pulseaudio --start
```

### Step 4 — Install the required packages

From inside the `visora-main` folder:

```bash
python3 -m pip install --user moderngl PyOpenGL pyglet dearpygui numpy scipy librosa sounddevice soundcard Pillow
```

### Step 5 — Run Visora

```bash
python3 main.py
```

---

## Running the App

Every time you want to start Visora, open a Terminal or Command Prompt,
navigate to the `visora-main` folder, and run:

**macOS and Linux:**
```
python3 main.py
```

**Windows:**
```
python main.py
```

Navigate to the folder quickly:

**macOS / Linux:**
```
cd ~/Desktop/visora-main
```

**Windows:**
```
cd %USERPROFILE%\Desktop\visora-main
```

---

## Using the App

### Left panel — Audio Source and Visualization Mode

#### Audio Source

| Option | What it does |
|---|---|
| System Audio | Captures all sound playing on your computer — music, videos, games, browser tabs. |
| Microphone | Listens to your microphone. Good for live instruments, singing, or clapping. |
| Window / App | Captures audio from one specific running application (e.g. Spotify, Chrome, VLC). |
| Audio File | Load an MP3, WAV, FLAC, or OGG file from your computer. |

**When you choose Window / App:**

1. A list of currently running applications appears automatically.
2. Use the **search box** to filter by name — type part of the app name to find
   it instantly.
3. Click the app you want. A green **✓ AppName** label appears below the list
   to confirm your selection.
4. Click **Refresh list** if you started an app after the Visora setup screen
   was already open.

**When you choose Audio File:**

Click **Browse…** to open a file picker. Supported formats: MP3, WAV, FLAC, OGG.

#### Visualization Mode

| Mode | Description |
|---|---|
| Abstract | Full-screen plasma shader inspired by Milkdrop. Reacts to bass, mids, and treble simultaneously. The most visually impressive mode. |
| Spectrum | Classic frequency bars — left side = bass (low sounds), right side = treble (high sounds). The taller a bar, the louder that frequency. |
| Waveform | An oscilloscope line showing the raw shape of the audio wave. Good for seeing the detail of instruments and vocals. |
| Particles | Sparks that burst outward on every beat. More bass = bigger burst. Great for energetic music like EDM or hip-hop. |

---

### Right panel — Presets, Colors, and Window Size

#### Presets

A preset is a saved combination of colours, speed, and visual parameters — like
a "theme" for the visualizer.

The preset browser has four tabs:

| Tab | Contents |
|---|---|
| **All** | Every preset in one list — the easiest place to browse. |
| **Built-in** | Presets that come with Visora. These cannot be deleted. |
| **My Presets** | Presets you have imported or saved yourself. |
| **Favorites ★** | Presets you have bookmarked for quick access. |

Click any preset to select it. The **Visualization Mode** on the left updates
automatically to match the preset.

**Preset action buttons:**

- **★ Favorite** — bookmark the selected preset. Click again to remove.
- **Import .milk** — import a Milkdrop preset file (see section below).
- **? .milk guide** — open the built-in guide for importing Milkdrop presets.

#### Color Palette

The palette controls the main colours of the visualizer. It blends with the
preset's own colour settings.

| Palette | Description |
|---|---|
| Neon | Electric purple and teal. Vivid and cyberpunk. |
| Fire | Deep red fading to bright yellow. Hot and energetic. |
| Ice | Cool blue-white. Calm and clean. |
| Sunset | Orange and warm gold. Relaxed and warm. |
| Purple | Violet tones. Great for lo-fi or ambient. |
| Mono | Pure white. Minimal, works with any mode. |

#### Window Size

| Option | Notes |
|---|---|
| 1280 × 720 | Standard HD. Works on any display, including older laptops. |
| 1920 × 1080 | Full HD. Sharp on large screens. |
| 2560 × 1440 | 2K. Requires a more capable GPU. |
| Fullscreen | Takes over the entire screen. Press ESC to exit. |

---

### In-app help

Click **? Help & Guide** at the top of the setup screen to open the built-in
documentation. Every feature is explained there in full.

Each section also has a small **?** button next to its heading that opens the
relevant help topic directly.

---

## Keyboard Shortcuts

These shortcuts work while the Visora animation window is running.

| Key | Action |
|---|---|
| TAB | Cycle to the next visualization mode |
| ESC | Close the visualizer and return to the setup screen |
| F | Toggle the FPS / performance overlay |

---

## Presets and Favorites

### Adding a preset manually

Presets are JSON files stored in your home folder:

**macOS and Linux:**
```
~/.visora/presets/
```

**Windows:**
```
C:\Users\YourName\.visora\presets\
```

Create a `.json` file in that folder with this structure:

```json
{
  "name": "My Preset",
  "mode": "Abstract",
  "params": {
    "color_a": [0.1, 0.0, 0.5],
    "color_b": [0.0, 1.0, 0.8],
    "zoom": 1.1,
    "rotation": 0.4
  },
  "description": "A short description of what it looks like",
  "author": "Your name",
  "builtin": false
}
```

Valid values for `"mode"`: `Abstract`, `Spectrum`, `Waveform`, `Particles`.

All `params` values are optional. If a key is missing, the default value is
used. Color values are RGB floats between 0.0 and 1.0.

### Managing favorites

Click any preset in the list, then click **★ Favorite** to bookmark it.
The preset instantly appears in the **Favorites ★** tab.
Click **★ Unfav** to remove it. Favorites are saved automatically and
remembered every time you open the app.

---

## Importing Milkdrop (.milk) Presets

Milkdrop presets are visual programs originally made for the Winamp media
player. Thousands of free presets are available online and work with Visora.

### Where to find .milk files

- Official projectM preset collection:
  `https://github.com/projectM-visualizer/presets-milkdrop-converted`
- Search GitHub for `milkdrop presets`
- Winamp forums and SourceForge archives

### How to import

1. Download a `.milk` file to your computer.
2. Open Visora and go to the setup screen.
3. In the **Presets** section, click **Import .milk**.
4. Browse to the `.milk` file and select it.
5. The preset appears in **My Presets** and **All** immediately.
6. Click it, then click **Launch**.

Simple `.milk` presets (colours, zoom, rotation) import fully and run in
Abstract mode. Complex presets with custom HLSL shader code are mapped to
Abstract mode with the colour parameters extracted.

---

## Troubleshooting

### "python3 is not recognized" or "python is not recognized"

Python is not installed or not on your PATH.

- **Windows:** reinstall Python and check **Add Python to PATH** during setup.
- **macOS:** make sure you downloaded Python from `python.org` and ran the
  Install Certificates script after installing.
- **Linux:** run `sudo apt install python3`.

### "No module named X" error

A required package is missing. Run this from inside the `visora-main` folder:

**macOS and Linux:**
```
python3 -m pip install moderngl PyOpenGL pyglet dearpygui numpy scipy librosa sounddevice soundcard Pillow
```

**Windows:**
```
python -m pip install moderngl PyOpenGL pyglet dearpygui numpy scipy librosa sounddevice soundcard Pillow
```

### The visualizer does not react to sound

- Make sure something is playing on your computer with the volume turned up.
- **macOS:** System Settings → Privacy & Security → Screen Recording — make
  sure Terminal has permission. Repeat for Microphone if using that mode.
- **Windows:** right-click the speaker icon in the taskbar → Sound settings —
  confirm your playback device is set as the default.
- **Linux:** run `pulseaudio --check -v` to confirm PulseAudio is running.
- Test with **Microphone** mode: speak into your mic to check if the
  visualizer reacts at all.

### The visualizer window does not appear after clicking Launch

- Wait up to five seconds — the window opens in a separate process and may
  take a moment to appear.
- Check the Terminal for any error messages printed after clicking Launch.
- Make sure `pyglet` is installed: `python3 -m pip install pyglet`
- **Linux:** make sure GLFW system libraries are installed:
  `sudo apt install libglfw3 libglfw3-dev`

### Two Visora windows opened at the same time

Close both windows, then delete this file:

- **macOS / Linux:** `~/.visora/app.lock`
- **Windows:** `C:\Users\YourName\.visora\app.lock`

Then run `python3 main.py` again.

### The animation is choppy or slow

- Switch to a smaller window size (1280 × 720 is the fastest).
- Use **Spectrum** or **Waveform** mode instead of **Abstract** or
  **Particles** — shader modes are more GPU-intensive.
- Close other GPU-heavy applications (browsers with video, games).
- On a laptop, plug in the charger — battery saving mode throttles the GPU.
- Press **F** inside the visualizer to see the actual FPS counter.

### On macOS: "macOS cannot verify the developer"

1. Go to System Settings → Privacy & Security.
2. Scroll down and click **Allow Anyway** next to the Visora message.

### On macOS: OpenGL error or black window

Make sure you are running Python 3.10 or newer and that `pyglet` is installed:

```
python3 -m pip install --upgrade pyglet moderngl
```

If the problem persists, your GPU may not support OpenGL 3.3 Core Profile.
Integrated Intel graphics on very old Macs (pre-2012) do not support it.

---

## Credits

**projectM** — `https://github.com/projectM-visualizer/projectm`  
Copyright (C) 2003-2024 projectM Team. LGPL v2.1.  
`audio/milkdrop_fft.py` and `audio/pcm_buffer.py` are direct Python ports of
projectM's `MilkdropFFT.cpp` and `PCM.cpp`.

**MilkdropFFT algorithm** — Copyright 2005-2013 Nullsoft, Inc. BSD-style license.

**moderngl** — `https://github.com/moderngl/moderngl` — MIT License

**GLFW / pyglet** — `https://www.glfw.org` — zlib/libpng License  
Cross-platform OpenGL window and context management.

**Dear PyGui** — `https://github.com/hoffstadt/DearPyGui` — MIT License

**librosa** — `https://librosa.org` — ISC License

**sounddevice / soundcard** — MIT License

Full license text is in `LICENSE`.
