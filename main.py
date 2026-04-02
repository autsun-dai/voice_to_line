#!/usr/bin/env python3
"""Voice-to-Line: 语音输入法
按住右 Alt 键录音，松开后自动识别并输入文字到光标处。
支持 Linux (X11)。
"""

import os
import sys
import time

import yaml
from pynput import keyboard

from asr_client import ASRClient
from audio_capture import AudioCapture
from text_input import type_text


def load_config(path: str = None) -> dict:
    if path is None:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        for candidate in [
            os.path.join(base, "config.yaml"),
            "config.yaml",
        ]:
            if os.path.exists(candidate):
                path = candidate
                break
    if path is None:
        raise FileNotFoundError("config.yaml")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 热键名称 → pynput Key 枚举
HOTKEY_MAP = {
    "alt_r": keyboard.Key.alt_r,
    "alt_l": keyboard.Key.alt_l,
    "ctrl_r": keyboard.Key.ctrl_r,
    "ctrl_l": keyboard.Key.ctrl_l,
    "super_r": keyboard.Key.cmd_r,
    "super_l": keyboard.Key.cmd_l,
    "menu": keyboard.Key.menu,
}


class VoiceInput:
    def __init__(self, config: dict):
        ds_cfg = config["dashscope"]
        audio_cfg = config["audio"]
        hotkey_cfg = config["hotkey"]

        self.asr = ASRClient(
            api_key=ds_cfg["api_key"],
            model=ds_cfg.get("model", "fun-asr-realtime-2026-02-28"),
        )
        self.capture = AudioCapture(
            sample_rate=audio_cfg.get("sample_rate", 16000),
            channels=audio_cfg.get("channels", 1),
        )

        hotkey_name = hotkey_cfg.get("key", "alt_r")
        self.hotkey = HOTKEY_MAP.get(hotkey_name, keyboard.Key.alt_r)
        self.is_recording = False

    def on_press(self, key):
        if key == self.hotkey and not self.is_recording:
            self.is_recording = True
            print("\n🎤 录音中... (松开按键结束)")
            try:
                self.asr.start(sample_rate=self.capture.sample_rate)
                self.capture.start_recording(chunk_callback=self.asr.send_audio)
            except Exception as e:
                print(f"[错误] 无法开始录音: {e}")
                self.is_recording = False

    def on_release(self, key):
        if key == self.hotkey and self.is_recording:
            self.is_recording = False
            self._process_audio()

    def _process_audio(self):
        """停止录音和识别 → 输入文字"""
        t0 = time.time()
        print("⏳ 正在处理...")

        self.capture.stop_recording()
        text = self.asr.stop()
        elapsed = time.time() - t0

        if text:
            print(f"✅ 识别结果 ({elapsed:.1f}s): {text}")
            if type_text(text):
                print("📝 已输入到光标处")
            else:
                print("[提示] 输入失败，识别结果: " + text)
        else:
            print(f"❌ 未识别到有效内容 ({elapsed:.1f}s)")

    def run(self):
        """启动语音输入守护进程"""
        hotkey_name = self.hotkey.name if hasattr(self.hotkey, "name") else str(self.hotkey)

        print("=" * 40)
        print("  VoiceToLine 语音输入法已启动")
        print(f"  按住 {hotkey_name} 键开始录音，松开结束")
        print("  按 Ctrl+C 退出")
        print("=" * 40)

        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


def main():
    try:
        config = load_config()
    except FileNotFoundError:
        print("[错误] 找不到 config.yaml，请确保在项目目录下运行")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[错误] config.yaml 格式错误: {e}")
        sys.exit(1)

    api_key = config.get("dashscope", {}).get("api_key", "")
    if not api_key or api_key == "YOUR_DASHSCOPE_API_KEY_HERE":
        print("[错误] 请在 config.yaml 中填入你的阿里云 DashScope API Key")
        print("       获取地址: https://dashscope.console.aliyun.com/apiKey")
        sys.exit(1)

    app = VoiceInput(config)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 已退出")


if __name__ == "__main__":
    main()
