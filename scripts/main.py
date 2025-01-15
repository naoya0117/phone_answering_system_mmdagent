from config import TEXT_INPUT_MODE, LISTENING_IP, LISTENING_PORT
from lib.input import listen_for_input, listen_for_voice
from Utils.Slot import Slot
from answer import answer_by_category, add_slot_category

import sys
import logging


sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


class ConversationHandler:

    def __init__(self):
        self.slot = Slot(slot_item={"ユーザーについての個人情報": {"organization": None, "name": None}, "相手の要求": {"content" : None, "keyword": None}})

        self.is_first_turn = True
        self.is_subject_filed = False

        self.category_list = ["遊びやイベント，行事などの参加の可否", "セールスや勧誘", "タスクの割り当て"]
        self.category = None

    def generate_answer(self, user_input):
        """
        入力データを受け取り、状態ごとの応答を生成
        """
    
        filled_slot = self.slot.fill_by_ai(message=user_input)

        if not self.slot.is_slot_filled_by_key("ユーザーについての個人情報"):
            if self.is_first_turn:
                self.is_first_turn = False
                return "こんにちは，こちらは留守番電話サービスです．" + self.generate_answer(user_input=user_input)

            if not filled_slot["ユーザーについての個人情報"]["organization"] or not filled_slot["ユーザについての個人情報"]["name"]:
                return "ご所属とお名前をお願いいたします"


        if not self.slot.is_slot_filled_by_key("相手の要求"):
            if not filled_slot["相手の要求"]["content"]:
                return f'{filled_slot["ユーザーについての個人情報"]["name"]}さんですね．ご用件をお願いします'

        if not self.category:
            self.category = self.slot.detect_category_by_ai(self.category_list)
            self.slot.fill_by_ai(message=filled_slot["相手の要求"]["content"])
            add_slot_category(slot=self.slot, category=self.category)

            category_confirm = f'''{filled_slot["相手の要求"]["keyword"] + "ですね．"
                if filled_slot["相手の要求"]["keyword"]  else ""}'''
            return category_confirm + self.generate_answer(user_input=user_input)

        category_answer = answer_by_category(slot=self.slot, category=self.category)

        if category_answer:
            return category_answer

        logging.error(f"category: {self.category}")

        return "承りました．また後日ご連絡させていただきます．" + self.slot.summary()

def main():

    conversation_handler = ConversationHandler()

    while True:
        # テキスト入力モードの場合は listen_for_input を使って入力を受け取る
        def data_handler(input_data):
            response = conversation_handler.generate_answer(input_data)
            print(f"SYNTH_START|-1|mei_voice_normal|{response}")
            return response

        if TEXT_INPUT_MODE:
            listen_for_input(
                listening_ip=LISTENING_IP,
                listening_port=LISTENING_PORT,
                data_handler=data_handler,
            )
        else:
            listen_for_voice(data_handler=data_handler)


if __name__ == "__main__":
    main()