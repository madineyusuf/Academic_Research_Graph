"""NetworkX ve Matplotlib kullanarak graf görselleştirme modülü."""

from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx


NODE_COLORS = {
    "academic": "#4C78A8",
    "field": "#F58518",
    "university": "#54A24B",
    "generic": "#888888",
}


def to_networkx(graph):
    """Projenin Graph nesnesini NetworkX grafına dönüştürür."""
    nx_graph = nx.Graph()
    for node in graph.nodes:
        kind = graph.node_types.get(node, "generic")
        nx_graph.add_node(node, kind=kind)

    for node, neighbors in graph.adjacency.items():
        for neighbor, weight in neighbors.items():
            if not nx_graph.has_edge(node, neighbor):
                nx_graph.add_edge(node, neighbor, weight=weight)
    return nx_graph


def draw_full_graph(
    graph,
    title="Ağ Genel Görünümü",
    save_path=None,
    show=True,
    max_nodes=80,
):
    """Tüm ağı (çok büyükse en yüksek dereceli düğümleri) çizer.

    Düğüm boyutu düğümün derecesine göre ölçeklenir.
    """
    nx_graph = to_networkx(graph)
    if nx_graph.number_of_nodes() == 0:
        raise ValueError("Görselleştirilecek düğüm bulunamadı.")

    if nx_graph.number_of_nodes() > max_nodes:
        top_nodes = sorted(
            nx_graph.degree, key=lambda item: item[1], reverse=True
        )[:max_nodes]
        nx_graph = nx_graph.subgraph([node for node, _ in top_nodes]).copy()
        title = f"{title} (En yüksek dereceli {max_nodes} düğüm)"

    pos = nx.spring_layout(nx_graph, seed=42, k=0.8)
    degrees = dict(nx_graph.degree())
    node_sizes = [300 + degrees[n] * 180 for n in nx_graph.nodes()]
    node_colors = [
        NODE_COLORS.get(nx_graph.nodes[n].get("kind", "generic"), "#888888")
        for n in nx_graph.nodes()
    ]

    plt.figure(figsize=(12, 8))
    nx.draw_networkx_edges(nx_graph, pos, alpha=0.35, edge_color="#888888")
    nx.draw_networkx_nodes(
        nx_graph, pos, node_size=node_sizes, node_color=node_colors, alpha=0.9
    )
    nx.draw_networkx_labels(nx_graph, pos, font_size=8)

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        output = Path(save_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150)

    if show:
        plt.show()
    else:
        plt.close()


def draw_ego_subgraph(
    graph,
    center_node,
    radius=1,
    title=None,
    save_path=None,
    show=True,
):
    """Seçilen bir akademisyen, alan veya üniversitenin yakın çevresini çizer."""
    if center_node not in graph.nodes:
        raise KeyError(f"Graf düğümü bulunamadı: {center_node}")

    nx_graph = to_networkx(graph)
    subgraph = nx.ego_graph(nx_graph, center_node, radius=radius)

    pos = nx.spring_layout(subgraph, seed=42, k=1.0)
    node_sizes = [
        1100 if n == center_node else 450 + subgraph.degree(n) * 120
        for n in subgraph.nodes()
    ]
    node_colors = [
        "#E45756"
        if n == center_node
        else NODE_COLORS.get(subgraph.nodes[n].get("kind", "generic"), "#888888")
        for n in subgraph.nodes()
    ]

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_edges(subgraph, pos, alpha=0.5, edge_color="#666666")
    nx.draw_networkx_nodes(
        subgraph, pos, node_size=node_sizes, node_color=node_colors, alpha=0.95
    )
    nx.draw_networkx_labels(subgraph, pos, font_size=9)

    edge_labels = {
        (u, v): f"{data['weight']:.2f}".rstrip("0").rstrip(".")
        for u, v, data in subgraph.edges(data=True)
        if "weight" in data
    }
    if edge_labels:
        nx.draw_networkx_edge_labels(
            subgraph, pos, edge_labels=edge_labels, font_size=8
        )

    plt.title(title or f"Alt Graf: {center_node} (yarıçap={radius})")
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        output = Path(save_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150)

    if show:
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    from university_graph import build_university_field_graph, load_sample_data

    sample_data = load_sample_data()
    uni_graph = build_university_field_graph(sample_data)
    out_dir = Path(__file__).resolve().parent / "outputs"

    draw_full_graph(
        uni_graph,
        title="Üniversite-Alan Ağı (Genel Görünüm)",
        save_path=out_dir / "university_field_full.png",
        show=True,
    )
    draw_ego_subgraph(
        uni_graph,
        center_node="University A",
        radius=1,
        save_path=out_dir / "university_a_subgraph.png",
        show=True,
    )
    print(f"Grafikler kaydedildi: {out_dir}")