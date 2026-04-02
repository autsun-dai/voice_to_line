#!/usr/bin/env python3
"""从视频/音频文件中提取音频并识别语音内容"""

import os
import subprocess
import sys
import tempfile
import time
import wave

import yaml

from asr_client import ASRClient


def extract_audio(video_path: str, wav_path: str) -> bool:
    """用 ffmpeg 从视频中提取 16kHz mono PCM WAV"""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-ar", "16000", "-ac", "1", "-f", "wav",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[错误] ffmpeg 提取音频失败:\n{result.stderr}")
        return False
    return True


def stream_wav_to_asr(wav_path: str, asr: ASRClient) -> str | None:
    """读取 WAV 文件并以 PCM 流式发送到 ASR"""
    with wave.open(wav_path, "rb") as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        duration = n_frames / sample_rate
        print(f"  采样率: {sample_rate}Hz, 时长: {duration:.1f}s")

        asr.start(sample_rate=sample_rate)

        chunk_size = int(sample_rate * 0.1)  # 100ms per chunk
        while True:
            frames = wf.readframes(chunk_size)
            if not frames:
                break
            asr.send_audio(frames)

    return asr.stop()


def main():
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <视频或音频文件路径>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"[错误] 文件不存在: {video_path}")
        sys.exit(1)

    # 加载配置
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    api_key = config["dashscope"]["api_key"]
    model = config["dashscope"].get("model", "fun-asr-realtime-2026-02-28")

    asr = ASRClient(api_key=api_key, model=model)

    # 提取音频
    wav_fd, wav_path = tempfile.mkstemp(suffix=".wav", prefix="voicetoline_")
    os.close(wav_fd)
    print(f"1. 从视频中提取音频...")
    if not extract_audio(video_path, wav_path):
        os.unlink(wav_path)
        sys.exit(1)

    try:
        # 识别
        print(f"2. 发送到阿里云 ASR 识别...")
        t0 = time.time()
        text = stream_wav_to_asr(wav_path, asr)
        elapsed = time.time() - t0

        if text:
            print(f"\n✅ 识别结果 ({elapsed:.1f}s):")
            print(text)
        else:
            print(f"\n❌ 未识别到内容 ({elapsed:.1f}s)")
    finally:
        os.unlink(wav_path)


if __name__ == "__main__":
    main()
