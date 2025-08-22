
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NTFY_CHANNEL = os.getenv("NTFY_CHANNEL")
NTFY_URL = f"https://ntfy.sh/{NTFY_CHANNEL}"

def send_ntfy_notification(message: str, title: str = None, tags: list = None, actions: list = None):
    """
    Sends a notification to ntfy.sh channel.

    Args:
        message (str): The message to send.
        title (str, optional): The title of the notification. Defaults to None.
        tags (list, optional): A list of tags (emojis are supported). Defaults to None.
        actions (list, optional): A list of action buttons. Defaults to None.
    """
    headers = {}
    if title:
        headers["Title"] = title
    if tags:
        headers["Tags"] = ",".join(tags)
    if actions:
        headers["Actions"] = "; ".join(actions)

    response = requests.post(NTFY_URL, data=message.encode('utf-8'), headers=headers)
    return response
