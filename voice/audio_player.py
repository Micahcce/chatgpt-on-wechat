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
        # �����ļ����Ͳ�����Ƶ
        if self.file_path.endswith('.wav'):
            self._play_wav()
        elif self.file_path.endswith('.mp3'):
            self._play_mp3()
        else:
            raise ValueError("Unsupported file format. Only .wav and .mp3 are supported.")

    def _play_wav(self):
        # �� WAV �ļ�
        wf = wave.open(self.file_path, 'rb')

        # ������Ƶ��
        self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                  channels=wf.getnchannels(),
                                  rate=wf.getframerate(),
                                  output=True)

        # ��ȡ���ݲ�����
        data = wf.readframes(1024)
        while data:
            self.stream.write(data)
            data = wf.readframes(1024)

        # �ر��ļ�
        wf.close()

    def _play_mp3(self):
        # ʹ�� pydub �򿪲����� MP3 �ļ�
        self.audio = AudioSegment.from_mp3(self.file_path)

        # ����Ƶ��
        self.stream = self.p.open(format=self.p.get_format_from_width(self.audio.sample_width),
                                  channels=self.audio.channels,
                                  rate=self.audio.frame_rate,
                                  output=True)

        # ����Ƶ����ת��Ϊ�ֽ���
        data = io.BytesIO(self.audio.raw_data)

        # ÿ�ζ�ȡ 1024 ���ֽڲ�����
        chunk_size = 1024
        chunk = data.read(chunk_size)

        while chunk:
            self.stream.write(chunk)
            chunk = data.read(chunk_size)
            
        self._close_stream()
        logger.debug("Finished playing audio.")

    def _close_stream(self):
        # ֹͣ���Ų�������Դ
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def terminate(self):
        # �ر� PyAudio ʵ��
        if self.p:
            self.p.terminate()

