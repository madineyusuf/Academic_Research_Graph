"""Akademik Uzmanlık Ağı - Ana Komut Satırı Uygulaması."""

from pathlib import Path

from academic_algorithms import (
    academic_fields,
    academics_at_university,
    academics_in_field,
    build_academic_field_graph,
    build_academic_similarity_graph,
    build_field_graph,
    degree_ranking,
    similarity_components,
    top_similar_academics,
)
from performance import benchmark_similarity, format_benchmark_table
from university_analysis import (
    cross_university_collaborations,
    rare_fields,
    recommend_advisors,
    similar_university_pairs,
    top_fields_per_university,
)
from university_graph import build_university_field_graph, load_sample_data
from visualization import draw_ego_subgraph, draw_full_graph


def _resolve_academic_name(academics, query):
    """Büyük/küçük harf duyarsız olarak tam akademisyen adını bulur."""
    wanted = query.strip().casefold()
    for academic in academics:
        name = str(academic["name"]).strip()
        if name.casefold() == wanted:
            return name
    raise KeyError(f"Akademisyen bulunamadı: '{query}'")


def _resolve_node(graph, query):
    """Büyük/küçük harf duyarsız olarak graf düğümünü bulur."""
    wanted = query.strip().casefold()
    for node in graph.nodes:
        if str(node).casefold() == wanted:
            return node
    raise KeyError(f"Graf düğümü bulunamadı: '{query}'")


def _print_menu():
    print("\n" + "=" * 60)
    print("   AKADEMİK UZMANLIK AĞI - ANA MENÜ")
    print("=" * 60)
    print(" 1. Temel sorgular (Alana / Akademisyene / Üniversiteye göre)")
    print(" 2. İki akademisyen arasındaki en kısa bağlantı yolu (BFS)")
    print(" 3. Merkezi düğümler (En yüksek dereceli akademisyen ve alanlar)")
    print(" 4. Bağlantılı bileşen analizi (Akademisyen benzerlik grafı)")
    print(" 5. Seçilen akademisyene en benzer 5 akademisyen (Jaccard)")
    print(" 6. Üniversitelerin en güçlü 5 alanı")
    print(" 7. Birbirine en çok benzeyen üniversite çiftleri")
    print(" 8. Üniversiteler arası işbirliği önerileri")
    print(" 9. Nadir alanlar (Yalnızca 1 veya 2 üniversitede çalışılan)")
    print("10. Danışman önerisi (İlgi alanlarına göre)")
    print("11. Performans karşılaştırması (Brute Force vs Inverted Index)")
    print("12. Graf görselleştirme (Genel ağ / Alt graf)")
    print(" 0. Çıkış")
    print("=" * 60)


def handle_basic_queries(academics):
    print("\n--- Temel Sorgular ---")
    print("a) Bir alanda çalışan akademisyenler")
    print("b) Bir akademisyenin çalışma alanları")
    print("c) Bir üniversitedeki akademisyenler")
    sub = input("Seçiminiz (a/b/c): ").strip().lower()

    if sub == "a":
        field = input("Çalışma alanı adı: ").strip()
        if not field:
            print("Uyarı: Alan adı boş olamaz.")
            return
        results = academics_in_field(academics, field)
        if not results:
            print(f"'{field}' alanında akademisyen bulunamadı.")
            return
        print(f"\n'{field}' alanında çalışanlar ({len(results)} kişi):")
        for item in results:
            print(f" - {item['name']} ({item.get('university', '-')})")

    elif sub == "b":
        raw_name = input("Akademisyen adı: ").strip()
        name = _resolve_academic_name(academics, raw_name)
        fields = academic_fields(academics, name)
        print(f"\n{name} çalışma alanları: {', '.join(fields)}")

    elif sub == "c":
        uni = input("Üniversite adı: ").strip()
        if not uni:
            print("Uyarı: Üniversite adı boş olamaz.")
            return
        results = academics_at_university(academics, uni)
        if not results:
            print(f"'{uni}' için akademisyen bulunamadı.")
            return
        print(f"\n{uni} akademisyenleri ({len(results)} kişi):")
        for item in results:
            print(f" - {item['name']} ({item.get('title', '-')})")
    else:
        print("Geçersiz alt menü seçimi.")


