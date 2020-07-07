import requests
from pairamid_api.config import auth_token, user_id, rc_base_url, rc_channel


class RocketChat:
    @classmethod
    def post(cls, message):
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
            "X-User-Id": user_id,
        }
        url = f"{rc_base_url}/chat.postMessage"
        data = {
            "channel": rc_channel,
            "text": message,
        }
        response = requests.post(url, headers=headers, data=data)

        if response:
            return True
        else:
            return False
