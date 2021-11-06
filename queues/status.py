import enum
from base.bot import bot


# Frequent error messages
VALUE_ERROR = 'Wrong format'


class StatusHandler:
    def __init__(self):
        self.reset()
        
    def error(self, error_msg):
        self.error_msg = error_msg
        self.ok = False
        
    def reset(self):
        self.ok = True
        self.error_msg = None
        self.success_msg = None
        
    def send_and_reset(self, chat_id, success_args=[], error_args=[]):
        if self.ok:
            message = self.success_msg.format(*success_args)
        else:
            message = self.error_msg.format(*error_args)
            
        bot.send_message(chat_id, message)
        self.reset()
        
        
handler = StatusHandler()
