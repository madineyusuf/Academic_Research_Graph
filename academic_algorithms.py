"""Akademisyen ve çalışma alanı grafı algoritmaları."""

from itertools import combinations

from graph import Graph


def _fields(academic):
    return {
        str(field).strip()
        for field in academic.get("fields", [])
        if str(field).strip()
    }


def build_academic_field_graph(academics):
    """Akademisyen-alan iki parçalı grafını oluşturur."""
    graph = Graph()
    for academic in academics:
        name = str(academic["name"]).strip()
        graph.add_node(name, "academic")
        for field in _fields(academic):
            graph.add_node(field, "field")
            graph.add_edge(name, field)
    return graph


def jaccard_similarity(first_fields, second_fields):
    """İki alan kümesinin Jaccard benzerliğini döndürür."""
    first_fields = set(first_fields)
    second_fields = set(second_fields)
    union = first_fields | second_fields
    return len(first_fields & second_fields) / len(union) if union else 0.0


def build_academic_similarity_graph(
    academics, minimum_similarity=0.0, weight_mode="jaccard"
):
    """Ortak alanı olan akademisyenleri seçilen ağırlıkla bağlar.

    ``weight_mode`` değeri ``"jaccard"`` veya ``"common"`` olabilir.
    """
    if weight_mode not in {"jaccard", "common"}:
        raise ValueError("weight_mode 'jaccard' veya 'common' olmalıdır.")
    records = [
        (str(academic["name"]).strip(), _fields(academic))
        for academic in academics
    ]
    graph = Graph()
    for name, _ in records:
        graph.add_node(name, "academic")
    for (first, first_fields), (second, second_fields) in combinations(records, 2):
        common_count = len(first_fields & second_fields)
        similarity = jaccard_similarity(first_fields, second_fields)
        weight = similarity if weight_mode == "jaccard" else common_count
        if common_count and weight >= minimum_similarity:
            graph.add_edge(first, second, weight)
    return graph


def build_field_graph(academics):
    """Aynı akademisyende birlikte geçen alanların ağırlıklı grafını kurar."""
    graph = Graph()
    for academic in academics:
        fields = sorted(_fields(academic))
        for field in fields:
            graph.add_node(field, "field")
        for first, second in combinations(fields, 2):
            graph.increment_edge(first, second)
    return graph


def academics_in_field(academics, field):
    """Verilen alanda çalışan akademisyenleri döndürür."""
    wanted = field.strip().casefold()
    return [
        academic
        for academic in academics
        if any(item.casefold() == wanted for item in _fields(academic))
    ]


def academic_fields(academics, name):
    """Bir akademisyenin çalışma alanlarını döndürür."""
    for academic in academics:
        if academic["name"] == name:
            return sorted(_fields(academic))
    raise KeyError(f"Akademisyen bulunamadı: {name}")


def academics_at_university(academics, university):
    """Bir üniversitedeki akademisyenleri döndürür."""
    wanted = university.strip().casefold()
    return [
        academic
        for academic in academics
        if str(academic.get("university", "")).strip().casefold() == wanted
    ]


def degree_ranking(graph, limit=None):
    """Düğümleri dereceye göre büyükten küçüğe sıralar."""
    result = sorted(
        ((node, graph.degree(node)) for node in graph.nodes),
        key=lambda item: (-item[1], str(item[0])),
    )
    return result if limit is None else result[:limit]


def similarity_components(academics):
    """Akademisyen benzerlik grafının bileşenlerini döndürür."""
    graph = build_academic_similarity_graph(academics)
    return graph.connected_components()


def top_similar_academics(academics, name, limit=5):
    """Bir akademisyene göre en benzer akademisyenleri döndürür."""
    records = list(academics)
    selected = next(
        (academic for academic in records if academic["name"] == name),
        None,
    )
    if selected is None:
        raise KeyError(f"Akademisyen bulunamadı: {name}")

    selected_fields = _fields(selected)
    scores = [
        (
            academic["name"],
            jaccard_similarity(selected_fields, _fields(academic)),
        )
        for academic in records
        if academic["name"] != name
    ]
    return sorted(scores, key=lambda item: (-item[1], item[0]))[:limit]
