def paginate(limit: int, offset: int, total: int) -> dict[str, int | None]:
    last_page = total // limit + 1 if total % limit else total // limit
    next_page = offset + 1 if offset < last_page else None
    prev_page = offset - 1 if (offset - 1) > 0 else None

    pagination_info = {
        "total": total,
        "page": offset,
        "size": limit,
        "first": 1,
        "last": last_page,
        "previous": prev_page,
        "next": next_page,
    }

    return pagination_info
