// URL API
const API_URL = "/";

// Переменные для хранения состояния игры
let currentHand = [];
let playerTable = {
    top: [],
    middle: [],
    bottom: []
};

// Функция для генерации SVG-карты
function generateCardSVG(card) {
    const [rank, suit] = [card.slice(0, -1), card.slice(-1)];
    const colors = { "♠": "black", "♣": "black", "♥": "red", "♦": "red" };

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", "100");
    svg.setAttribute("height", "150");

    // Фон карты
    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("width", "100");
    rect.setAttribute("height", "150");
    rect.setAttribute("fill", "white");
    rect.setAttribute("stroke", "black");
    rect.setAttribute("stroke-width", "2");
    rect.setAttribute("rx", "10");
    rect.setAttribute("ry", "10");

    // Верхний текст (номинал и масть)
    const textTop = document.createElementNS(svgNS, "text");
    textTop.setAttribute("x", "10");
    textTop.setAttribute("y", "30");
    textTop.setAttribute("font-size", "20");
    textTop.setAttribute("fill", colors[suit]);
    textTop.textContent = `${rank}${suit}`;

    // Нижний текст (номинал и масть, перевернутый)
    const textBottom = document.createElementNS(svgNS, "text");
    textBottom.setAttribute("x", "70");
    textBottom.setAttribute("y", "140");
    textBottom.setAttribute("font-size", "20");
    textBottom.setAttribute("fill", colors[suit]);
    textBottom.setAttribute("transform", "rotate(180, 70, 140)");
    textBottom.textContent = `${rank}${suit}`;

    // Добавляем элементы в SVG
    svg.appendChild(rect);
    svg.appendChild(textTop);
    svg.appendChild(textBottom);

    return svg;
}

// Отображение текущей руки
function renderHand(hand) {
    const handDiv = document.getElementById("hand");
    handDiv.innerHTML = ""; // Очищаем предыдущие карты

    hand.forEach(card => {
        const cardSVG = generateCardSVG(card);
        cardSVG.classList.add("card");
        cardSVG.setAttribute("draggable", "true");

        // Добавляем обработчики для drag-and-drop
        cardSVG.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("text/plain", card);
        });

        handDiv.appendChild(cardSVG);
    });
}

// Отображение таблицы игрока
function renderPlayerTable() {
    ["top", "middle", "bottom"].forEach(line => {
        const lineDiv = document.getElementById(`player-${line}`);
        lineDiv.innerHTML = ""; // Очищаем предыдущие карты

        playerTable[line].forEach(card => {
            const cardSVG = generateCardSVG(card);
            lineDiv.appendChild(cardSVG);
        });
    });
}

// Обработчик для начала игры
document.getElementById("start").addEventListener("click", async () => {
    const response = await fetch(`${API_URL}start`, { method: "POST" });
    const data = await response.json();

    currentHand = data.hand;
    playerTable = { top: [], middle: [], bottom: [] };

    renderHand(currentHand);
    renderPlayerTable();
});

// Обработчик для следующей раздачи
document.getElementById("next").addEventListener("click", async () => {
    // Проверяем, все ли карты из руки размещены
    if (currentHand.length > 0) {
        alert("Вы должны разложить все карты перед продолжением!");
        return;
    }

    const response = await fetch(`${API_URL}next`, { method: "POST" });
    const data = await response.json();

    if (data.status === "Game over") {
        alert("Игра завершена! Подсчет очков...");
        console.log(data.scores); // Выводим итоговые очки
    } else {
        currentHand = data.hand;
        renderHand(currentHand);
    }
});

// Обработчики для drag-and-drop
["top", "middle", "bottom"].forEach(line => {
    const lineDiv = document.getElementById(`player-${line}`);

    lineDiv.addEventListener("dragover", (e) => {
        e.preventDefault(); // Разрешаем перетаскивание
    });

    lineDiv.addEventListener("drop", (e) => {
        e.preventDefault();
        const card = e.dataTransfer.getData("text/plain");

        // Добавляем карту в соответствующую линию
        if (!playerTable[line].includes(card)) {
            playerTable[line].push(card);
            currentHand = currentHand.filter(c => c !== card); // Убираем карту из руки
            renderHand(currentHand);
            renderPlayerTable();
        }
    });
});

// Сохранение прогресса в GitHub
document.getElementById("save-github").addEventListener("click", async () => {
    const response = await fetch(`${API_URL}save_to_github`, { method: "POST" });
    const data = await response.json();

    if (data.status === "Progress successfully saved to GitHub") {
        alert("Прогресс успешно сохранен в GitHub!");
    } else {
        alert(`Ошибка: ${data.error}`);
    }
});
