# -*- coding: utf-8 -*-
"""Read-only access to JSON data shipped with the repository."""

import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_data(filename):
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Required data file not found: {path}")
    with path.open("r", encoding="utf-8") as data_file:
        return json.load(data_file)
