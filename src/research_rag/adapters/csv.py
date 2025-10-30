"""Adapters for reading metadata from CSV companion files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Optional

from research_rag.models.papers import PaperSummary


class CSVLoader:
    """Loads structured metadata records from CSV files."""

    def load(self, path: str | Path) -> List[PaperSummary]:
        """Load paper summary records from ``path``.

        Parameters
        ----------
        path:
            Path to the CSV file containing paper metadata and summaries.

        Returns
        -------
        list[PaperSummary]
            Parsed CSV entries converted into :class:`PaperSummary` objects.

        Raises
        ------
        FileNotFoundError
            If the supplied ``path`` does not exist.
        ValueError
            When required fields are missing from a CSV row.
        """

        csv_path = Path(path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        records: List[PaperSummary] = []
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader: Iterable[dict[str, Optional[str]]] = csv.DictReader(handle)
            if reader.fieldnames is None or "title" not in {
                name.strip().lower() for name in reader.fieldnames if name
            }:
                raise ValueError("CSV file must include a 'title' column in the header")

            for row in reader:
                if not any(row.values()):
                    continue
                records.append(PaperSummary.from_row(row))

        return records
