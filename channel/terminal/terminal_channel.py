import sys
import threading

from numpy import record

from bridge.context import *
from bridge.reply import Reply, ReplyType
from channel.chat_channel import ChatChannel, check_prefix
from channel.chat_message import ChatMessage
from common.log import logger
from config import conf
from voice.audio_recorder import AudioRecorder
from voice.audio_player import AudioPlayer


class TerminalMessage(ChatMessage):
    def __init__(
        self,
        msg_id,
        content,
        ctype,
        from_user_id="User",
        to_user_id="Chatgpt",
        other_user_id="Chatgpt",
    ):
        self.msg_id = msg_id
        self.ctype = ctype
        self.content = content
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.other_user_id = other_user_id


class TerminalChannel(ChatChannel):
    def __init__(self):
        super().__init__()
        self.NOT_SUPPORT_REPLYTYPE = []
        self.msg_id = 0
        self.lock = threading.Lock()  # 用于控制对msg_id的访问
        self.auto_record = False
    
    def send(self, reply: Reply, context: Context):
        if context.type == ContextType.VOICE:
            print(context["user_text"])

        print("\nBot:")
        if reply.type == ReplyType.VOICE:
            print(context["bot_text"])
            self.player.play(reply.content)
        elif reply.type == ReplyType.IMAGE:
            from PIL import Image

            image_storage = reply.content
            image_storage.seek(0)
            img = Image.open(image_storage)
            print("<IMAGE>")
            img.show()
        elif reply.type == ReplyType.IMAGE_URL:  # 从网络下载图片
            import io

            import requests
            from PIL import Image

            img_url = reply.content
            pic_res = requests.get(img_url, stream=True)
            image_storage = io.BytesIO()
            for block in pic_res.iter_content(1024):
                image_storage.write(block)
            image_storage.seek(0)
            img = Image.open(image_storage)
            print(img_url)
            img.show()
        else:
            print(reply.content)
        print("\nUser:", end="")
        sys.stdout.flush()
        return

    def startup(self):
        context = Context()
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        logger.setLevel("DEBUG")
        print("\n请输入您的问题（或按下右Shift键开始录音，可输入'toggle'切换为自动录音）:\nUser:", end="")
        sys.stdout.flush()
        
        # 创建线程，用于监听语音录制
        audio_thread = threading.Thread(target=self.record_audio)
        audio_thread.daemon = True              # 设置为守护线程，以便主线程结束后，子线程也会结束
        audio_thread.start()

        while True:
            try:
                prompt = self.get_input()
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit()
                
            if prompt == "toggle":
                self.auto_record = not self.auto_record
                self.recorder.stop_record()
                if self.auto_record:
                    print("已切换到监听模式\nUser:", end="")
                else:
                    print("已切换到按键模式\nUser:", end="")
                continue
                
            with self.lock:
                self.msg_id += 1
                
            #trigger_prefixs = conf().get("single_chat_prefix", [""])
            #if check_prefix(prompt, trigger_prefixs) is None:
            #    prompt = trigger_prefixs[0] + prompt  # 给没触发的消息加上触发前缀

            context = self._compose_context(ContextType.TEXT, prompt, msg=TerminalMessage(self.msg_id, prompt, ContextType.TEXT))
            context["isgroup"] = False
            if context:
                self.produce(context)
            else:
                raise Exception("context is None")

    def get_input(self):
        """
        Multi-line input function
        """
        sys.stdout.flush()
        line = input()
        return line

    def record_audio(self):
        while True:
            try:
                if self.auto_record == True:
                    record_file = self.recorder.listen_record()
                else:
                    record_file = self.recorder.shiftkey_record()
                    
                if record_file == None:     # 切换模式时返回 None
                    continue
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit()
                
            with self.lock:
                self.msg_id += 1

            context = self._compose_context(ContextType.VOICE, record_file, msg=TerminalMessage(self.msg_id, record_file, ContextType.VOICE))
            context["isgroup"] = False
            if context:
                self.produce(context)
            else:
                raise Exception("context is None")



