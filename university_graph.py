"""Üniversite-Alan grafı oluşturma modülü."""

from pathlib import Path
import json

from graph import Graph


def clean_fields(academic):
    """Akademisyenin çalışma alanlarını temizleyip tekrarsız küme döndürür."""
    return {
        str(field).strip()
        for field in academic.get("fields", [])
        if str(field).strip()
    }


def get_university(academic):
    """Üniversite adını alır ('university' veya 'institution' anahtarını destekler)."""
    uni = academic.get("university") or academic.get("institution") or ""
    return str(uni).strip()


def build_university_field_graph(academics):
    """Üniversite-Alan ağırlıklı yönsüz grafını oluşturur.

    Düğümler: üniversiteler ('university') ve çalışma alanları ('field').
    Kenar ağırlığı: ilgili üniversitede o alanda çalışan akademisyen sayısı.
    """
    graph = Graph()
    for academic in academics:
        university = get_university(academic)
        if not university:
            continue

        graph.add_node(university, "university")
        for field in clean_fields(academic):
            graph.add_node(field, "field")
            graph.increment_edge(university, field)

    return graph


def load_sample_data():
    """Test verisini proje klasörüne göre otomatik bulup yükler."""
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "data" / "academics.json",
        base_dir / "data" / "academics_sample.json",
        base_dir / "academics_sample.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    raise FileNotFoundError("data/academics_sample.json dosyası bulunamadı.")


if __name__ == "__main__":
    academics_data = load_sample_data()
    uni_graph = build_university_field_graph(academics_data)
    print(f"Toplam düğüm sayısı: {len(uni_graph.nodes)}")
    for node, kind in sorted(uni_graph.node_types.items()):
        if kind == "university":
            print(f"{node} -> {uni_graph.neighbors(node)}")