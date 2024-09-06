# encoding:utf-8

from aip import AipImageClassify

import plugins
from bridge.bridge import Bridge
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from config import conf


@plugins.register(
    name="baidu_imgrecg",
    desire_priority=10,
    hidden=True,
    desc="�ٶ�ͼ��ʶ����",
    version="1.0",
    author="Micahcee",
)
            
        
class BaiduImgRecg(Plugin):
        '''
        �ٶ�ͼƬʶ��
        '''
        def __init__(self):
            super().__init__()
            try:
                self.baidu_app_id = conf().get("baidu_imgrecg_app_id", None)
                self.baidu_api_key = conf().get("baidu_imgrecg_api_key", None)
                self.baidu_secret_key = conf().get("baidu_imgrecg_secret_key", None)
                self.client = AipImageClassify(self.baidu_app_id, self.baidu_api_key, self.baidu_secret_key)

                self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
                logger.info("[baidu_imgrecg] inited")
            except Exception as e:
                print(f"[baidu_imgrecg] inited:{e}")


        def on_handle_context(self, e_context: EventContext):
            if e_context['context'].type != ContextType.TEXT:
                return
            img_path = e_context['context'].content
            
            try:
                reply = Reply()
                reply.type = ReplyType.TEXT

                data = self.baidu_imgrecg(img_path)
                data = "����ΪͼƬʶ�𷵻ؽ�����������һ�£�" + data
                print(data)
                
                reply.content = data
            except Exception as e:
                print(e)
                
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK  # �¼����������ٸ��¸��������������Ĭ�ϵ��¼������߼�


        def get_file_content(self, filePath):
            """ ��ȡͼƬ """
            with open(filePath, 'rb') as fp:
                return fp.read()
            

        def baidu_imgrecg(self, img_path):
            image = self.get_file_content(img_path)

            """ ����ͨ������ͳ���ʶ�� """
            self.client.advancedGeneral(image)

            """ ����п�ѡ���� """
            options = {}
            options["baike_num"] = 5

            """ ����������ͨ������ͳ���ʶ�� """
            data = self.client.advancedGeneral(image, options)
            return data