def handle_shortest_path(academics, af_graph):
    first = _resolve_academic_name(academics, input("1. Akademisyen adı: "))
    second = _resolve_academic_name(academics, input("2. Akademisyen adı: "))
    path = af_graph.bfs_shortest_path(first, second)
    if path is None:
        print("Bu iki akademisyen arasında bağlantı yolu bulunamadı.")
    else:
        print("\nEn kısa yol:")
        print(" -> ".join(path))


def handle_central_nodes(af_graph):
    academics_only = [
        (node, deg)
        for node, deg in degree_ranking(af_graph)
        if af_graph.node_types.get(node) == "academic"
    ][:5]
    fields_only = [
        (node, deg)
        for node, deg in degree_ranking(af_graph)
        if af_graph.node_types.get(node) == "field"
    ][:5]

    print("\nEn çok alanda çalışan akademisyenler (Top 5):")
    for node, deg in academics_only:
        print(f" - {node}: {deg} alan")

    print("\nEn çok akademisyenin çalıştığı alanlar (Top 5):")
    for node, deg in fields_only:
        print(f" - {node}: {deg} akademisyen")


def handle_components(academics):
    components = similarity_components(academics)
    sizes = sorted((len(comp) for comp in components), reverse=True)
    print(f"\nToplam bağlantılı bileşen sayısı: {len(components)}")
    print(f"En büyük bileşen boyutu: {sizes[0] if sizes else 0} akademisyen")
    print(f"Bileşen boyutları: {sizes}")


def handle_similar_academics(academics):
    name = _resolve_academic_name(academics, input("Akademisyen adı: "))
    results = top_similar_academics(academics, name, limit=5)
    print(f"\n{name} için en benzer 5 akademisyen:")
    for other, score in results:
        print(f" - {other}: {score:.2f}")


def handle_top_uni_fields(academics):
    uni_input = input("Üniversite adı (tümü için boş bırakın): ").strip()
    data = top_fields_per_university(
        academics, university=uni_input or None, limit=5
    )
    for uni, fields in data.items():
        formatted = ", ".join(f"{f} ({c})" for f, c in fields)
        print(f" - {uni}: {formatted}")


def handle_similar_universities(academics):
    pairs = similar_university_pairs(academics, limit=5)
    if not pairs:
        print("Ortak alana sahip üniversite çifti bulunamadı.")
        return
    print("\nEn benzer üniversite çiftleri:")
    for uni_a, uni_b, score in pairs:
        print(f" - {uni_a} <-> {uni_b}: {score:.2f}")


def handle_collaborations(academics):
    pairs = cross_university_collaborations(academics, limit=5)
    if not pairs:
        print("Üniversiteler arası işbirliği önerisi bulunamadı.")
        return
    print("\nÜniversiteler arası işbirliği önerileri:")
    for name_a, uni_a, name_b, uni_b, score in pairs:
        print(f" - {name_a} ({uni_a}) <-> {name_b} ({uni_b}) | Skor: {score:.2f}")


def handle_rare_fields(academics):
    items = rare_fields(academics, max_universities=2)
    if not items:
        print("Nadir alan bulunamadı.")
        return
    print(f"\nNadir alanlar (en fazla 2 üniversitede) [{len(items)} alan]:")
    for field, count, unis in items:
        print(f" - {field} ({count} üni): {', '.join(unis)}")


