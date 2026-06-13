from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection, Row


def row_to_dict(row: Row[Any]) -> dict[str, Any]:
    return dict(row._mapping)
