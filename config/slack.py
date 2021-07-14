from slacker import Slacker

class Slack():
    def __init__(self):
        self.token = 'xoxb-2257324003063-2272279572627-pokjoriZAUtbkVk4h0RR2RcJ'
        
    def notification(self, pretext=None, title=None, fallback=None, text=None):
        attachments_dist    = dist()
        attachments_dist['pretext'] = pretext   #kikicom1
        attachments_dist['title']   = title     #kikicom2
        attachments_dist['fallback']=fallback   #kikicom3
        attachments_dist['text']    = text      #kikicom3
        
        attachments     = [attachments_dist]
        
        slack = Slacker(self.token)
        
        slack.chat.post_message(channel='#kikicom', text=None, attachments=attachments, as_user=None)
        