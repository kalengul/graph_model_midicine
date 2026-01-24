"""Модуль управления цветами."""

import json
from pathlib import Path

from django.conf import settings


color_path = Path(settings.BASE_DIR) / 'data/rank_colors/default_colors.json'

colors = {}

with open(color_path, 'r', encoding='utf-8') as file:
    colors = json.load(file)
