import pytest
from query_builder import QueryBuilder


def test_simple_select():
    qb = QueryBuilder("users")
    sql, params = qb.build()
    assert sql == "SELECT * FROM users"
    assert params == []


def test_select_columns_and_where_parameterized():
    qb = QueryBuilder("users")
    qb.select("id", "username", "email")
    qb.where("age", ">=", 18)
    qb.where("status", "=", "active")
    sql, params = qb.build()

    assert sql == "SELECT id, username, email FROM users WHERE age >= ? AND status = ?"
    assert params == [18, "active"]


def test_order_by_and_limit():
    qb = QueryBuilder("products")
    qb.where("price", "<", 100.0)
    qb.order_by("created_at", "DESC")
    qb.limit(20)
    sql, params = qb.build()

    assert sql == "SELECT * FROM products WHERE price < ? ORDER BY created_at DESC LIMIT 20"
    assert params == [100.0]


def test_sql_injection_prevention():
    qb = QueryBuilder("accounts")
    malicious_input = "' OR '1'='1"
    qb.where("username", "=", malicious_input)
    sql, params = qb.build()

    assert sql == "SELECT * FROM accounts WHERE username = ?"
    assert params == [malicious_input]
