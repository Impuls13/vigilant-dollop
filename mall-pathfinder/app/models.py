"""
Модели данных для API.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class Point(BaseModel):
    """
    Модель для представления точки на карте.
    
    Атрибуты:
        x (int): Координата X
        y (int): Координата Y
    """
    x: int
    y: int


class RouteRequest(BaseModel):
    """
    Модель для запроса маршрута по ID узлов.
    
    Атрибуты:
        start (str): ID начального узла
        end (str): ID конечного узла
    """
    start: str
    end: str


class CoordinateRouteRequest(BaseModel):
    """
    Модель для запроса маршрута по координатам.
    
    Атрибуты:
        start (Point): Начальная точка
        end (Point): Конечная точка
    """
    start: Point
    end: Point


class RouteResponse(BaseModel):
    """
    Модель для ответа с маршрутом.
    
    Атрибуты:
        route (List[Point]): Список точек маршрута
    """
    route: List[Point]


class GraphData(BaseModel):
    """
    Модель для представления данных графа.
    
    Атрибуты:
        nodes (Dict[str, Dict[str, int]]): Словарь узлов
        edges (Dict[str, List[str]]): Словарь связей
    """
    nodes: Dict[str, Dict[str, int]]
    edges: Dict[str, List[str]]