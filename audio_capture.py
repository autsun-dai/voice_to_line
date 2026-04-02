import numpy as np
import sounddevice as sd


class AudioCapture:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._stream: sd.InputStream | None = None
        self._chunk_callback = None  # 实时音频帧回调

    def start_recording(self, chunk_callback=None):
        """开始录音。chunk_callback(bytes) 会在每帧音频时被调用，用于流式传输。"""
        self._chunk_callback = chunk_callback
        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
        except sd.PortAudioError as e:
            print(f"[错误] 无法打开麦克风: {e}")
            raise

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        if status:
            print(f"[警告] 录音状态: {status}")
        if self._chunk_callback:
            self._chunk_callback(indata.tobytes())

    def stop_recording(self):
        """停止录音"""
        if self._stream is None:
            return

        self._stream.stop()
        self._stream.close()
        self._stream = None
        self._chunk_callback = None
