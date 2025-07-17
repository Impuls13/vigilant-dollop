"""
Модуль для работы с графом и алгоритмом A* для поиска кратчайшего пути.
"""
import json
import heapq
from typing import Dict, List, Tuple, Set, Optional, Any


class Graph:
    """
    Класс для представления графа с узлами и связями.
    
    Атрибуты:
        nodes (Dict[str, Dict[str, int]]): Словарь узлов, где ключ - ID узла, 
                                          значение - словарь с координатами x, y.
        edges (Dict[str, List[str]]): Словарь связей, где ключ - ID узла,
                                     значение - список ID соседних узлов.
    """
    
    def __init__(self, nodes: Dict[str, Dict[str, int]] = None, edges: Dict[str, List[str]] = None):
        """
        Инициализация графа.
        
        Args:
            nodes: Словарь узлов {node_id: {"x": x, "y": y}}
            edges: Словарь связей {node_id: [connected_node_ids]}
        """
        self.nodes = nodes or {}
        self.edges = edges or {}
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Graph':
        """
        Создание графа из JSON-данных.
        
        Args:
            json_data: Словарь с данными графа
            
        Returns:
            Graph: Экземпляр графа
        """
        return cls(json_data.get("nodes", {}), json_data.get("edges", {}))
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'Graph':
        """
        Загрузка графа из JSON-файла.
        
        Args:
            file_path: Путь к JSON-файлу
            
        Returns:
            Graph: Экземпляр графа
        """
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return cls.from_json(json_data)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """
        Получение списка соседних узлов.
        
        Args:
            node_id: ID узла
            
        Returns:
            List[str]: Список ID соседних узлов
        """
        return self.edges.get(node_id, [])
    
    def has_edge(self, node_id1: str, node_id2: str) -> bool:
        """
        Проверка наличия ребра между узлами.
        
        Args:
            node_id1: ID первого узла
            node_id2: ID второго узла
            
        Returns:
            bool: True, если ребро существует
        """
        return (node_id2 in self.edges.get(node_id1, []) or 
                node_id1 in self.edges.get(node_id2, []))
    
    def heuristic(self, node_id1: str, node_id2: str) -> float:
        """
        Эвристическая функция - расстояние по прямой между узлами.
        
        Args:
            node_id1: ID первого узла
            node_id2: ID второго узла
            
        Returns:
            float: Расстояние между узлами
        """
        if node_id1 not in self.nodes or node_id2 not in self.nodes:
            return float('inf')
        
        node1 = self.nodes[node_id1]
        node2 = self.nodes[node_id2]
        return ((node1["x"] - node2["x"]) ** 2 + (node1["y"] - node2["y"]) ** 2) ** 0.5
    
    def distance(self, node_id1: str, node_id2: str) -> float:
        """
        Расстояние между соседними узлами.
        ВАЖНО: Возвращает бесконечность, если ребра нет!
        
        Args:
            node_id1: ID первого узла
            node_id2: ID второго узла
            
        Returns:
            float: Расстояние между узлами или бесконечность
        """
        # Проверяем, есть ли ребро между узлами
        if not self.has_edge(node_id1, node_id2):
            return float('inf')
        
        return self.heuristic(node_id1, node_id2)


