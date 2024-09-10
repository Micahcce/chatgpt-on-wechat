# encoding:utf-8

import json
import base64

import openai
from bridge.bridge import Bridge

import plugins
from bridge.context import Context, ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *


@plugins.register(
    name="Imgrecg",
    desire_priority=10,
    hidden=False,
    desc="图像识别插件",
    version="1.0",
    author="Micahcce",
)
            
        
class ImgRecg(Plugin):
        '''
        OpenAI图片识别，基于gpt-4o模型
        '''
        def __init__(self):
            super().__init__()
            try:
                # set the default api_key
                openai.api_key = conf().get("open_ai_api_key")
                if conf().get("open_ai_api_base"):
                    openai.api_base = conf().get("open_ai_api_base")

                self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
                logger.info("[IMGRECG] inited")
            except Exception as e:
                logger.warning(f"[IMGRECG] inited: {e}")


        def on_handle_context(self, e_context: EventContext):
            if e_context['context'].type != ContextType.TEXT:
                return
            try:
                reply = Reply()
                image_path = e_context['context'].content
                base64_image = self.encode_image(image_path) # 获取编码
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o",                         # 固定模型名称: gpt-4o
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": ""},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                )
                content = response.choices[0].message["content"]
                
                session_id = e_context["context"]["session_id"]
                if content != "":
                    Bridge().get_bot("chat").sessions.session_reply(content, session_id)
                e_context['reply'].type = ReplyType.TEXT
                e_context['reply'].content = content
                e_context.action = EventAction.BREAK_PASS  # 事件结束，不再给下个插件处理，不交付给默认的事件处理逻辑
                
                logger.debug(f"[IMGRECG] get imgrecg info = {content}")
            except Exception as e:
                logger.warning(f"[IMGRECG] get imgrecg error: {e}")

        def encode_image(self, image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

