import random
import os
import json

def initialize_game():
    deck = generate_deck()
    random.shuffle(deck)
    return {
        "deck": deck,
        "player_table": {"top": [], "middle": [], "bottom": []},
        "ai_table": {"top": [], "middle": [], "bottom": []},
        "current_hand": deck[:5],
        "used_cards": deck[:5],
        "round": 1
    }

def generate_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [f"{rank}{suit}" for suit in suits for rank in ranks]

def deal_next_hand(game_state):
    game_state["current_hand"] = game_state["deck"][:3]
    game_state["used_cards"].extend(game_state["deck"][:3])
    game_state["deck"] = game_state["deck"][3:]
    game_state["round"] += 1

def validate_hand(player_table):
    def strength(line):
        # Простая функция для определения силы линии
        return sum([ord(card[0]) for card in line])

    top = strength(player_table["top"])
    middle = strength(player_table["middle"])
    bottom = strength(player_table["bottom"])
    return top <= middle <= bottom

def calculate_scores(game_state):
    player_scores = {"top": 0, "middle": 0, "bottom": 0}
    ai_scores = {"top": 0, "middle": 0, "bottom": 0}
    for line in ["top", "middle", "bottom"]:
        if sum(game_state["player_table"][line]) > sum(game_state["ai_table"][line]):
            player_scores[line] += 1
        else:
            ai_scores[line] += 1
    return {"player": player_scores, "ai": ai_scores}

def save_game_progress(game_state):
    token = os.getenv("AI_PROGRESS_TOKEN")
    if not token:
        raise Exception("AI_PROGRESS_TOKEN not set")
    with open(f"progress/{token}.json", "w") as f:
        json.dump(game_state, f)
