import os
import json
import requests
from urllib.parse import quote_plus
from .operations import read_json_file


class JarvisBot:
    token = os.environ.get("api_token")  # bot tokken
    base_url = f"https://api.telegram.org/bot{token}"  # base url for all api requests
    private_token = os.environ.get("private_token")  # the bot will report errors here (fill with personal chat id)

    def __init__(self, personality="./database/personality.json", active=False):
        self.personality = read_json_file(personality)
        self.active = active

    def get_msg_list(self):
        url = f"{self.base_url}/getUpdates"
        response = requests.get(url)
        message_list = json.loads(response.content)['result']

        # check if server responded with ok and message_list isn't empty
        if response.status_code == 200 and len(message_list) > 0:
            return message_list
        elif len(message_list) == 0:
            self.send(self.private_token, "Error: Message list is empty, please fix by sending a message.")
            new_url = f"{self.base_url}/getUpdates?timeout=100&offset=10"
            return json.loads(requests.get(new_url).content)['result']
        elif response.status_code != 200:
            self.get_msg_list()

    def get_last_msg(self, offset, timeout=100, recursion_depth=30):
        url = f"{self.base_url}/getUpdates?timeout={timeout}&offset={offset+1}"
        response = requests.get(url)
        message_list = json.loads(response.content)['result']

        if len(message_list) > 0:
            return message_list[-1]
        elif recursion_depth == 0:
            return []
        else:
            if recursion_depth == 30:
                self.send(self.private_token, "Error: Message list is empty, please fix by sending a message.")
            return self.get_last_msg(10, 300, recursion_depth-1)

    def send(self, chat_id, text):
        url = f"{self.base_url}/sendAudio?chat_id={chat_id}&text={quote_plus(text, safe='')}"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content)['result']
        else:
            self.send(chat_id, text)

    def edit_msg(self, chat_id, message_id, text):
        url = f"{self.base_url}/editMessageText?chat_id={chat_id}" \
              f"&message_id={message_id}&text={quote_plus(text, safe='')}"
        message = requests.get(url)
        return json.loads(message.content)['result']

    def del_msg(self, chat_id, message_id):
        url = f"{self.base_url}/deleteMessage?chat_id={chat_id}&message_id={message_id}"
        message = requests.get(url)
        return json.loads(message.content)['result']