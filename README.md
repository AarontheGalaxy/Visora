# Visora

A real-time desktop music visualizer that reacts to any sound on your computer.
It captures system audio, microphone input, a specific application, or an audio file,
and renders GPU-accelerated animations synchronized to the music.

Built on top of the projectM audio analysis engine with a clean, accessible user interface
designed so that anyone — including first-time users — can get it running in minutes.

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

- **Audio Source** — what sound to listen to (your whole computer, one specific app, microphone, or a file)
- **Visualization Mode** — the style of animation (Abstract plasma, Spectrum bars, Waveform, or Particles)
- **Preset** — a saved combination of colours and visual settings
- **Color Palette** — the main colour scheme

Click Launch and a full-screen or windowed animation starts, reacting to the music in real time.

---

## System Requirements

| | Minimum |
|---|---|
| Operating System | macOS 12, Windows 10, or Ubuntu 20.04 (or newer) |
| Python | 3.10 or newer |
| GPU | Any GPU with OpenGL 3.3 support (integrated graphics is fine) |
| RAM | 4 GB |
| Disk space | 500 MB (includes all Python packages) |

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

Move this folder to a place that is easy to find again, such as your Desktop.

### Step 2 — Install Python

1. Open Safari or Chrome and go to: `https://www.python.org/downloads/`
2. Click the large yellow button that says **Download Python 3.x.x**.
   Any version that starts with 3.10 or higher is fine.
3. Open the `.pkg` file that was downloaded and follow the steps in the installer.
4. When the installer finishes, it will open a Finder window with a file called
   **Install Certificates.command**. Double-click that file and let it run.
   It will open a Terminal window and close automatically when done.

To verify that Python is installed correctly:

1. Press `Command + Space` on your keyboard, type `Terminal`, and press Enter.
   A white or black text window will open.
2. Type the following line exactly and press Enter:

```
python3 --version
```

You should see a response like `Python 3.12.4`. If you see that, Python is ready.

### Step 3 — Install the required packages

In the Terminal window, type the following command and press Enter.
This installs all the software Visora needs to run.

```
python3 -m pip install moderngl PyOpenGL dearpygui numpy scipy librosa sounddevice soundcard Pillow pygame
```

You will see a lot of text as packages download and install. This can take
two to five minutes depending on your internet speed. When it is finished
you will see a line that says `Successfully installed`.

If you see a warning about pip being out of date, you can ignore it.

### Step 4 — Grant macOS permissions (first run only)

macOS protects audio access. The first time Visora tries to capture sound,
macOS will ask you for permission.

- For **System Audio** and **Window / App** mode: macOS will show a dialog that says
  it needs **Screen Recording** permission. Click **Allow**.
- For **Microphone** mode: macOS will ask for **Microphone** permission. Click **Allow**.

If you accidentally clicked Don't Allow, go to:
System Settings > Privacy & Security > Screen Recording (or Microphone)
and turn on the toggle for Terminal.

You only need to grant these permissions once.

### Step 5 — Run Visora

In the Terminal, navigate to the `visora-main` folder you downloaded.
If you put it on your Desktop, type this and press Enter:

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

On the GitHub page, click the green **Code** button near the top, then click **Download ZIP**.

Open your Downloads folder. You will see a file called `visora-main.zip`.
Right-click it and select **Extract All**. When asked where to extract,
choose your Desktop and click **Extract**.

You will get a folder called `visora-main` on your Desktop.

### Step 2 — Install Python

1. Open your browser and go to: `https://www.python.org/downloads/windows/`
2. Click the top result that says **Python 3.x.x** (the latest version).
3. On the next page, scroll down to the **Files** section.
   Click the link that says **Windows installer (64-bit)** to download it.
4. Open the installer file from your Downloads folder.

**This step is critical:** On the very first screen of the installer you will
see a small checkbox at the bottom that says **Add Python to PATH**.
Check that box before you click anything else.
If you do not check it, Visora will not be able to run.

After checking that box, click **Install Now** and follow the remaining steps.

To verify Python is installed:

1. Press the Windows key on your keyboard. Type `cmd` and press Enter.
   A black window called **Command Prompt** will open.
2. Type the following and press Enter:

```
python --version
```

