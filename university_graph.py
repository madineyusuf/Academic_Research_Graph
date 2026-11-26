"""Üniversite-Alan grafı oluşturma modülü."""

from graph import Graph


def _clean_fields(academic):
    """Akademisyenin çalışma alanlarını temizleyip tekrarsız küme döndürür."""
    return {
        str(field).strip()
        for field in academic.get("fields", [])
        if str(field).strip()
    }


def _get_university(academic):
    """Üniversite adını alır ('university' veya 'institution' anahtarını destekler)."""
    uni = academic.get("university") or academic.get("institution") or ""
    return str(uni).strip()


def build_university_field_graph(academics):
    """Üniversite-Alan ağırlıklı grafını oluşturur.

    Düğümler: üniversiteler ('university') ve çalışma alanları ('field').
    Kenar ağırlığı: ilgili üniversitede o alanda çalışan akademisyen sayısı.
    """
    graph = Graph()
    for academic in academics:
        university = _get_university(academic)
        if not university:
            continue

        graph.add_node(university, "university")
        for field in _clean_fields(academic):
            graph.add_node(field, "field")
            graph.increment_edge(university, field)

    return graph


if __name__ == "__main__":
    import json
    from pathlib import Path

    # Test için önce data/academics_sample.json, yoksa mevcut klasöre bakar
    sample_path = Path("/Users/madineyusuf/Desktop/python_proje/data/academics_sample.json")
    if not sample_path.exists():
        sample_path = Path("academics_sample.json")

    with open(sample_path, "r", encoding="utf-8") as file:
        sample_data = json.load(file)

    uni_graph = build_university_field_graph(sample_data)
    print(f"Toplam düğüm sayısı: {len(uni_graph.nodes)}")
    for node, kind in uni_graph.node_types.items():
        if kind == "university":
            print(f"{node} -> {uni_graph.neighbors(node)}")