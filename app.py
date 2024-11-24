from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from game_logic import initialize_game, deal_next_hand, validate_hand, calculate_scores, save_game_progress
from ai import MCCFR_AI
import os

app = FastAPI()

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация игры
game_state = initialize_game()
ai_agent = MCCFR_AI()

@app.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": {}, "game_state": game_state})

@app.post("/start")
async def start_game():
    global game_state
    game_state = initialize_game()
    return {"status": "Game started", "hand": game_state["current_hand"]}

@app.post("/next")
async def next_round():
    global game_state
    if not validate_hand(game_state["player_table"]):
        raise HTTPException(status_code=400, detail="Invalid hand placement")
    if game_state["round"] >= 5:
        return {"status": "Game over", "scores": calculate_scores(game_state)}
    deal_next_hand(game_state)
    return {"status": "Next round", "hand": game_state["current_hand"]}

@app.post("/ai_move")
async def ai_move():
    global game_state
    ai_agent.make_move(game_state)
    return {"status": "AI move completed"}

@app.post("/save")
async def save_progress():
    save_game_progress(game_state)
    return {"status": "Progress saved"}
