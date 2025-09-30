"""Модуль загрузки ПД, связанных с полом пациента."""

import json
from pathlib import Path

from django.conf import settings


GENDER_SIDE_EFFECT_PATH = (
    Path(settings.TXT_DB_PATH) / 'dictonary_male_female_side_e.json')

with open(GENDER_SIDE_EFFECT_PATH, 'r', encoding='utf-8') as f:
    GENDER_SIDE_EFFECT = json.load(f)
