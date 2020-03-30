import requests
from config import Config

class RocketChat():
    @classmethod
    def post(cls, message):
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': Config.auth_token,
            'X-User-Id': Config.user_id
            }
        url = f'{Config.rc_base_url}/chat.postMessage'
        data = {
                "channel": Config.rc_channel,
                "text": message,
                }
        response = requests.post(url, headers=header, data=data)

        if response:
            return True
        else:
            return False

