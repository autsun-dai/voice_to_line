# VoiceToLine

**VoiceToLine** is a voice input tool for Ubuntu (Linux/X11) that transcribes your speech and types the recognized text directly at the current cursor position in any application — no copy-paste required.

Hold a configurable hotkey to start recording, release it to stop, and the transcribed text is automatically injected at the cursor. Powered by [Alibaba Cloud DashScope](https://dashscope.aliyun.com/) real-time ASR (Automatic Speech Recognition).

---

## Features

- 🎤 **Push-to-talk** — hold a hotkey to record, release to transcribe
- ⌨️ **Cursor injection** — recognized text is typed directly at the active cursor position via `xdotool`
- 🌊 **Streaming ASR** — audio is streamed in real time to DashScope for low-latency results
- ⚙️ **Configurable** — choose your hotkey, sample rate, and ASR model via a simple YAML file
- 🐧 **Ubuntu / Linux X11** — designed and tested on Ubuntu with the X Window System

---

## Requirements

- Ubuntu (or any Linux distro running **X11**)
- Python 3.10+
- An [Alibaba Cloud DashScope API Key](https://dashscope.console.aliyun.com/apiKey)
- `xdotool` (installed automatically by `setup.sh`)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/autsun-dai/voice_to_line.git
cd voice_to_line
```

### 2. Run the setup script

```bash
bash setup.sh
```

This installs `xdotool` (via `apt`) and all Python dependencies.

### 3. Configure your API Key

Copy the example config and fill in your DashScope API Key:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml`:

```yaml
dashscope:
  api_key: "YOUR_DASHSCOPE_API_KEY_HERE"   # <-- replace with your real key
  model: "fun-asr-realtime-2026-02-28"

audio:
  sample_rate: 16000
  channels: 1

hotkey:
  key: "alt_r"   # right Alt key — hold to record, release to stop
```

> **Security tip:** Keep your `config.yaml` private. The file is already listed in `.gitignore` so it will not be committed to Git. It is also recommended to restrict its file permissions:
> ```bash
> chmod 600 config.yaml
> ```
> Alternatively, you can set your API Key via an environment variable and read it in the config if you prefer not to store it on disk.

---

## Usage

```bash
python main.py
```

Once started:

1. Place your cursor in any text field (browser, terminal, document editor, etc.).
2. **Hold** the configured hotkey (default: **Right Alt**) — recording begins immediately.
3. **Speak** clearly into your microphone.
4. **Release** the hotkey — speech is transcribed and the text is typed at the cursor.
5. Press **Ctrl+C** in the terminal to quit.

### Available hotkeys

| Config value | Key |
|---|---|
| `alt_r` | Right Alt *(default)* |
| `alt_l` | Left Alt |
| `ctrl_r` | Right Ctrl |
| `ctrl_l` | Left Ctrl |
| `super_r` | Right Super (Win key) |
| `super_l` | Left Super (Win key) |
| `menu` | Menu key |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pynput` | Global hotkey detection |
| `sounddevice` | Microphone audio capture |
| `numpy` | Audio buffer handling |
| `PyYAML` | Configuration file parsing |
| `dashscope` | Alibaba Cloud ASR SDK |
| `xdotool` *(system)* | Typing text at cursor position |

---

## Privacy Notice

- **Your voice is sent to a third-party cloud service.** All audio captured while the hotkey is held is streamed in real time to Alibaba Cloud DashScope for speech recognition. Please review [Alibaba Cloud's Privacy Policy](https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-privacy-policy) before use.
- **No audio is saved locally.** Audio data is streamed directly to the ASR service and is not written to disk.
- **Global keyboard listener.** This tool uses a system-wide keyboard listener (via `pynput`) solely to detect the configured hotkey. No keystrokes other than the hotkey trigger are processed or recorded.
- Do not use this tool in environments where recording or transmitting voice data is restricted or prohibited.

---

## Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

The authors are not responsible for:
- Any costs incurred through usage of the Alibaba Cloud DashScope API.
- Any data privacy issues arising from voice data transmitted to third-party services.
- Any unintended text input or system behavior caused by this tool.

Use this tool at your own risk. Always ensure you comply with the terms of service of Alibaba Cloud DashScope and the data privacy regulations applicable in your jurisdiction.

---

## License

This project does not currently specify a license. All rights reserved by the author unless otherwise stated.
