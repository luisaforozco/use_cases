import requests
import miro_api
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BOARD_ID = os.getenv("BOARD_ID")
BASE_URL = f"https://api.miro.com/v2/boards/{BOARD_ID}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def check_connection():
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code == 200:
        print("✅ Access token is valid.")
        return True
    else:
        print("❌ Access token is invalid or expired.")
        print("Status code:", response.status_code)
        print("Response:", response.json())
        return False


def create_sticky_note(note_text: str = "", color: str = "yellow", x: float = 0.0, y: float = 0.0, width: float = 300) -> str:
    """
    Create a sticky note on the Miro board. See docs: https://developers.miro.com/reference/create-sticky-note-item
    
    Parameters:
        note_text (str): The text content of the sticky note.
        color (str): The fill color for the sticky note (Miro color name).
        x (float): X position on the board (center of the note).
        y (float): Y position on the board (center of the note).
        width (float, optional): Width of the sticky note. Default is 300.
    
    Returns:
        str: The ID of the created sticky note object.
    
    Raises:
        Exception: If the sticky note could not be created.
    """
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
            "x": float(x),
            "y": float(y)
        },
        "geometry": {
            "width": float(width)  # only one needed, object keeps aspect ratio
        }
    }
    # Option 1: direct API + requests
    url_sticky_notes = f"{BASE_URL}/sticky_notes"
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
    content: str | None = None,
    parent_frame_id: str | None = None,
) -> str:
    """
    Create a shape on the Miro board. Miro doesn't adapt the text size to the shape, while for sticky notes it does automatically.
    See docs: https://developers.miro.com/reference/create-shape-item

    Parameters:
        x (float): X position on the board (center of the shape).
        y (float): Y position on the board (center of the shape).
        shape (str): Shape type (e.g., "rectangle", "ellipse", etc.). Default is "rectangle".
        width (float): Width of the shape. Default is 300.
        height (float): Height of the shape. Default is 200.
        fill_color (str): Fill color of the shape (hex). Default is "#FFD966".
        border_color (str): Border color of the shape (hex). Default is "#1a1a1a".
        content (str | None): Optional text (HTML allowed) inside the shape.
        parent_frame_id (str | None): Optional parent frame ID to attach the shape to.

    Returns:
        str: The ID of the created shape object.

    Raises:
        Exception: If the shape could not be created.
    """
    payload = {
        "data": {
            "shape": shape,
            **({"content": f"<p>{content}</p>"} if content else {}),
        },
        "style": {
            "fillColor": fill_color,
            "borderColor": border_color
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
        **({"parent": {"id": parent_frame_id}} if parent_frame_id else {}),
    }

    # Option 1: using requests directly
    url_shapes = f"{BASE_URL}/shapes"
    response = requests.post(url_shapes, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Error creating shape: {response.text}")
    return response.json().get("id")

    # Option 2: Using miro_api
    # api = miro_api.MiroApi(ACCESS_TOKEN)
    # return api.create_shape_item(
    #     board_id=BOARD_ID,
    #     shape_create_request=payload,
    # )


def create_connector(source_id, target_id, caption=None, font_size=14, color="#1a1a1a", shape="elbowed") -> str:
    """
    Create a connection (line/arrow) between two objects on the Miro board.
    docs: https://developers.miro.com/reference/create-connector
    - source_id: ID of the source object (miro item)
    - target_id: ID of the target object (miro item)
    - caption: Optional text label for the connection
    - color: Line color (hex)
    - shape: "elbowed" or "straight"
    Returns the connection object ID.
    """
    payload = {
        "startItem": {"id": source_id},
        "endItem": {"id": target_id},
        "style": {
            "color": color,
            "strokeColor": color,
            "strokeStyle": "normal",
            "fontSize": font_size,
            "endStrokeCap": "none",
        },
        "shape": shape,
        "captions": [{"content": caption if caption else ""}]
    }
    url_connectors = f"{BASE_URL}/connectors"
    response = requests.post(url_connectors, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error creating connector: {response.text}")
    return response.json().get("id")