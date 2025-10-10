from math import ceil
from app.api.v1 import schemas


def make_links(base_url: str, page: int, per_page: int, total: int) -> schemas.Links:
    """
    Gera links de paginação (self, next, prev) para uma coleção de recursos.

    Args:
        base_url: A URL base para os links.
        page: O número da página atual.
        per_page: O número de itens por página.
        total: O número total de itens na coleção.

    Returns:
        Um objeto `schemas.Links` contendo os links de paginação.
    """
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
