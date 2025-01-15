import openai
from config import logging
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class Slot:
    def __init__(self, slot_item=None):
        self.__slot_item = slot_item or {}

    def get(self):
        return self.__slot_item
        
    def is_slot_filled_by_key(self, key):
        return all(self.__slot_item[key].values())


    def fill_by_ai(self, message):
        """
        ChatGPTを利用して、スロットを埋める関数。
        Args: message: ユーザーからの入力メッセージ。
        """
        try:
            system_message = {
                "role": "system",
                "content": (
                    "あなたは、与えられた情報を識別する.jsonのapiプログラムのUPDATEメソッドです"
                    "ユーザの日本語による自然言語による入力に対し、すでにある情報も含めて"
                    "当てはまる情報をjson形式で埋めて返してください。"
                    "情報がない項目はnullを入れること.しかし，明らかな間違いでない場合は，既存要素をnullで更新しないこと．"
                    "ないことが明示されている場合は，nullではなく，無しです．"
                    "日本語で入力された語句のニュアンスは大事にしてください.これ以外の文字列は出力しないでください。"
                    "与えられている情報と出力形式は以下の通り.オブジェクトのキーの名前は絶対に変えないこと"
                    "値を返すときにキーの名前が元のデータと一致していることと内容が正しいことを必ず確認してください"
                    f"{json.dumps(self.__slot_item)}"
                )
            }

            user_message = {"role": "user", "content": message}

            # ChatCompletion APIのリクエスト
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[system_message, user_message]
            )

            # レスポンスの取得
            logging.info(response.choices[0].message.content)
            response_content = response.choices[0].message.content

            if response_content:
                format_response = response_content.replace("```json", "").replace("```", "")
                ai_response_json = json.loads(format_response)
                for key, value in ai_response_json.items():
                    if key in self.__slot_item:
                        self.__slot_item[key] = value
            else:
                logging.warning("AIの応答に期待される'content'が含まれていません。")


        except json.JSONDecodeError as e:
            logging.error(f"JSONデコードエラー: {e}")
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")

        return self.__slot_item

    def detect_category_by_ai(self, category_list):
        """
        対話のカテゴリの分類分けをするメソッド
        Args:
            category_list (list[str]): A list of category names represented
            as strings.

        Returns:
            str: The name of the detected category as predicted by the AI model.

        Raises:
            ValueError: If the provided category_list is empty.
            TypeError: If category_list contains non-string elements.
        """
        if not category_list:
            raise ValueError("Category list cannot be empty.")

        try:
            system_message = {
                "role": "system",
                "content": (
                    "あなたは，与えられたjson形式の情報と，カテゴリのリストから対話の内容を分類するモジュールです"
                    "対話の内容は以下の通りです．"
                    f"{json.dumps(self.__slot_item)}"
                    "カテゴリのリストは以下の通りです"
                    f"{category_list}"
                    "カテゴリのリストの中から最もマッチする要素一個のみを抽出し，要素のみの形式で返してください"
                    "回答を返すときに，与えられたカテゴリのリストの要素と一致するかを確認してください．"
                    "また，分類分けも正確にお願いします．"
                    "要素のみを返し，余計な文字列は出力しないこと"
                ),
            }
            user_message = {
                "role": "user",
                "content": "最もマッチする単語を教えてください．"
            }

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[system_message, user_message]
            )

            # レスポンスの取得
            logging.info("detect_category_by_ai:")
            logging.info(response.choices[0].message.content)
            response_content = response.choices[0].message.content

            if not response_content:
                logging.warning("AIの応答に期待される'content'が含まれていません。")
                return None

            return response_content


        except Exception as e:
            logging.error("予期しないエラー: %s", e)

    def add_slot(self, key, value):
        self.__slot_item[key] = value
        return self.__slot_item

    def summary(self):
        try:
            system_message = {
                "role": "system",
                "content": (
                    "あなたは，与えられたjson形式の情報と，カテゴリのリストから対話の内容を分類するモジュールです"
                    "対話の内容は以下の通りです．"
                    f"{json.dumps(self.__slot_item)}"
                    "対話の内容を要約して返してください"
                ),
            }
            user_message = {
                "role": "user",
                "content": "わかりやすく要約してください"
            }

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_message, user_message]
            )

            # レスポンスの取得
            logging.info("detect_category_by_ai:")
            logging.info(response.choices[0].message.content)
            response_content = response.choices[0].message.content

            if not response_content:
                logging.warning("AIの応答に期待される'content'が含まれていません。")
                return None

            return response_content

        except Exception as e:
            logging.error(e)

