from pathlib import Path


WINDOW_TITLE = "Générateur de Fiche Médicale - CHU Besançon"
WINDOW_MIN_SIZE = (760, 560)
INPUT_MAX_HEIGHT = 100
SEND_BUTTON_SIZE = 36

ASSETS_DIR = Path(__file__).resolve().parent / "ui" / "img"
SEND_ICON_PATH = ASSETS_DIR / "send_icon.svg"
