import requests
import json


class Caller(object):
    def __init__(self, user, key, nick=None):
        self.user = user
        self.key = key
        self.nick = nick

        requests.post('https://cleverbot.io/1.0/create', json={
            'user': user,
            'key': key,
            'nick': nick
        })

    def ask(self, text):
        req = requests.post('https://cleverbot.io/1.0/ask', json={
            'user': self.user,
            'key': self.key,
            'nick': self.nick,
            'text': text
        })

        r = json.loads(req)
        if r['status'] == 'success':
            return r['response']
        else:
            return False