def handle_advisor_recommendation(academics):
    raw_interests = input("İlgi alanlarınız (virgülle ayırın): ").strip()
    interests = [item.strip() for item in raw_interests.split(",") if item.strip()]
    if not interests:
        print("Uyarı: En az bir ilgi alanı girmelisiniz.")
        return
    uni_filter = input("Üniversite filtresi (isteğe bağlı, boş geçilebilir): ").strip()
    results = recommend_advisors(
        academics, interests, university=uni_filter or None, limit=5
    )
    if not results:
        print("Girilen kriterlere uygun danışman bulunamadı.")
        return
    print("\nÖnerilen danışmanlar:")
    for name, uni, score in results:
        print(f" - {name} ({uni}) | Benzerlik: {score:.2f}")


def handle_visualization(graphs):
    print("\nHangi grafı görselleştirmek istersiniz?")
    print("1. Akademisyen-Alan Grafı")
    print("2. Akademisyen Benzerlik Grafı")
    print("3. Alan Grafı")
    print("4. Üniversite-Alan Grafı")
    choice = input("Graf seçimi (1-4): ").strip()
    selected = graphs.get(choice)
    if selected is None:
        print("Geçersiz graf seçimi.")
        return

    title, graph = selected
    mode = input("Görünüm: (1) Genel Ağ, (2) Seçilen Düğümün Alt Grafı: ").strip()
    out_dir = Path(__file__).resolve().parent / "outputs"

    if mode == "1":
        draw_full_graph(
            graph,
            title=f"{title} (Genel Görünüm)",
            save_path=out_dir / f"graph_{choice}_full.png",
            show=True,
        )
    elif mode == "2":
        node_input = input("Merkez düğüm adı (akademisyen/alan/üniversite): ").strip()
        center = _resolve_node(graph, node_input)
        draw_ego_subgraph(
            graph,
            center_node=center,
            radius=1,
            save_path=out_dir / f"graph_{choice}_ego.png",
            show=True,
        )
    else:
        print("Geçersiz görünüm seçimi.")


def main():
    try:
        academics = load_sample_data()
    except Exception as exc:
        print(f"Veri yüklenirken hata oluştu: {exc}")
        return

    print(f"Veri başarıyla yüklendi. Toplam akademisyen sayısı: {len(academics)}")

    af_graph = build_academic_field_graph(academics)
    sim_graph = build_academic_similarity_graph(academics)
    field_graph = build_field_graph(academics)
    uni_graph = build_university_field_graph(academics)

    graphs = {
        "1": ("Akademisyen-Alan Grafı", af_graph),
        "2": ("Akademisyen Benzerlik Grafı", sim_graph),
        "3": ("Alan Grafı", field_graph),
        "4": ("Üniversite-Alan Grafı", uni_graph),
    }

    while True:
        _print_menu()
        choice = input("Seçiminiz (0-12): ").strip()

        try:
            if choice == "0":
                print("Programdan çıkılıyor. İyi çalışmalar!")
                break
            elif choice == "1":
                handle_basic_queries(academics)
            elif choice == "2":
                handle_shortest_path(academics, af_graph)
            elif choice == "3":
                handle_central_nodes(af_graph)
            elif choice == "4":
                handle_components(academics)
            elif choice == "5":
                handle_similar_academics(academics)
            elif choice == "6":
                handle_top_uni_fields(academics)
            elif choice == "7":
                handle_similar_universities(academics)
            elif choice == "8":
                handle_collaborations(academics)
            elif choice == "9":
                handle_rare_fields(academics)
            elif choice == "10":
                handle_advisor_recommendation(academics)
            elif choice == "11":
                stats = benchmark_similarity(academics, repeats=10)
                print("\n" + format_benchmark_table(stats))
            elif choice == "12":
                handle_visualization(graphs)
            else:
                print("Hatalı seçim! Lütfen 0 ile 12 arasında bir sayı girin.")
        except (KeyError, ValueError) as exc:
            print(f"Uyarı: {exc}")
        except Exception as exc:
            print(f"Beklenmeyen bir hata oluştu: {exc}")


if __name__ == "__main__":
    main()