"""
Основной модуль FastAPI приложения для поиска пути в торговом центре.
"""
import os
import json
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import RouteRequest, RouteResponse, Point, CoordinateRouteRequest
from app.pathfinder import Graph, astar_algorithm, add_temporary_nodes

# Создание экземпляра FastAPI
app = FastAPI(
    title="Mall Pathfinder",
    description="API для поиска кратчайшего пути между двумя точками на карте торгового центра",
    version="1.0.0"
)

# Определение путей к директориям
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")
GRAPH_FILE = os.path.join(DATA_DIR, "graph.json")

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Загрузка графа из JSON-файла
try:
    graph = Graph.from_json_file(GRAPH_FILE)
except Exception as e:
    # В случае ошибки при загрузке графа, создаем пустой граф
    # В реальном приложении здесь должна быть более сложная обработка ошибок
    print(f"Ошибка при загрузке графа: {e}")
    graph = Graph()


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Главная страница приложения.
    
    Args:
        request: Объект запроса
        
    Returns:
        HTMLResponse: HTML-страница
    """
    return templates.TemplateResponse("index.html", {"request": request})


"""@app.get("/api/nodes")
async def get_nodes():
    
    Получение списка всех узлов графа.

    Returns:
        Dict: Словарь узлов
    
    return graph.nodes"""

@app.get("/api/nodes")
async def get_visible_nodes():
    
    """Возвращает только узлы с visible: true или без свойства visible"""
    
    visible_nodes = {
        node_id: data
        for node_id, data in graph.nodes.items()
        if "visible" not in data or data["visible"]  # учитываем узлы без visible или с visible=True
    }
    return visible_nodes  


@app.post("/api/route", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    """
    Расчет маршрута между двумя узлами по ID.
    
    Args:
        request: Объект запроса с начальным и конечным узлами
        
    Returns:
        RouteResponse: Объект ответа с маршрутом
        
    Raises:
        HTTPException: Если узлы не найдены или путь не существует
    """
    # Проверка наличия узлов
    if request.start not in graph.nodes:
        raise HTTPException(status_code=404, detail=f"Начальный узел {request.start} не найден")
    
    if request.end not in graph.nodes:
        raise HTTPException(status_code=404, detail=f"Конечный узел {request.end} не найден")
    
    try:
        # Расчет маршрута
        path = astar_algorithm(graph, request.start, request.end)
        
        # Преобразование пути в список координат
        route = [Point(x=graph.nodes[node_id]["x"], y=graph.nodes[node_id]["y"]) for node_id in path]
        
        return RouteResponse(route=route)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете маршрута: {str(e)}")


@app.post("/api/route/coordinates", response_model=RouteResponse)
async def calculate_route_by_coordinates(request: CoordinateRouteRequest):
    """
    Расчет маршрута между двумя произвольными точками по координатам.
    
    Args:
        request: Объект запроса с координатами начальной и конечной точек
        
    Returns:
        RouteResponse: Объект ответа с маршрутом
        
    Raises:
        HTTPException: Если путь не существует
    """
    try:
        # Создаем граф с временными узлами
        temp_graph, start_temp_id, end_temp_id = add_temporary_nodes(
            graph, 
            (request.start.x, request.start.y), 
            (request.end.x, request.end.y)
        )
        
        # Расчет маршрута
        path = astar_algorithm(temp_graph, start_temp_id, end_temp_id)
        
        # Преобразование пути в список координат
        route = [Point(x=temp_graph.nodes[node_id]["x"], y=temp_graph.nodes[node_id]["y"]) for node_id in path]
        
        return RouteResponse(route=route)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете маршрута: {str(e)}")


@app.get("/api/debug/graph")
async def get_graph_debug():
    """
    Отладочная информация о графе.
    
    Returns:
        Dict: Информация о графе
    """
    return {
        "nodes_count": len(graph.nodes),
        "edges_count": len(graph.edges),
        "nodes": graph.nodes,
        "edges": graph.edges
    }


# Для запуска приложения с помощью uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)