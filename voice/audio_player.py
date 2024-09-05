import io
import threading
import queue
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
        self.lock = threading.Lock()  # 用于线程安全
        self.is_playing = False  # 标识当前是否有音频正在播放
        self.queue = queue.Queue()  # 播放队列
        
        # 播放线程
        self.play_thread = threading.Thread(target=self._process_queue)
        self.play_thread.daemon = True
        self.play_thread.start()

    def play(self, file_name):
        # 将请求加入队列
        self.queue.put(file_name)
        logger.debug(f"Added {file_name} to the queue.")

    def _process_queue(self):
        while True:
            # 等待播放队列中的下一个文件
            file_name = self.queue.get()
            with self.lock:
                self.is_playing = True
                self.file_path = file_name

                # 根据文件类型选择播放方式
                if self.file_path.endswith('.wav'):
                    self._play_wav()
                elif self.file_path.endswith('.mp3'):
                    self._play_mp3()
                else:
                    logger.error("Unsupported file format. Only .wav and .mp3 are supported.")
                    self.is_playing = False

            self.queue.task_done()

    def _play_wav(self):
        try:
            wf = wave.open(self.file_path, 'rb')
            self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                      channels=wf.getnchannels(),
                                      rate=wf.getframerate(),
                                      output=True)

            data = wf.readframes(1024)
            while data:
                self.stream.write(data)
                data = wf.readframes(1024)

            wf.close()
        finally:
            self._close_stream()
            self.is_playing = False

    def _play_mp3(self):
        try:
            self.audio = AudioSegment.from_mp3(self.file_path)
            self.stream = self.p.open(format=self.p.get_format_from_width(self.audio.sample_width),
                                      channels=self.audio.channels,
                                      rate=self.audio.frame_rate,
                                      output=True)

            data = io.BytesIO(self.audio.raw_data)
            chunk_size = 1024
            chunk = data.read(chunk_size)

            while chunk:
                self.stream.write(chunk)
                chunk = data.read(chunk_size)

        finally:
            self._close_stream()
            self.is_playing = False
            logger.debug("Finished playing audio.")

    def _close_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def terminate(self):
        if self.p:
            self.p.terminate()
