import pytest
from pagination import Paginator


def test_empty_list_pagination():
    res = Paginator.paginate([], page=1, page_size=10)
    assert res.items == []
    assert res.pagination.total_items == 0
    assert res.pagination.total_pages == 1
    assert res.pagination.has_next is False
    assert res.pagination.has_previous is False


def test_first_page_pagination():
    items = [{"id": i} for i in range(1, 26)]
    res = Paginator.paginate(items, page=1, page_size=10)
    assert len(res.items) == 10
    assert res.items[0]["id"] == 1
    assert res.items[-1]["id"] == 10
    assert res.pagination.total_pages == 3
    assert res.pagination.has_next is True
    assert res.pagination.has_previous is False


def test_middle_page_pagination():
    items = [{"id": i} for i in range(1, 26)]
    res = Paginator.paginate(items, page=2, page_size=10)
    assert len(res.items) == 10
    assert res.items[0]["id"] == 11
    assert res.items[-1]["id"] == 20
    assert res.pagination.has_next is True
    assert res.pagination.has_previous is True


def test_last_page_pagination():
    items = [{"id": i} for i in range(1, 26)]
    res = Paginator.paginate(items, page=3, page_size=10)
    assert len(res.items) == 5
    assert res.items[0]["id"] == 21
    assert res.items[-1]["id"] == 25
    assert res.pagination.has_next is False
    assert res.pagination.has_previous is True


def test_invalid_page_raises():
    items = [{"id": 1}]
    with pytest.raises(ValueError):
        Paginator.paginate(items, page=0, page_size=10)
    with pytest.raises(ValueError):
        Paginator.paginate(items, page=-1, page_size=10)


def test_invalid_page_size_raises():
    items = [{"id": 1}]
    with pytest.raises(ValueError):
        Paginator.paginate(items, page=1, page_size=0)
    with pytest.raises(ValueError):
        Paginator.paginate(items, page=1, page_size=101)
