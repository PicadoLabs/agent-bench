import pytest
from pipeline import DataPipeline


def test_empty_dataset():
    res = DataPipeline.process_records([])
    assert res["record_count"] == 0
    assert res["total_revenue"] == 0.0
    assert res["average_amount"] == 0.0
    assert res["records"] == []


def test_valid_records_cleaning_and_date_parsing():
    raw = [
        {" item ": " Widget A ", "amount": " 25.50 ", "date": "2026-05-15"},
        {"item": "Widget B", "amount": 74.50, "date": "15/05/2026"}
    ]
    res = DataPipeline.process_records(raw)
    assert res["record_count"] == 2
    assert res["total_revenue"] == 100.0
    assert res["average_amount"] == 50.0
    assert res["records"][0]["item"] == "Widget A"
    assert res["records"][0]["date"] == "2026-05-15"
    assert res["records"][1]["date"] == "2026-05-15"


def test_invalid_dates_skipped():
    raw = [
        {"item": "Valid", "amount": "50.0", "date": "2026-01-01"},
        {"item": "Invalid Date", "amount": "100.0", "date": "not-a-date"},
        {"item": "Missing Date", "amount": "20.0"}
    ]
    res = DataPipeline.process_records(raw)
    assert res["record_count"] == 1
    assert res["total_revenue"] == 50.0
    assert res["records"][0]["item"] == "Valid"


def test_negative_amount_raises():
    raw = [{"item": "Bad", "amount": -10.0, "date": "2026-01-01"}]
    with pytest.raises(ValueError):
        DataPipeline.process_records(raw)
