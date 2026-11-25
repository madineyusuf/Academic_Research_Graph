"""Temel yönsüz ve ağırlıklı graf veri yapısı."""

from collections import deque


class Graph:
    """Komşuluk sözlüğü kullanan basit bir yönsüz graf."""

    def __init__(self):
        self.nodes = set()
        self.node_types = {}
        self.adjacency = {}

    def add_node(self, value, kind="generic"):
        self.nodes.add(value)
        self.node_types.setdefault(value, kind)
        self.adjacency.setdefault(value, {})

    def add_edge(self, first, second, weight=1.0):
        if first == second:
            raise ValueError("Bir düğüm kendisine kenar oluşturamaz.")
        if weight < 0:
            raise ValueError("Kenar ağırlığı negatif olamaz.")
        self.add_node(first)
        self.add_node(second)
        self.adjacency[first][second] = float(weight)
        self.adjacency[second][first] = float(weight)

    def increment_edge(self, first, second, amount=1.0):
        if amount < 0:
            raise ValueError("Kenar artışı negatif olamaz.")
        current = self.adjacency.get(first, {}).get(second, 0.0)
        self.add_edge(first, second, current + amount)

    def neighbors(self, value):
        if value not in self.adjacency:
            raise KeyError(f"Graf düğümü bulunamadı: {value}")
        return dict(self.adjacency[value])

    def degree(self, value):
        return len(self.neighbors(value))

    def bfs_shortest_path(self, start, target):
        if start not in self.nodes or target not in self.nodes:
            return None
        queue = deque([start])
        previous = {start: None}
        while queue:
            current = queue.popleft()
            if current == target:
                break
            for neighbor in self.adjacency[current]:
                if neighbor not in previous:
                    previous[neighbor] = current
                    queue.append(neighbor)
        if target not in previous:
            return None
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous[current]
        return path[::-1]

    def connected_components(self):
        components = []
        unseen = set(self.nodes)
        while unseen:
            root = unseen.pop()
            component = {root}
            queue = deque([root])
            while queue:
                current = queue.popleft()
                for neighbor in self.adjacency[current]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
        return components
