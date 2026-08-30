# pagination.py - In-memory pagination helper for REST APIs
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class PageMetadata(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel):
    items: List[Dict[str, Any]]
    pagination: PageMetadata


class Paginator:
    @staticmethod
    def paginate(items: List[Dict[str, Any]], page: int = 1, page_size: int = 10) -> PaginatedResponse:
        # BUG: Missing validation for negative/zero page or page_size > 100
        # BUG: total_pages becomes 0 when items is empty instead of 1
        # BUG: has_previous calculation is wrong
        total_items = len(items)
        total_pages = total_items // page_size if total_items > 0 else 0
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        sliced_items = items[start_idx:end_idx]

        return PaginatedResponse(
            items=sliced_items,
            pagination=PageMetadata(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=True  # BUG: always true!
            )
        )