You should see something like `Python 3.12.4`.
If you see an error, go back and reinstall Python, making sure to check
**Add Python to PATH**.

### Step 3 — Install the required packages

In the Command Prompt window, navigate to the `visora-main` folder.
If you extracted it to your Desktop, type this and press Enter:

```
cd %USERPROFILE%\Desktop\visora-main
```

Then install the packages:

```
python -m pip install moderngl PyOpenGL dearpygui numpy scipy librosa sounddevice soundcard Pillow pygame
```

Wait until you see `Successfully installed` before continuing.

### Step 4 — Run Visora

In the Command Prompt, from the `visora-main` folder, type:

```
python main.py
```

The Visora setup window will appear.

**About system audio on Windows:**
Visora uses Windows WASAPI loopback to capture desktop audio without any
extra software. If the visualizer is not reacting to sound, right-click the
speaker icon in the taskbar, open **Sound settings**, and make sure your
speakers or headphones are set as the default playback device.

---

## Installation — Linux

These instructions are written for Ubuntu 20.04 and newer, and other Debian-based
distributions. For Fedora, replace `apt` with `dnf`. For Arch Linux, use `pacman`.

### Step 1 — Download Visora

If you have `git` installed, clone the repository:

```bash
git clone https://github.com/AarontheGalaxy/visora.git
cd visora
```

If you do not have git, download the ZIP from GitHub
(click **Code** > **Download ZIP**), then open a Terminal and run:

```bash
cd ~/Downloads
unzip visora-main.zip
cd visora-main
```

### Step 2 — Install Python and system libraries

Run these commands one at a time in the Terminal:

```bash
sudo apt update
```

```bash
sudo apt install python3 python3-pip python3-dev portaudio19-dev libsndfile1 ffmpeg
```

Verify Python is ready:

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
python3 -m pip install --user moderngl PyOpenGL dearpygui numpy scipy librosa sounddevice soundcard Pillow pygame
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

A quick way to navigate to the folder on macOS and Linux:

```
cd ~/Desktop/visora-main
```

On Windows:

```
cd %USERPROFILE%\Desktop\visora-main
```

---

## Using the App

### Left panel — Audio Source and Visualization Mode

**Audio Source**

| Option | What it does |
|---|---|
| System Audio | Captures all sound playing on your computer — music, videos, games. |
| Microphone | Listens to your microphone. |
| Window / App | Captures audio from one specific application (e.g. Spotify, Chrome, VLC). |
| Audio File | Load an MP3, WAV, FLAC, or OGG file from your computer. |

When you choose **Window / App**, a list of running applications appears.
Use the **search box** to filter by name — type part of the app name to find it
instantly without scrolling. Click **Refresh list** if you started an app after
the Visora setup screen was already open.

When you choose **Audio File**, click **Browse** to open a file picker.

**Visualization Mode**

| Mode | Description |
|---|---|
| Abstract | Full-screen plasma animation inspired by Milkdrop. Reacts to bass, mids, and treble. The most visually striking mode. |
| Spectrum | Frequency bars. Left side shows bass (low sounds), right side shows treble (high sounds). |
| Waveform | An oscilloscope line that shows the raw shape of the audio wave. |
| Particles | Sparks that burst outward on every beat. Best for energetic music. |

### Right panel — Presets, Colors, and Window Size

**Presets**

A preset is a saved combination of colours, speed, and visual parameters.

- **Built-in** tab: presets that come with Visora. These cannot be deleted.
- **My Presets** tab: presets you have imported or added yourself.
- **Favorites** tab: presets you have bookmarked for quick access.

Click a preset to select it. The Visualization Mode on the left updates automatically.

**Color Palette**

| Palette | Description |
|---|---|
| Neon | Electric purple and teal. |
| Fire | Deep red fading to bright yellow. |
| Ice | Cool blue-white. |
| Sunset | Orange and warm gold. |
| Purple | Violet tones. |
| Mono | Pure white. Works with any mode. |

**Window Size**

| Option | Notes |
|---|---|
| 1280 x 720 | Standard HD. Runs on any machine including older laptops. |
| 1920 x 1080 | Full HD. |
| 2560 x 1440 | 2K resolution. Requires a more capable GPU. |
| Fullscreen | Takes over the entire screen. Press ESC to exit. |

