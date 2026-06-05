from __future__ import annotations

from app import content


def search_products(query: str, limit: int = 8) -> list[str]:
    normalized = query.strip().lower()
    if not normalized:
        return []

    scored: list[tuple[int, str]] = []
    for slug, product in content.PRODUCTS.items():
        haystack = " ".join(
            [
                product["name"],
                product["summary"],
                " ".join(product["benefits"]),
                " ".join(product["keywords"]),
            ]
        ).lower()
        score = 0
        if normalized in product["name"].lower():
            score += 5
        if normalized in haystack:
            score += 3
        for word in normalized.split():
            if word in haystack:
                score += 1
        if score:
            scored.append((score, slug))

    scored.sort(reverse=True)
    return [slug for _, slug in scored[:limit]]

