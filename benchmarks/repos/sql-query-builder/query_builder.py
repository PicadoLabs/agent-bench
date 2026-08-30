# query_builder.py - Safe Parameterized SQL Query Builder
from typing import List, Dict, Any, Tuple, Optional


class QueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self.selected_columns: List[str] = ["*"]
        self.where_conditions: List[Tuple[str, str, Any]] = []
        self.order_by_col: Optional[str] = None
        self.order_dir: str = "ASC"
        self.limit_val: Optional[int] = None

    def select(self, *columns: str) -> "QueryBuilder":
        if columns:
            self.selected_columns = list(columns)
        return self

    def where(self, column: str, operator: str, value: Any) -> "QueryBuilder":
        self.where_conditions.append((column, operator, value))
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self.order_by_col = column
        self.order_dir = direction.upper() if direction.upper() in ["ASC", "DESC"] else "ASC"
        return self

    def limit(self, count: int) -> "QueryBuilder":
        if count < 0:
            raise ValueError("Limit must be non-negative")
        self.limit_val = count
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build SQL query string with ? placeholders and return (sql_string, params_list).
        Example:
        ("SELECT id, name FROM users WHERE age >= ? AND status = ? ORDER BY id DESC LIMIT 10", [18, 'active'])
        """
        cols = ", ".join(self.selected_columns)
        sql = f"SELECT {cols} FROM {self.table}"
        params: List[Any] = []

        if self.where_conditions:
            # BUG: Concatenates literal values directly causing SQL injection instead of parameter placeholders '?'
            where_parts = []
            for col, op, val in self.where_conditions:
                where_parts.append(f"{col} {op} {val}")
            sql += " WHERE " + " AND ".join(where_parts)
            # BUG: params list left empty!

        if self.order_by_col:
            sql += f" ORDER BY {self.order_by_col} {self.order_dir}"

        if self.limit_val is not None:
            sql += f" LIMIT {self.limit_val}"

        return sql, params
