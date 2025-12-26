# Udon4Odin

A lightweight Linux-only GUI for Odin4 to flash Samsung devices.  

**Note:** Windows is not officially supported (as there's already an "official" Windows tool). Only Linux is supported.

## Features

- Monitor device connection/disconnection in real-time.
- Flash AP, BL, CP, and CSC files.
- Reboot or reboot into download mode.
- Show progress and logs while flashing.

## Requirements

- Linux
- Python 3
- PyQt6

## Installation

1. Clone the repository:

```bash
git clone https://github.com/alarmingly/Udon4Odin/
cd Udon4Odin
````

2. Install dependencies:

```bash
pip install PyQt6
```

3. Make sure `odin4` binary is executable:

```bash
chmod +x ./assets/odin4
```

## Usage

```bash
python udon.py
```

* Select files using the buttons.
* Click **Start** to flash.
* Use **Reboot** or **Reboot Download** as needed.

## Notes

* Linux is the only supported OS.
* Use `pkexec` for elevated permissions when flashing.
* Windows users should stick with the official Odin tool.

* I am aware that this code is not good, I am not very good at coding, this is a very simple thing that i made with some help from ChatGPT