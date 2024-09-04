import pyaudio
import wave
import numpy as np
from common.tmp_dir import TmpDir


class AudioRecorder:
    def __init__(self):
        # 参数设置
        self.chunk = 1024  # 每个缓冲区的帧数
        self.format = pyaudio.paInt16  # 采样位数
        self.channels = 1  # 单声道
        self.rate = 16000  # 采样频率44100（百度语音识别仅支持16K或8K）
        self.record_seconds = 60  # 最大录音时长（以防长时间无声）
        self.voice_threshold = 500  # 声音检测阈值
        self.silence_chunks = 30   #允许的连续静音块数，超出该数停止录音。（每秒采样块数=RATE/CHUNK）
        self.output_filename = TmpDir().path() + "record_output.wav"  # 录音保存文件

    def get_volume(self, data):
        """ 获取当前音量的大小，返回值为均值绝对值 """
        audio_data = np.frombuffer(data, np.int16)
        return np.abs(audio_data).mean()

    def is_silent(self, data):
        """ 判断数据是否低于阈值，低于则认为是安静 """
        return np.max(np.frombuffer(data, np.int16)) < self.voice_threshold

    def record(self):
        """ 录音函数，根据声音阈值和沉默块数自动控制录音 """
        p = pyaudio.PyAudio()

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        print("等待检测到声音...")

        frames = []
        recod_silent_chunks = 0  # 记录连续静音块数
        start_recording = False

        while True:
            data = stream.read(self.chunk)
            volume = self.get_volume(data)  # 计算当前音量大小
            #print(f"当前音量：{volume}")  # 打印音量大小

            if self.is_silent(data):
                recod_silent_chunks += 1
                if start_recording and recod_silent_chunks >= self.silence_chunks:
                    print("录音结束。")
                    break
            else:
                recod_silent_chunks = 0  # 发现有声音时重置静音计数

                if not start_recording:
                    print("声音检测到，开始录音...")
                    start_recording = True

            # 录音状态下才存储音频数据
            if start_recording:
                frames.append(data)

            # 防止录音时间过长
            if len(frames) >= (self.rate // self.chunk) * self.record_seconds:
                print("达到最大录音时长。")
                break

        # 停止并关闭音频流
        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存音频文件
        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"音频已保存为 {self.output_filename}")
        return self.output_filename
     



if __name__ == '__main__':
    recorder = AudioRecorder()
    recorder.record()
