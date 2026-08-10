"""
combination_checker/services/storage.py
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from dataclasses import dataclass

class ResultWriter(ABC):
    @abstractmethod
    def open(self) -> None: ...
    @abstractmethod
    def write(self, *, drug_ids: list[int], drug_names: list[str], max_rank: float) -> None: ...
    @abstractmethod
    def close(self) -> None: ...


class CSVResultWriter(ResultWriter):
    """
    Запись результатов в CSV.
    """
    HEADER = ["drug_ids", "drug_names", "max_rank"]

    def __init__(self, filename: str | Path, delimiter: str = ";", encoding: str = "utf-8-sig"):
        self.filename = Path(filename)
        self.delimiter = delimiter
        self.encoding = encoding
        self.file = None
        self.writer = None

    # =======================================================
    # PUBLIC
    # =======================================================

    def open(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.filename, "w", newline="", encoding=self.encoding)
        self.writer = csv.writer(self.file, delimiter=self.delimiter)
        self.writer.writerow(self.HEADER)

    def close(self):
        if self.file is not None:
            self.file.flush()
            self.file.close()
            self.file = None
            self.writer = None

    def write(self, *, drug_ids: list[int], drug_names: list[str], max_rank: float):
        if self.writer is None:
            raise RuntimeError("Writer is not opened.")
        self.writer.writerow([
            ",".join(map(str, drug_ids)),
            " | ".join(drug_names),
            round(max_rank, 3),
        ])
