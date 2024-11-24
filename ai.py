import json
import os
import base64
import requests
from collections import defaultdict
from random import choices


class MCCFR_AI:
    def __init__(self):
        self.regret_table = defaultdict(lambda: defaultdict(float))  # Таблица сожалений
        self.strategy_table = defaultdict(lambda: defaultdict(float))  # Таблица стратегий
        self.strategy_sum = defaultdict(lambda: defaultdict(float))  # Сумма стратегий

    def get_strategy(self, state):
        """
        Вычисляет текущую стратегию на основе сожалений.
        """
        actions = list(self.regret_table[state].keys())
        regrets = [max(0, self.regret_table[state][action]) for action in actions]
        total_regret = sum(regrets)

        if total_regret > 0:
            strategy = [regret / total_regret for regret in regrets]
        else:
            # Если нет положительных сожалений, выбираем равновероятную стратегию
            strategy = [1.0 / len(actions)] * len(actions)

        # Обновляем стратегию
        for i, action in enumerate(actions):
            self.strategy_table[state][action] = strategy[i]
            self.strategy_sum[state][action] += strategy[i]

        return {action: strategy[i] for i, action in enumerate(actions)}

    def sample_action(self, state):
        """
        Выбирает действие на основе текущей стратегии.
        """
        strategy = self.get_strategy(state)
        actions, probabilities = zip(*strategy.items())
        return choices(actions, probabilities)[0]

    def update_regret(self, state, action, regret):
        """
        Обновляет сожаление для данного действия.
        """
        self.regret_table[state][action] += regret

    def make_move(self, game_state):
        """
        Делает ход, выбирая оптимальное действие на основе MCCFR.
        """
        state = self.get_state_representation(game_state)
        action = self.sample_action(state)

        # Пример: размещение карты в указанной линии
        card = game_state["current_hand"].pop(0)
        game_state["ai_table"][action].append(card)

    def get_state_representation(self, game_state):
        """
        Преобразует состояние игры в строку для хранения в таблице.
        """
        return json.dumps(game_state, sort_keys=True)

    def save_progress(self, path="progress/ai_progress.json"):
        """
        Сохраняет прогресс MCCFR в JSON-файл.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "regret_table": self.regret_table,
                "strategy_table": self.strategy_table,
                "strategy_sum": self.strategy_sum
            }, f)

    def load_progress(self, path="progress/ai_progress.json"):
        """
        Загружает прогресс MCCFR из JSON-файла.
        """
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.regret_table = defaultdict(lambda: defaultdict(float), data["regret_table"])
                self.strategy_table = defaultdict(lambda: defaultdict(float), data["strategy_table"])
                self.strategy_sum = defaultdict(lambda: defaultdict(float), data["strategy_sum"])

    def save_to_github(self, repo, path, commit_message="Update AI progress"):
        """
        Сохраняет прогресс MCCFR в репозиторий GitHub.
        
        :param repo: Название репозитория в формате "owner/repo".
        :param path: Путь к файлу в репозитории.
        :param commit_message: Сообщение коммита.
        """
        token = os.getenv("AI_PROGRESS_TOKEN")
        if not token:
            raise Exception("AI_PROGRESS_TOKEN не установлен в переменных окружения.")

        # Преобразуем данные в JSON и кодируем в base64
        progress_data = {
            "regret_table": self.regret_table,
            "strategy_table": self.strategy_table,
            "strategy_sum": self.strategy_sum,
        }
        content = base64.b64encode(json.dumps(progress_data).encode()).decode()

        # URL для API GitHub
        url = f"https://api.github.com/repos/{repo}/contents/{path}"

        # Проверяем, существует ли файл (чтобы получить SHA для обновления)
        response = requests.get(url, headers={"Authorization": f"token {token}"})
        if response.status_code == 200:
            sha = response.json()["sha"]  # SHA текущей версии файла
        else:
            sha = None  # Файл еще не существует

        # Данные для запроса
        payload = {
            "message": commit_message,
            "content": content,
        }
        if sha:
            payload["sha"] = sha

        # Отправляем запрос на сохранение файла
        response = requests.put(
            url,
            headers={"Authorization": f"token {token}"},
            json=payload,
        )

        # Проверяем результат
        if response.status_code in [200, 201]:
            print("Прогресс успешно сохранен в GitHub.")
        else:
            print(f"Ошибка при сохранении: {response.status_code} - {response.json()}")
