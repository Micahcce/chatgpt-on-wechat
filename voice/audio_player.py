import io

import pyaudio
import wave
from pydub import AudioSegment

from common.log import logger


class AudioPlayer:
    def __init__(self):
        self.file_path = None
        self.audio = None
        self.stream = None
        self.p = pyaudio.PyAudio()

    def play(self, file_name):
        self.file_path = file_name
        # 根据文件类型播放音频
        if self.file_path.endswith('.wav'):
            self._play_wav()
        elif self.file_path.endswith('.mp3'):
            self._play_mp3()
        else:
            raise ValueError("Unsupported file format. Only .wav and .mp3 are supported.")

    def _play_wav(self):
        # 打开 WAV 文件
        wf = wave.open(self.file_path, 'rb')

        # 创建音频流
        self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                  channels=wf.getnchannels(),
                                  rate=wf.getframerate(),
                                  output=True)

        # 读取数据并播放
        data = wf.readframes(1024)
        while data:
            self.stream.write(data)
            data = wf.readframes(1024)

        # 关闭文件
        wf.close()

    def _play_mp3(self):
        # 使用 pydub 打开并解码 MP3 文件
        self.audio = AudioSegment.from_mp3(self.file_path)

        # 打开音频流
        self.stream = self.p.open(format=self.p.get_format_from_width(self.audio.sample_width),
                                  channels=self.audio.channels,
                                  rate=self.audio.frame_rate,
                                  output=True)

        # 将音频数据转换为字节流
        data = io.BytesIO(self.audio.raw_data)

        # 每次读取 1024 个字节并播放
        chunk_size = 1024
        chunk = data.read(chunk_size)

        while chunk:
            self.stream.write(chunk)
            chunk = data.read(chunk_size)
            
        self._close_stream()
        logger.debug("Finished playing audio.")

    def _close_stream(self):
        # 停止播放并清理资源
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def terminate(self):
        # 关闭 PyAudio 实例
        if self.p:
            self.p.terminate()

