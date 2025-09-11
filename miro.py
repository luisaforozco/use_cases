import requests
import miro_api
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BOARD_ID = os.getenv("BOARD_ID")

url = f"https://api.miro.com/v2/boards/{BOARD_ID}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def check_connection():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("✅ Access token is valid.")
        return True
    else:
        print("❌ Access token is invalid or expired.")
        print("Status code:", response.status_code)
        print("Response:", response.json())
        return False


def create_sticky_note(note_text, color, x, y, width: float = 300):
    payload = {
        "data": {
            "content": note_text,
            "shape": "square"
        },
        "style": {
            "fillColor": color
        },
        "position": {
            "origin": "center",
            "x": x,
            "y": y
        },
        "geometry": {
            "width": width # only one needed, object keeps aspect ratio
        }
    }
    # Option 1: direct API + requests
    url_sticky_notes = f"https://api.miro.com/v2/boards/{BOARD_ID}/sticky_notes"
    response = requests.post(url_sticky_notes, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Error creating sticky note: {response.text}")
    return response.json().get("id")

    # Option 2: using miro_api python package
    #api = miro_api.MiroApi(ACCESS_TOKEN)
    #sticky = api.create_sticky_note_item(
    #    board_id=BOARD_ID,
    #    sticky_note_create_request=payload,
    #)

def create_shape(
    x: float,
    y: float,
    shape: str = "rectangle",
    width: float = 300,
    height: float = 200,
    fill_color: str = "#FFD966",
    border_color: str = "#1a1a1a",
    content: str | None = None,     # optional text inside the shape (HTML allowed)
    parent_frame_id: str | None = None,
):
    # Decided not to use because MIRO doesn't adapt the text size to the shape, while for sticky notes it does automatically.
    payload = {
        "data": {
            "shape": shape,   # shape type
            # Miro shapes accept rich-text HTML; keep it simple with <p>...</p>
            **({"content": f"<p>{content}</p>"} if content else {}),
        },
        "style": {
            "fillColor": fill_color,
            "borderColor": border_color # can also set e.g. "border_style": "normal", "text_color": "#000000", etc.
        },
        "position": {
            "origin": "center",
            "x": x,
            "y": y,
        },
        "geometry": {
            "width": width,
            "height": height,
        },
        # Attach to a frame if provided
        **({"parent": {"id": parent_frame_id}} if parent_frame_id else {}),
    }

    # Option 1: using requests directly
    url_shapes = f"https://api.miro.com/v2/boards/{BOARD_ID}/shapes"
    response = requests.post(url_shapes, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Error creating shape: {response.text}")
    return response.json()

    # Option 2: Using miro_api
    # api = miro_api.MiroApi(ACCESS_TOKEN)
    # return api.create_shape_item(
    #     board_id=BOARD_ID,
    #     shape_create_request=payload,
    # )

def create_connector(source_id, target_id, caption=None, font_size=14,color="#1a1a1a", shape="elbowed"):
    """
    Create a connection (line/arrow) between two objects on the Miro board.
    docs: https://developers.miro.com/reference/create-connector
    - source_id: ID of the source object
    - target_id: ID of the target object
    - caption: Optional text label for the connection
    - color: Line color (hex)
    - shape: "elbowed" or "straight"
    Returns the connection object ID.
    """
    url_connectors = f"https://api.miro.com/v2/boards/{BOARD_ID}/connectors"
    payload = {
        "startItem": {"id": source_id},
        "endItem": {"id": target_id},
        "style": {
            "color": color,
            "strokeColor": color,
            "strokeStyle": "normal",
            "fontSize": font_size,
        },
        "shape": shape,  # "elbowed" or "straight",
        "captions": [
            {"content": caption if caption else ""}
        ],
    }
    response = requests.post(url_connectors, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error creating connector: {response.text}")
    return response.json().get("id")