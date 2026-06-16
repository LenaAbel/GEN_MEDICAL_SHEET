from pathlib import Path


WINDOW_TITLE = "Générateur de Fiche Médicale - CHU Besançon"
WINDOW_MIN_SIZE = (760, 560)
INPUT_MAX_HEIGHT = 100
SEND_BUTTON_SIZE = 36
HEADER_ACTION_BUTTON_SIZE = 36
HEADER_ACTION_ICON_SIZE = 24

ASSETS_DIR = Path(__file__).resolve().parents[1] / "ui" / "assets"
SEND_ICON_PATH = ASSETS_DIR / "send_icon.svg"
RECORD_ICON_PATH = ASSETS_DIR / "record_icon.svg"
NEW_CONVERSATION_ICON_PATH = ASSETS_DIR / "new_conversation_icon.svg"
