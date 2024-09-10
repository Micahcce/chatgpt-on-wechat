"""
Auto-replay chat robot abstract class
"""


from bridge.context import Context
from bridge.reply import Reply
from bot.session_manager import SessionManager


class Bot(object):
    def reply(self, query, context: Context = None) -> Reply:
        """
        bot auto-reply content
        :param req: received message
        :return: reply content
        """
        raise NotImplementedError
