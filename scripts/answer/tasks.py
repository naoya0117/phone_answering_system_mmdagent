from config import logging

TASK_SLOT = {
    "date" : None,
    "time" : None,
    "task" : None,
    "other_info": None,
}

def answer_task(slot):
    filled_item = slot.get()
    logging.info(filled_item)

    if not filled_item["タスクの詳細"]["task"]:
        return "何をする必要がありますか"
    if not filled_item["タスクの詳細"]["date"] and not filled_item["タスクの詳細"]["time"]:
        return "いつまでに対応が必要ですか？"

    return None