### In-app help

Click **? Help & Guide** at the top of the setup screen to open the built-in
documentation. Every feature is explained there in full detail.

Every section also has a small **?** button next to its heading that opens the
relevant help topic directly. Hovering over any control shows a short tooltip.

---

## Keyboard Shortcuts

These shortcuts work while the Visora animation window is running.

| Key | Action |
|---|---|
| TAB | Cycle to the next visualization mode |
| ESC | Close the visualizer |
| F | Toggle the FPS and performance overlay |

---

## Presets and Favorites

### Adding a preset manually

Presets are JSON files stored here:

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
  "description": "A short description",
  "author": "Your name",
  "builtin": false
}
```

Valid values for `mode`: `Abstract`, `Spectrum`, `Waveform`, `Particles`.

### Managing favorites

Click any preset in the list, then click **Favorite** to bookmark it.
Click **Unfav** to remove it. Favorites are saved automatically.

---

## Importing Milkdrop (.milk) Presets

Milkdrop presets are visual programs originally made for the Winamp media player.
Thousands of free presets are available online and work with Visora.

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
5. The preset appears in **My Presets** immediately.
6. Click it, then click **Launch**.

Simple `.milk` presets (colours, zoom, rotation) import fully and run in
Abstract mode. Complex presets with custom shader code may render with
reduced detail, as full HLSL compilation is not yet supported.

---

## Troubleshooting

### "python3 is not recognized" or "python is not recognized"

Python is not installed or not on your PATH.

- On Windows: reinstall Python and check **Add Python to PATH** during setup.
- On macOS: make sure you downloaded Python from `python.org` and ran the
  Install Certificates script after installing.
- On Linux: run `sudo apt install python3`.

### "No module named X" error

A required package is missing. Run this from the `visora-main` folder:

**macOS and Linux:**
```
python3 -m pip install moderngl PyOpenGL dearpygui numpy scipy librosa sounddevice soundcard Pillow pygame
```

**Windows:**
```
python -m pip install moderngl PyOpenGL dearpygui numpy scipy librosa sounddevice soundcard Pillow pygame
```

### The visualizer does not react to sound

- Confirm something is playing on your computer with the volume turned up.
- **macOS**: System Settings > Privacy & Security > Screen Recording —
  make sure Terminal has permission. Repeat for Microphone.
- **Windows**: right-click the speaker in the taskbar > Sound settings —
  confirm your playback device is the default.
- **Linux**: run `pulseaudio --check -v` to confirm it is running.
- Test with **Microphone** mode: speak into your microphone to see if
  the visualizer reacts at all.

### Two Visora windows opened at the same time

Close both windows, then delete this file:

- macOS / Linux: `~/.visora/app.lock`
- Windows: `C:\Users\YourName\.visora\app.lock`

Then run `python3 main.py` once.

### The animation is choppy or slow

- Switch to a smaller window size (1280 x 720 is the fastest).
- Use Spectrum or Waveform mode instead of Abstract or Particles.
- Close GPU-heavy applications (browsers with video, games).
- On a laptop, plug in the charger — battery saving reduces GPU performance.
- Press **F** to see the FPS counter.

### On macOS: "macOS cannot verify the developer"

1. Go to System Settings > Privacy & Security.
2. Scroll down and click **Allow Anyway** next to the Visora message.

---

## Credits

**projectM** — `https://github.com/projectM-visualizer/projectm`
Copyright (C) 2003-2024 projectM Team. LGPL v2.1.
`audio/milkdrop_fft.py` and `audio/pcm_buffer.py` are direct Python ports
of projectM's MilkdropFFT.cpp and PCM.cpp.

**MilkdropFFT algorithm** — Copyright 2005-2013 Nullsoft, Inc. BSD-style license.

**moderngl** — `https://github.com/moderngl/moderngl` — MIT License

**Dear PyGui** — `https://github.com/hoffstadt/DearPyGui` — MIT License

**pygame** — `https://www.pygame.org` — LGPL License

**librosa** — `https://librosa.org` — ISC License

**sounddevice / soundcard** — MIT License

Full license text is in `LICENSE`.
