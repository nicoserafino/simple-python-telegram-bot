import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = 'YOUR_BOT_TOKEN_HERE'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None, stk=None, audio=None, doc=None, fw=None, chat=None, chat1=None, chat2=None, chat3=None, chat4=None, chat5=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg,
                    'disable_web_page_preview': 'true',
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            elif stk:
                resp = urllib2.urlopen(BASE_URL + 'sendSticker', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'sticker': stk,
                })).read()
            elif audio:
                resp = urllib2.urlopen(BASE_URL + 'sendAudio', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'audio': audio,
                })).read()
            elif doc:
                resp = urllib2.urlopen(BASE_URL + 'sendDocument', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'document': doc,
                })).read()
            elif fw:
                resp = urllib2.urlopen(BASE_URL + 'forwardMessage', urllib.urlencode({
                    'chat_id': fw,
                    'from_chat_id': str(chat_id),
                    'message_id': str(message_id),
                })).read()
            elif chat:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': 'target_chat_id',
                    'text': chat.replace("=SEND=", "").encode('utf-8'),
                    'disable_web_page_preview': 'true',
                })).read()
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text.lower() == '/start' or text.lower() == '/start@name_of_your_bot':
                reply('Bot enabled.\nSend /command to list functions.')
                setEnabled(chat_id, True)
            elif text.lower() == '/stop' or text.lower() == '/stop@name_of_your_bot':
                reply('Bot disabled.\nSend /start to enable.')
                setEnabled(chat_id, False)
        if text.lower() == '/command'
            reply('Hello! I\'m a bot.')

        # CUSTOMIZE FROM HERE 
		# Testo			reply('testo')
        # Immagini		reply(img=urllib2.urlopen('https://telegram.org/img/t_logo.png').read())
		# Sticker		reply(stk='file_id')
		# Audio			reply(audio='file_id')
		# Documenti		reply(doc='file_id')
		# you can find file_id in log section of your Google Cloud Console sending files to the bot 

        elif text.lower() != 'suggest' and 'suggest' in text.lower():
			reply(fw='your_chat_id')
			reply('Thank you for suggestion!')
        elif text.startswith('=SEND='):
			reply(chat=text)
        else:
            if getEnabled(chat_id):
				if 'Hello' in text.lower():
					reply('Hello!')
				if 'Who are you' in text.lower():
					reply('I\'m a bot! My name is TeleBot')
				if 'sticker' in text.lower():
					reply(stk='BQADBAADGwADTyaZAjUU-thrRuh9Ag')
				if 'image' in text.lower():
					reply(img=urllib2.urlopen('https://telegram.org/img/t_logo.png').read())
				if text == '/function' or text == '/function@name_of_your_bot':
					reply('Insert your function')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
