"""
openai image service
"""
import json

import openai

from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from image.image import Image
import requests
from common import const
import datetime, random

class OpenaiImage(Image):
    def __init__(self):
        openai.api_key = conf().get("open_ai_api_key")
        openai.api_base = conf().get("open_ai_api_base") or "https://api.openai.com/v1/chat/completions"

    def imageRecg(self, image_path):
        logger.debug("[Openai] image file name={}".format(image_path))
        try:
            reply = Reply()
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
                
            #session_id = e_context["context"]["session_id"]
            #if content != "":
            #    Bridge().get_bot("chat").sessions.session_reply(content, session_id)
            
            reply = Reply(ReplyType.TEXT, content)

            logger.info("[Openai] imageRecg content={} image file name={}".format(content, image_path))
        except Exception as e:
            reply = Reply(ReplyType.ERROR, "我暂时还无法看见您的图片，请稍后再试吧~")
        finally:
            return reply


