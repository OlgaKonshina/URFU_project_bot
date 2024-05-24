import telebot
import yaml
import time

with open(r"src/TGBot_config.yaml", "r") as f:
    config = yaml.safe_load(f)

token = config["token"]
chat_id = config["user_id"]


class TestTeleBot:
    def test_test(self):
        pass
    ##def test_message_handler(self):
    ##    tb = telebot.TeleBot("")
    ##    msg = self.create_text_message("/help")
##
    ##    @tb.message_handler(commands=["help", "start"])
    ##    def command_handler(message):
    ##        message.text = "got"
##
    ##    tb.process_new_messages([msg])
    ##    time.sleep(1)
    ##    assert msg.text == "got"

    ##def test_send_voice(self):
    ##   file_data = open("./test/test_data/hello_voice.wav", "rb")
    ##   tb = telebot.TeleBot(token)
    ##   msg_voice = tb.send_voice(chat_id, file_data)
    ##   assert msg_voice.voice.mime_type == "audio/ogg"
    ##   
    ##def test_send_dice(self):
    ##   tb = telebot.TeleBot(token)
    ##   msg_emoji = tb.send_dice(chat_id, emoji="🎯")
    ##   assert msg_emoji.message_id
    ##   assert msg_emoji.content_type == "dice"
