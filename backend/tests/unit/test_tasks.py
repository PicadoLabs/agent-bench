import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.storage.models import Base
from app.benchmarks.loader import BenchmarkLoader
from app.storage.repository import BenchmarkRepository


def test_load_all_yaml_tasks():
    tasks = BenchmarkLoader.load_all_benchmarks("./benchmarks/tasks")
    assert len(tasks) >= 10
    
    ids = [t.id for t in tasks]
    assert "fix-auth-jwt" in ids
    assert "feat-fastapi-pagination" in ids
    assert "fix-rate-limiter" in ids
    assert "fix-sql-builder" in ids
    assert "fix-lru-ttl-cache" in ids


def test_sync_benchmarks_to_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        synced = BenchmarkLoader.sync_benchmarks_to_db(db, "./benchmarks/tasks")
        assert len(synced) >= 10
        repo = BenchmarkRepository(db)
        all_b = repo.get_all()
        assert len(all_b) >= 10
    finally:
        db.close()
