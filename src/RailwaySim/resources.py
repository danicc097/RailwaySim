from pathlib import Path
import sys


def get_path(relative_path):
    """Use correct absolute paths for bundled and dev versions."""
    rel_path = Path(relative_path)
    dev_base_path = Path(__file__).resolve().parent.parent
    #* dev_base_path is used by default if _MEIPASS doesn't exist
    base_path = getattr(
        sys, "_MEIPASS", dev_base_path
    )  # _MEIPASS works for both onedir and onefile
    return base_path / rel_path