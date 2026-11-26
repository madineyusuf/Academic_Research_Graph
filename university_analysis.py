"""Üniversite odaklı analizler, nadir alanlar ve danışman önerisi modülü."""

from itertools import combinations

from academic_algorithms import jaccard_similarity
from university_graph import (
    _clean_fields,
    _get_university,
    build_university_field_graph,
)


def top_fields_per_university(academics, university=None, limit=5):
    """Her üniversite (veya seçilen tek üniversite) için en güçlü alanları döndürür."""
    graph = build_university_field_graph(academics)
    universities = [
        node for node, kind in graph.node_types.items() if kind == "university"
    ]

    if university is not None:
        wanted = university.strip().casefold()
        matched = next(
            (uni for uni in universities if uni.casefold() == wanted), None
        )
        if matched is None:
            raise KeyError(f"Üniversite bulunamadı: {university}")
        universities = [matched]

    result = {}
    for uni in sorted(universities):
        fields = sorted(
            graph.neighbors(uni).items(),
            key=lambda item: (-item[1], item[0]),
        )
        result[uni] = [(field, int(count)) for field, count in fields[:limit]]
    return result


def similar_university_pairs(academics, limit=5):
    """Alan profili birbirine en çok benzeyen üniversite çiftlerini (Jaccard) döndürür."""
    graph = build_university_field_graph(academics)
    uni_fields = {
        node: set(graph.neighbors(node).keys())
        for node, kind in graph.node_types.items()
        if kind == "university"
    }

    pairs = []
    for uni_a, uni_b in combinations(sorted(uni_fields), 2):
        score = jaccard_similarity(uni_fields[uni_a], uni_fields[uni_b])
        if score > 0:
            pairs.append((uni_a, uni_b, score))

    pairs.sort(key=lambda item: (-item[2], item[0], item[1]))
    return pairs if limit is None else pairs[:limit]


def cross_university_collaborations(academics, limit=5):
    """Farklı üniversitelerde çalışan en benzer akademisyen çiftlerini önerir."""
    records = [
        (
            str(academic["name"]).strip(),
            _get_university(academic),
            _clean_fields(academic),
        )
        for academic in academics
    ]

    pairs = []
    for (name_a, uni_a, fields_a), (name_b, uni_b, fields_b) in combinations(
        records, 2
    ):
        if uni_a.casefold() == uni_b.casefold():
            continue
        score = jaccard_similarity(fields_a, fields_b)
        if score > 0:
            pairs.append((name_a, uni_a, name_b, uni_b, score))

    pairs.sort(key=lambda item: (-item[4], item[0], item[2]))
    return pairs if limit is None else pairs[:limit]


def rare_fields(academics, max_universities=2):
    """Yalnızca 1 veya 2 üniversitede çalışılan nadir alanları döndürür."""
    graph = build_university_field_graph(academics)
    result = []
    for node, kind in graph.node_types.items():
        if kind == "field":
            unis = sorted(graph.neighbors(node).keys())
            if 1 <= len(unis) <= max_universities:
                result.append((node, len(unis), unis))

    result.sort(key=lambda item: (item[1], item[0]))
    return result


def recommend_advisors(academics, interests, university=None, limit=5):
    """Kullanıcının ilgi alanlarına göre en uygun danışmanları sıralar."""
    wanted_fields = {
        str(field).strip().casefold()
        for field in interests
        if str(field).strip()
    }
    if not wanted_fields:
        return []

    uni_filter = university.strip().casefold() if university else None
    scores = []
    for academic in academics:
        uni = _get_university(academic)
        if uni_filter and uni.casefold() != uni_filter:
            continue

        acad_fields = {f.casefold() for f in _clean_fields(academic)}
        score = jaccard_similarity(wanted_fields, acad_fields)
        if score > 0:
            scores.append((str(academic["name"]).strip(), uni, score))

    scores.sort(key=lambda item: (-item[2], item[0]))
    return scores if limit is None else scores[:limit]


if __name__ == "__main__":
    import json
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent
    sample_path = base_dir / "data" / "academics_sample.json"
    if not sample_path.exists():
        sample_path = base_dir / "academics_sample.json"

    with open(sample_path, "r", encoding="utf-8") as file:
        sample_data = json.load(file)

    print("1) En güçlü alanlar (University A):", top_fields_per_university(sample_data, "University A"))
    print("2) Benzer üniversiteler:", similar_university_pairs(sample_data, limit=3))
    print("3) İşbirliği önerileri:", cross_university_collaborations(sample_data, limit=3))
    print("4) Nadir alanlar (<=2 üni):", rare_fields(sample_data))
    print("5) Danışman önerisi (ML, Deep Learning):", recommend_advisors(sample_data, ["Machine Learning", "Deep Learning"]))