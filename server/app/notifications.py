from .integrations.ntfyConnector import send_ntfy_notification

NOTIFICATION_TEMPLATES = {
    "google_task": {
        "title": "Nowe zadanie w Google Tasks",
        "message": 'Zadanie "{title}" zostało utworzone.',
        "tags": ["white_check_mark"],
        "action_text": "Otwórz zadanie",
        "action_url_key": "webViewLink"
    },
    "google_calendar": {
        "title": "Nowe wydarzenie w Kalendarzu Google",
        "message": 'Wydarzenie "{title}" zostało utworzone na {start_datetime}.',
        "tags": ["calendar"],
        "action_text": "Otwórz wydarzenie",
        "action_url_key": "link"
    },
    "notion_page": {
        "title": "Nowa strona w Notion",
        "message": 'Notatka "{title}" została utworzona.',
        "tags": ["notebook_with_decorative_cover"],
        "action_text": "Otwórz stronę",
        "action_url_key": "url"
    },
    "notion_shopping_list": {
        "title": "Nowa lista zakupów w Notion",
        "message": 'Lista zakupów "{title}" została utworzona.',
        "tags": ["shopping_trolley"],
        "action_text": "Otwórz listę",
        "action_url_key": "url"
    }
}

def send_notifications(responses):
    for response in responses:
        item_type = response.get("type")
        if item_type not in NOTIFICATION_TEMPLATES:
            continue

        template = NOTIFICATION_TEMPLATES[item_type]
        data = response.get("data", {})
        response_data = response.get("response", {})

        title = data.get("title", "bez tytułu")
        start_datetime = data.get("start_datetime", "nieznana data")
        
        message = template["message"].format(title=title, start_datetime=start_datetime)
        
        action_url = response_data.get(template["action_url_key"], "")
        actions = [f'view, {template["action_text"]}, {action_url}'] if action_url else None

        send_ntfy_notification(
            title=template["title"],
            message=message,
            tags=template["tags"],
            actions=actions
        )
