/**
 * Навигатор по торговому центру - клиентская логика
 */

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const startSelect = document.getElementById('start-point');
    const endSelect = document.getElementById('end-point');
    const findButton = document.getElementById('find-route');
    const clearButton = document.getElementById('clear-route');
    const mallMap = document.getElementById('mall-map');
    const pathCanvas = document.getElementById('path-canvas');
    const routeDetails = document.getElementById('route-details');
    
    // Контекст для рисования на canvas
    const ctx = pathCanvas.getContext('2d');
    
    // Данные о узлах
    let nodes = {};
    
    // Текущий маршрут
    let currentRoute = [];
    
    /**
     * Инициализация приложения
     */
    function init() {
        // Загрузка списка узлов
        loadNodes();
        
        // Обработчики событий
        findButton.addEventListener('click', findRoute);
        clearButton.addEventListener('click', clearRoute);
        mallMap.addEventListener('load', setupCanvas);
        
        // Настройка canvas при загрузке страницы
        setupCanvas();
    }
    
    /**
     * Настройка canvas для отрисовки пути
     */
    function setupCanvas() {
        // Установка размеров canvas в соответствии с размерами изображения
        pathCanvas.width = mallMap.clientWidth;
        pathCanvas.height = mallMap.clientHeight;
        
        // Очистка canvas
        ctx.clearRect(0, 0, pathCanvas.width, pathCanvas.height);
    }
    
    /**
     * Загрузка списка узлов с сервера
     */
    async function loadNodes() {
        try {
            const response = await fetch('/api/nodes');
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            nodes = await response.json();
            
            // Заполнение выпадающих списков
            populateSelectOptions(startSelect, nodes);
            populateSelectOptions(endSelect, nodes);
            
            // Вывод сообщения об успешной загрузке
            console.log('Узлы успешно загружены:', Object.keys(nodes).length);
        } catch (error) {
            console.error('Ошибка при загрузке узлов:', error);
            showError('Не удалось загрузить данные узлов. Пожалуйста, обновите страницу.');
        }
    }
    
    /**
     * Заполнение выпадающего списка опциями
     */
    function populateSelectOptions(selectElement, nodes) {
        // Сохраняем первую опцию (placeholder)
        const placeholder = selectElement.options[0];
        
        // Очищаем список
        selectElement.innerHTML = '';
        
        // Возвращаем placeholder
        selectElement.appendChild(placeholder);
        
        // Добавляем опции для каждого узла
        for (const nodeId in nodes) {
            const option = document.createElement('option');
            option.value = nodeId;
            option.textContent = nodeId;
            selectElement.appendChild(option);
        }
    }
    
    /**
     * Поиск маршрута между выбранными точками
     */
    async function findRoute() {
        const startId = startSelect.value;
        const endId = endSelect.value;
        
        // Проверка выбора начальной и конечной точек
        if (!startId || !endId) {
            showError('Пожалуйста, выберите начальную и конечную точки.');
            return;
        }
        
        try {
            // Отправка запроса на сервер
            const response = await fetch('/api/route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    start: startId,
                    end: endId
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Ошибка HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Сохранение текущего маршрута
            currentRoute = data.route;
            
            // Отрисовка маршрута
            drawRoute(currentRoute);
            
            // Отображение информации о маршруте
            displayRouteInfo(startId, endId, currentRoute);
        } catch (error) {
            console.error('Ошибка при поиске маршрута:', error);
            showError(`Не удалось найти маршрут: ${error.message}`);
        }
    }
    
    /**
     * Отрисовка маршрута на canvas
     */
    function drawRoute(route) {
        // Очистка canvas
        ctx.clearRect(0, 0, pathCanvas.width, pathCanvas.height);
        
        if (!route || route.length === 0) {
            return;
        }
        
        // Масштабирование координат к размеру изображения
        const scaleX = pathCanvas.width / mallMap.naturalWidth;
        const scaleY = pathCanvas.height / mallMap.naturalHeight;
        
        // Отрисовка линий маршрута
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        // Перемещение к первой точке
        ctx.moveTo(route[0].x * scaleX, route[0].y * scaleY);
        
        // Рисование линий к остальным точкам
        for (let i = 1; i < route.length; i++) {
            ctx.lineTo(route[i].x * scaleX, route[i].y * scaleY);
        }
        
        ctx.stroke();
        
        // Отрисовка точек маршрута
        for (let i = 0; i < route.length; i++) {
            const x = route[i].x * scaleX;
            const y = route[i].y * scaleY;
            
            // Разный цвет для начальной, промежуточных и конечной точек
            if (i === 0) {
                // Начальная точка (зеленая)
                ctx.fillStyle = 'green';
                ctx.beginPath();
                ctx.arc(x, y, 8, 0, 2 * Math.PI);
                ctx.fill();
            } else if (i === route.length - 1) {
                // Конечная точка (синяя)
                ctx.fillStyle = 'blue';
                ctx.beginPath();
                ctx.arc(x, y, 8, 0, 2 * Math.PI);
                ctx.fill();
            } else {
                // Промежуточные точки (красные)
                ctx.fillStyle = 'red';
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, 2 * Math.PI);
                ctx.fill();
            }
        }
    }
    
    /**
     * Отображение информации о маршруте
     */
    function displayRouteInfo(startId, endId, route) {
        if (!route || route.length === 0) {
            routeDetails.innerHTML = '<p>Маршрут не найден.</p>';
            return;
        }
        
        // Расчет длины маршрута
        let totalDistance = 0;
        for (let i = 1; i < route.length; i++) {
            const dx = route[i].x - route[i-1].x;
            const dy = route[i].y - route[i-1].y;
            totalDistance += Math.sqrt(dx*dx + dy*dy);
        }
        
        // Округление до целого числа
        totalDistance = Math.round(totalDistance);
        
        // Формирование HTML с информацией о маршруте
        let html = `
            <p><strong>Начальная точка:</strong> ${startId}</p>
            <p><strong>Конечная точка:</strong> ${endId}</p>
            <p><strong>Длина маршрута:</strong> ${totalDistance} пикселей</p>
            <p><strong>Количество точек:</strong> ${route.length}</p>
        `;
        
        routeDetails.innerHTML = html;
    }
    
    /**
     * Очистка маршрута
     */
    function clearRoute() {
        // Очистка canvas
        ctx.clearRect(0, 0, pathCanvas.width, pathCanvas.height);
        
        // Сброс выбранных точек
        startSelect.selectedIndex = 0;
        endSelect.selectedIndex = 0;
        
        // Очистка информации о маршруте
        routeDetails.innerHTML = '<p>Выберите начальную и конечную точки для построения маршрута.</p>';
        
        // Сброс текущего маршрута
        currentRoute = [];
    }
    
    /**
     * Отображение сообщения об ошибке
     */
    function showError(message) {
        routeDetails.innerHTML = `<p class="error">${message}</p>`;
    }
    
    // Запуск инициализации
    init();
});