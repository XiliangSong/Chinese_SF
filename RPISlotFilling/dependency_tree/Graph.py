__author__ = 'boliangzhang'

from collections import defaultdict


class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance


# first dict returned is the shortest distance from initial to all nodes.
def dijsktra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, edge)]
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path

if __name__ == "__main__":
    g = Graph()
    g.add_node('A')
    g.add_node('B')
    g.add_node('C')
    g.add_node('D')
    g.add_node('E')
    g.add_edge('A', 'B', 3)
    g.add_edge('A', 'C', 5)
    g.add_edge('A', 'D', 1)
    g.add_edge('B', 'C', 8)
    g.add_edge('B', 'D', 1)
    g.add_edge('C', 'D', 2)
    g.add_edge('A', 'E', 10)
    g.add_edge('B', 'E', 3)
    g.add_edge('D', 'E', 1)
    g.add_edge('C', 'E', 2)

    print(dijsktra(g, 'A'))


