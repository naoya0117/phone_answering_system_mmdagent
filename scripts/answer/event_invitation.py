from config import logging

INVITATION_SLOT = {
    "date" : None,
    "time" : None,
    "place": None,
    "what_to_bring": None,
    "other_info": None,
}

def answer_event_invitation(slot):
    filled_item = slot.get()
    logging.info(filled_item)

    if not filled_item["イベントの詳細"]["date"] or not filled_item["イベントの詳細"]["time"]:
        return "予定の日付と時間を教えてください."

    if not filled_item["イベントの詳細"]["place"]:
        return "場所はどちらですか？"

    if not filled_item["イベントの詳細"]["what_to_bring"]:
        return "持ち物や注意事項等はございますか"

    return None