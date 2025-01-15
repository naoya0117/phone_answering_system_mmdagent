from answer.event_invitation import INVITATION_SLOT, answer_event_invitation
from answer.sales import answer_sales
from answer.tasks import answer_task, TASK_SLOT
from config import logging

def add_slot_category(slot, category):
    """
    カテゴリに応じたスロットを追加
    Parameters:
    slot : object
        The slot object to which a category will be added.
    """
    logging.info(f"category:{category}")
    match category:
        case _ if "イベント" in category:
            slot.add_slot("イベントの詳細", INVITATION_SLOT)
        case _ if "タスク" in category:
            slot.add_slot("タスクの詳細", TASK_SLOT)

    slot.add_slot("その他の情報", None)

def answer_by_category(category, slot):
    """
    Provides functionality to generate an appropriate response

    based on a given category and slot.

    Parameters:
    category : str
        The category of the event or invitation, used to determine the type of
        response. Expected to be a specific category describing the context.
    slot : any
        An additional parameter, potentially meant for further customization
        of the response based on the provided category.

    Returns:
    str
        A string representing the response corresponding to the given category.
    """
    match category:
        case "遊びやイベント，行事などの参加の可否":
            return answer_event_invitation(slot)
        case _ if "セールス" in category:
            return answer_sales()
        case _ if "タスク" in category:
            return answer_task(slot)

    return None