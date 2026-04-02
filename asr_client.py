import threading

import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult


class _ASRCallback(RecognitionCallback):
    """收集流式识别结果的回调，只保留完整句子"""

    def __init__(self):
        super().__init__()
        self.sentences: list[str] = []
        self._last_partial: str = ""
        self.error: str | None = None
        self._open_event = threading.Event()

    def on_event(self, result: RecognitionResult):
        sentence = result.get_sentence()
        if sentence and isinstance(sentence, dict):
            text = sentence.get("text", "")
            if not text:
                return
            if RecognitionResult.is_sentence_end(sentence):
                # 完整句子，保存并清空临时缓存
                self.sentences.append(text)
                self._last_partial = ""
            else:
                # 中间结果，只缓存最后一个
                self._last_partial = text

    def on_error(self, result: RecognitionResult):
        self.error = f"code={result.status_code}, message={result.message}"

    def on_close(self):
        # 连接关闭时，把最后一段未结束的文本也保留
        if self._last_partial:
            self.sentences.append(self._last_partial)
            self._last_partial = ""

    def on_open(self):
        self._open_event.set()

    def on_complete(self):
        pass

    def wait_open(self, timeout: float = 5.0) -> bool:
        return self._open_event.wait(timeout=timeout)


class ASRClient:
    def __init__(self, api_key: str, model: str = "fun-asr-realtime-2026-02-28"):
        dashscope.api_key = api_key
        self.model = model
        self._callback: _ASRCallback | None = None
        self._recognition: Recognition | None = None

    def start(self, sample_rate: int = 16000):
        """开始流式识别会话"""
        self._callback = _ASRCallback()
        self._recognition = Recognition(
            model=self.model,
            callback=self._callback,
            format="pcm",
            sample_rate=sample_rate,
        )
        self._recognition.start()
        # 等待 WebSocket 连接就绪后再开始录音
        if not self._callback.wait_open(timeout=5.0):
            print("[警告] ASR 连接未在 5s 内就绪")

    def send_audio(self, audio_bytes: bytes):
        """发送一段 PCM 音频数据"""
        if self._recognition:
            self._recognition.send_audio_frame(audio_bytes)

    def stop(self) -> str | None:
        """停止识别，返回完整识别文本"""
        if not self._recognition:
            return None

        self._recognition.stop()
        self._recognition = None

        if self._callback and self._callback.error:
            print(f"[错误] ASR 识别失败: {self._callback.error}")
            return None

        if self._callback and self._callback.sentences:
            return "".join(self._callback.sentences).strip()

        return None
