# encoding:utf-8

import json

from aip import AipImageClassify

import plugins
from bridge.context import ContextType
from bridge.context import Context, ContextType
from common.log import logger
from plugins import *


@plugins.register(
    name="baidu_imgrecg",
    desire_priority=10,
    hidden=False,
    desc="百度图像识别插件",
    version="1.0",
    author="Micahcce",
)
            
        
class BaiduImgRecg(Plugin):
        '''
        百度图片识别
        '''
        def __init__(self):
            super().__init__()
            try:
                pconfig = super().load_config()
                baidu_app_id = pconfig.get("baidu_imgrecg_app_id", None)
                baidu_api_key = pconfig.get("baidu_imgrecg_api_key", None)
                baidu_secret_key = pconfig.get("baidu_imgrecg_secret_key", None)
                self.client = AipImageClassify(baidu_app_id, baidu_api_key, baidu_secret_key)

                self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
                logger.info("[BAIDU_IMGRECG] inited")
            except Exception as e:
                print(f"[BAIDU_IMGRECG] inited: {e}")


        def on_receive_message(self, e_context: EventContext):
            if e_context['context'].type != ContextType.IMAGE:
                return
            
            try:
                img_path = e_context['context'].content
                data = self.baidu_imgrecg(img_path)
                
                new_data = "以下为图片识别返回结果，其中'keyword'代表图中的物体，'score'代表识别的可信度，'root'代表物体类别，请简要评论两句：" + json.dumps(data, ensure_ascii=False)
                logger.debug(f"[BAIDU_IMGRECG] modify the input = {new_data}")
            except Exception as e:
                print(f"[BAIDU_IMGRECG] get imgrecg error: {e}")
                
            e_context['context'].type = ContextType.TEXT
            e_context['context'].content = new_data
            e_context.action = EventAction.BREAK_PASS  # 事件结束，不再给下个插件处理，不交付给默认的事件处理逻辑


        def get_file_content(self, filePath):
            """ 读取图片 """
            with open(filePath, 'rb') as fp:
                return fp.read()
            

        def baidu_imgrecg(self, img_path):
            """ 
            图像识别，返回字典 
            """
            image = self.get_file_content(img_path)

            """ 如果有可选参数 """
            #options = {}
            #options["baike_num"] = 5
            #data = self.client.advancedGeneral(image, options)

            """ 调用通用物体和场景识别 """
            data = self.client.advancedGeneral(image)
            
            data = data["result"]
            
            return data

