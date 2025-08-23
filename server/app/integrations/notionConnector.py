import os
from notion_client import Client

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

notion = Client(auth=NOTION_API_KEY)

def create_notion_page(data: dict, parent_id: str):
    """
    Accepts structured data and creates a regular Notion page using the official Notion SDK.
    `data` should contain at least 'title' and optionally 'content'.
    """
    title = data.get("title", "Untitled")
    content = data.get("content", "")

    result = notion.pages.create(
        parent={"type": "page_id", "page_id": parent_id},
        properties={
            "title": [
                {
                    "type": "text",
                    "text": {"content": title}
                }
            ]
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content}
                        }
                    ]
                }
            }
        ]
    )
    return {
        'success': True,
        'url': result.get('url'),
        'page_data': result
    }