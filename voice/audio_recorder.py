import pyaudio
import keyboard
import wave
import numpy as np

from common.tmp_dir import TmpDir
from common.log import logger


class AudioRecorder:
    def __init__(self):
        # 参数设置
        self.chunk = 1024  # 每个缓冲区的帧数
        self.format = pyaudio.paInt16  # 采样位数
        self.channels = 1  # 单声道
        self.rate = 16000  # 采样频率44100（百度语音识别仅支持16K或8K）
        self.record_seconds = 60  # 最大录音时长（以防长时间无声）
        self.voice_threshold = 700  # 声音检测阈值
        self.silence_chunks = 30   #允许的连续静音块数，超出该数停止录音。（每秒采样块数=RATE/CHUNK）
        self.pressdown_chunks = 10   #按键检测块数，超出该数录音有效
        self.output_filepath = TmpDir().path() + "record_output.wav"  # 录音保存文件
        
        # PyAudio和流对象
        self.p = pyaudio.PyAudio()
        self.stream = None

    def _print_volume(self, data):
        """ 用于调试：打印当前音量的大小，返回值为均值绝对值 """
        audio_data = np.frombuffer(data, np.int16)
        volume = np.abs(audio_data).mean()
        print(f"当前音量：{volume}")  # 打印音量大小

    def _open_stream(self):
        """打开音频流"""
        self.stream = self.p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
    
    def _close_stream(self):
        """关闭音频流"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
    def terminate(self):
        if self.p:
            self.p.terminate()

    def listen_record(self):
        """ 录音函数，根据声音阈值和沉默块数自动控制录音 """
        self._open_stream()

        frames = []
        record_silent_chunks = 0  # 记录连续静音块数
        start_recording = False
        # print("等待检测到声音...")
        
        while True:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            #self._print_volume()   #打印音量大小

            if np.max(np.frombuffer(data, np.int16)) < self.voice_threshold:    #判断数据是否低于阈值，低于则认为是安静
                record_silent_chunks += 1
                if start_recording and record_silent_chunks >= self.silence_chunks:
                    logger.info("录音完成。")
                    break
            else:
                record_silent_chunks = 0  # 发现有声音时重置静音计数

                if not start_recording:
                    logger.info("声音检测到，开始录音...")
                    start_recording = True

            # 录音状态下才存储音频数据
            if start_recording:
                frames.append(data)

            # 防止录音时间过长
            if len(frames) >= (self.rate // self.chunk) * self.record_seconds:
                logger.warning("达到最大录音时长。")
                break

        self._close_stream()
        self._save_to_wave(frames)
        return self.output_filepath
    
    def shiftkey_record(self):
        """ 录音函数，按压左shift键录音 """
        self._open_stream()
        
        frames = []
        pressdown_num = 0
        #print("按下左shift键开始录音")
        
        while True:
            while keyboard.is_pressed("LEFT_SHIFT"):
                if pressdown_num == 0:
                    logger.info("开始录音...")
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                pressdown_num += 1
            if pressdown_num and pressdown_num >= self.pressdown_chunks:
                break
            elif pressdown_num:
                pressdown_num = 0
                logger.warning("录音时间过短，请按下左shift重新录制")
            
        logger.info("录音完成。")
        
        self._close_stream()
        self._save_to_wave(frames)
        return self.output_filepath
        
    def _save_to_wave(self, frames):
        try:
            # 保存音频文件
            wf = wave.open(self.output_filepath, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            logger.warning(f"Error saving WAV file: {e}")
            
