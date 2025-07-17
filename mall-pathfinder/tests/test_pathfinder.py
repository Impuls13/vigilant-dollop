"""
Тесты для модуля pathfinder.py
"""
import sys
import os
import pytest
from typing import Dict, List, Any

# Добавляем путь к директории app в sys.path для импорта модуля pathfinder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.pathfinder import Graph, astar_algorithm


# Фикстура для создания тестового графа
@pytest.fixture
def test_graph() -> Graph:
    """
    Создает тестовый граф для использования в тестах.
    
    Returns:
        Graph: Тестовый граф
    """
    nodes = {
        "A": {"x": 0, "y": 0},
        "B": {"x": 1, "y": 0},
        "C": {"x": 2, "y": 0},
        "D": {"x": 0, "y": 1},
        "E": {"x": 1, "y": 1},
        "F": {"x": 2, "y": 1},
        "G": {"x": 0, "y": 2},
        "H": {"x": 1, "y": 2},
        "I": {"x": 2, "y": 2}
    }
    
    edges = {
        "A": ["B", "D"],
        "B": ["A", "C", "E"],
        "C": ["B", "F"],
        "D": ["A", "E", "G"],
        "E": ["B", "D", "F", "H"],
        "F": ["C", "E", "I"],
        "G": ["D", "H"],
        "H": ["E", "G", "I"],
        "I": ["F", "H"]
    }
    
    return Graph(nodes, edges)


# Тесты для класса Graph
def test_graph_initialization():
    """Тест инициализации графа"""
    graph = Graph()
    assert graph.nodes == {}
    assert graph.edges == {}
    
    nodes = {"A": {"x": 0, "y": 0}}
    edges = {"A": ["B"]}
    graph = Graph(nodes, edges)
    assert graph.nodes == nodes
    assert graph.edges == edges


def test_graph_from_json():
    """Тест создания графа из JSON-данных"""
    json_data = {
        "nodes": {"A": {"x": 0, "y": 0}, "B": {"x": 1, "y": 1}},
        "edges": {"A": ["B"], "B": ["A"]}
    }
    graph = Graph.from_json(json_data)
    assert graph.nodes == json_data["nodes"]
    assert graph.edges == json_data["edges"]


def test_get_neighbors(test_graph):
    """Тест получения соседних узлов"""
    assert test_graph.get_neighbors("A") == ["B", "D"]
    assert test_graph.get_neighbors("E") == ["B", "D", "F", "H"]
    assert test_graph.get_neighbors("Z") == []  # Несуществующий узел


def test_heuristic(test_graph):
    """Тест эвристической функции"""
    # Расстояние между A(0,0) и I(2,2) должно быть sqrt(8) = 2.83
    assert abs(test_graph.heuristic("A", "I") - 2.83) < 0.01
    # Расстояние между соседними узлами A(0,0) и B(1,0) должно быть 1
    assert test_graph.heuristic("A", "B") == 1.0


def test_distance(test_graph):
    """Тест функции расстояния между узлами"""
    # Расстояние должно совпадать с эвристикой
    assert test_graph.distance("A", "B") == test_graph.heuristic("A", "B")
    assert test_graph.distance("A", "I") == test_graph.heuristic("A", "I")


# Тесты для алгоритма A*
def test_astar_same_node(test_graph):
    """Тест поиска пути, когда начальный и конечный узлы совпадают"""
    path = astar_algorithm(test_graph, "A", "A")
    assert path == ["A"]


def test_astar_adjacent_nodes(test_graph):
    """Тест поиска пути между соседними узлами"""
    path = astar_algorithm(test_graph, "A", "B")
    assert path == ["A", "B"]


def test_astar_straight_path(test_graph):
    """Тест поиска прямого пути"""
    path = astar_algorithm(test_graph, "A", "C")
    assert path == ["A", "B", "C"]


def test_astar_complex_path(test_graph):
    """Тест поиска сложного пути"""
    path = astar_algorithm(test_graph, "A", "I")
    # Оптимальный путь: A -> B -> E -> F -> I или A -> D -> E -> F -> I
    # Проверяем только длину пути и начальную/конечную точки
    assert len(path) == 5
    assert path[0] == "A"
    assert path[-1] == "I"


def test_astar_nonexistent_node(test_graph):
    """Тест поиска пути с несуществующим узлом"""
    with pytest.raises(ValueError):
        astar_algorithm(test_graph, "A", "Z")


def test_astar_no_path():
    """Тест поиска пути, когда путь не существует"""
    # Создаем граф без связей между компонентами
    nodes = {
        "A": {"x": 0, "y": 0},
        "B": {"x": 1, "y": 1},
        "C": {"x": 2, "y": 2}
    }
    edges = {
        "A": ["B"],
        "B": ["A"],
        "C": []
    }
    graph = Graph(nodes, edges)
    
    with pytest.raises(ValueError):
        astar_algorithm(graph, "A", "C")


# Тест на реальном примере из JSON-файла
def test_astar_with_json_file():
    """Тест поиска пути с использованием данных из JSON-файла"""
    # Создаем тестовый JSON
    test_json = {
        "nodes": {
            "A": {"x": 100, "y": 150},
            "B": {"x": 300, "y": 150},
            "C": {"x": 300, "y": 300}
        },
        "edges": {
            "A": ["B"],
            "B": ["A", "C"],
            "C": ["B"]
        }
    }
    
    graph = Graph.from_json(test_json)
    path = astar_algorithm(graph, "A", "C")
    assert path == ["A", "B", "C"]