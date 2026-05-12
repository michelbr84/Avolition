"""Tests for the Dijkstra pathfinding algorithm."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai.pathfinding import Graph


def test_shortest_path_simple():
    graph = Graph({
        'A': {'B': 1, 'C': 4},
        'B': {'A': 1, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    })
    path = graph.shortest_path('A', 'D')
    assert path is not None
    assert 'D' in path


def test_shortest_path_direct():
    graph = Graph({
        'A': {'B': 1},
        'B': {'A': 1}
    })
    path = graph.shortest_path('A', 'B')
    assert path == ['B']


def test_path_length():
    graph = Graph({
        'A': {'B': 3, 'C': 1},
        'B': {'A': 3, 'C': 1},
        'C': {'A': 1, 'B': 1}
    })
    length = graph.path_length('A', 'B')
    assert length == 2  # A->C->B = 1+1 = 2


if __name__ == '__main__':
    test_shortest_path_simple()
    test_shortest_path_direct()
    test_path_length()
    print("All pathfinding tests passed!")
