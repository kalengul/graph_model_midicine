"""Модуль для констант."""

from types import MappingProxyType


IDX_2_RANK_NAME = MappingProxyType({
    0: 'rang_base',
    1: 'rang_m1',
    2: 'rang_f1',
    5: 'rang_freq',
    3: 'rang_m2',
    4: 'rang_f2'
})
RANK_NAMES = ['rang_base', 'rang_m1', 'rang_f1',
              'rang_freq', 'rang_m2', 'rang_f2']