def astar_algorithm(graph: Graph, start_id: str, end_id: str) -> List[str]:
    """
    Реализация алгоритма A* для поиска кратчайшего пути в графе.
    
    Args:
        graph: Граф
        start_id: ID начального узла
        end_id: ID конечного узла
        
    Returns:
        List[str]: Список ID узлов, составляющих кратчайший путь
    """
    # Проверка наличия узлов в графе
    if start_id not in graph.nodes or end_id not in graph.nodes:
        raise ValueError(f"Узлы {start_id} или {end_id} не найдены в графе")
    
    # Если начальный и конечный узлы совпадают
    if start_id == end_id:
        return [start_id]
    
    # Множество посещенных узлов
    closed_set: Set[str] = set()
    
    # Множество узлов в открытом списке для быстрой проверки
    open_set_nodes: Set[str] = {start_id}
    
    # Словарь для хранения предыдущего узла на оптимальном пути
    came_from: Dict[str, Optional[str]] = {}
    
    # Словарь для хранения стоимости пути от начального узла до текущего
    g_score: Dict[str, float] = {start_id: 0}
    
    # Словарь для хранения оценки полной стоимости пути через текущий узел
    f_score: Dict[str, float] = {start_id: graph.heuristic(start_id, end_id)}
    
    # Очередь с приоритетом для выбора узла с наименьшей оценкой f_score
    open_set = [(f_score[start_id], start_id)]
    heapq.heapify(open_set)
    
    while open_set:
        # Извлечение узла с наименьшей оценкой f_score
        current_f, current = heapq.heappop(open_set)
        
        # Проверяем, что узел еще актуален (может быть устаревшая запись)
        if current in closed_set:
            continue
            
        # Удаляем из открытого множества
        open_set_nodes.discard(current)
        
        # Если достигнут конечный узел, восстанавливаем путь
        if current == end_id:
            path = []
            while current:
                path.append(current)
                current = came_from.get(current)
            return path[::-1]  # Возвращаем путь в обратном порядке
        
        # Добавляем текущий узел в множество посещенных
        closed_set.add(current)
        
        # Перебираем соседние узлы (только те, которые связаны ребрами!)
        for neighbor in graph.get_neighbors(current):
            # Пропускаем уже посещенные узлы
            if neighbor in closed_set:
                continue
            
            # Вычисляем стоимость пути до соседнего узла через текущий
            edge_distance = graph.distance(current, neighbor)
            
            # Если ребра нет, пропускаем
            if edge_distance == float('inf'):
                continue
                
            tentative_g_score = g_score[current] + edge_distance
            
            # Если найден более короткий путь к соседу
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                # Обновляем информацию о пути
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + graph.heuristic(neighbor, end_id)
                
                # Добавляем соседний узел в очередь, если его там нет
                if neighbor not in open_set_nodes:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_nodes.add(neighbor)
    
    # Если путь не найден
    raise ValueError(f"Путь между узлами {start_id} и {end_id} не найден")


def find_nearest_node(graph: Graph, x: int, y: int) -> str:
    """
    Поиск ближайшего узла к заданной точке.
    
    Args:
        graph: Граф
        x: Координата X точки
        y: Координата Y точки
        
    Returns:
        str: ID ближайшего узла
    """
    if not graph.nodes:
        raise ValueError("Граф не содержит узлов")
    
    min_distance = float('inf')
    nearest_node = None
    
    for node_id, node_data in graph.nodes.items():
        distance = ((node_data["x"] - x) ** 2 + (node_data["y"] - y) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            nearest_node = node_id
    
    return nearest_node


def add_temporary_nodes(graph: Graph, start_point: Tuple[int, int], end_point: Tuple[int, int]) -> Tuple[Graph, str, str]:
    """
    Добавление временных узлов для произвольных точек с подключением к ближайшим узлам.
    
    Args:
        graph: Исходный граф
        start_point: Координаты начальной точки (x, y)
        end_point: Координаты конечной точки (x, y)
        
    Returns:
        Tuple[Graph, str, str]: Новый граф с временными узлами, ID начального и конечного узлов
    """
    # Создаем копию графа
    new_nodes = graph.nodes.copy()
    new_edges = {}
    for node_id, neighbors in graph.edges.items():
        new_edges[node_id] = neighbors.copy()
    
    # ID для временных узлов
    start_temp_id = "TEMP_START"
    end_temp_id = "TEMP_END"
    
    # Добавляем временные узлы
    new_nodes[start_temp_id] = {"x": start_point[0], "y": start_point[1]}
    new_nodes[end_temp_id] = {"x": end_point[0], "y": end_point[1]}
    
    # Создаем новый граф с временными узлами
    temp_graph = Graph(new_nodes, new_edges)
    
    # Находим ближайшие узлы
    start_nearest = find_nearest_node(graph, start_point[0], start_point[1])
    end_nearest = find_nearest_node(graph, end_point[0], end_point[1])
    
    # Подключаем временные узлы к ближайшим
    temp_graph.edges[start_temp_id] = [start_nearest]
    temp_graph.edges[end_temp_id] = [end_nearest]
    
    # Добавляем обратные связи
    if start_nearest not in temp_graph.edges:
        temp_graph.edges[start_nearest] = []
    temp_graph.edges[start_nearest].append(start_temp_id)
    
    if end_nearest not in temp_graph.edges:
        temp_graph.edges[end_nearest] = []
    temp_graph.edges[end_nearest].append(end_temp_id)
    
    return temp_graph, start_temp_id, end_temp_id