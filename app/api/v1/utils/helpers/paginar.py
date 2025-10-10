from math import ceil
from app.api.v1 import schemas


def make_links(base_url: str, page: int, per_page: int, total: int) -> schemas.Links:
    page = int(page)
    per_page = int(per_page) if int(per_page) > 0 else 1
    total = int(total)

    total_pages = ceil(total / per_page) if total > 0 else 1

    links = schemas.Links(
        self=f"{base_url}&page={page}&per_page={per_page}",
        next=(
            f"{base_url}&page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        prev=(f"{base_url}&page={page - 1}&per_page={per_page}" if page > 1 else None),
    )

    return links
