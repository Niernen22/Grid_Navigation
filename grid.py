import queue
import math
import random

# Grid class felel a tanulási és döntési folyamatokért
class Grid:
    def __init__(self, start, goal, grid_map, alpha=0.1, gamma=0.9, epsilon=0.2):
        self._start = start
        self._goal = goal
        self._width = len(grid_map[0])
        self._height = len(grid_map)
        self._grid_map = grid_map 

        self.alpha = alpha  # Tanulás
        self.gamma = gamma  # Diszkontálási tényező
        self.epsilon = epsilon  # 'Felfedező' ráta

        # Q-tábla készítés
        self.q_table = {}
        for y in range(self._height):
            for x in range(self._width):
                self.q_table[(y, x)] = [0, 0, 0, 0]  # Q-értékek az akciókra (jobb, bal, fel, le)

    # Reward function
    def reward_function(self, state):
        if state == self._goal: # cél elérése
            return 1 
        if self._grid_map[state[0]][state[1]] == 1:  # akadályba ütközés
            return -1 
        return -0.1  # lépésekért járó pici büntetés

    # Lehetséges lépések az aktuális pozícióból
    def neighbors(self, position):
        (x, y) = position
        result = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)] 
        result = filter(self.within_bounds, result)
        result = filter(self.not_obstacle, result)
        return list(result)

    def within_bounds(self, position):
        (x, y) = position
        return 0 <= x < self._height and 0 <= y < self._width

    def not_obstacle(self, position):
        (x, y) = position
        return not self._grid_map[x][y]

    # Q-érték frissítése
    def update_q_value(self, current_state, action, reward, next_state):
        best_future_q = max(self.q_table[next_state]) 
        current_q = self.q_table[current_state][action]
        # Q-learning formula
        self.q_table[current_state][action] += self.alpha * (reward + self.gamma * best_future_q - current_q)

    # exploration vs exploitation
    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice([0, 1, 2, 3])
        else: 
            return max(range(4), key=lambda a: self.q_table[state][a])  # Q-tábla szerinti legkedvezőbb lépés

    # Q-learning algorithm
    def train(self, num_episodes):
        for _ in range(num_episodes):
            state = self._start
            while state != self._goal:
                action = self.choose_action(state)
                neighbors = self.neighbors(state)
                next_state = neighbors[action] if action < len(neighbors) else state

                reward = self.reward_function(next_state)
                self.update_q_value(state, action, reward, next_state)

                state = next_state

    # Legjobb út kiválasztása miután eleget tanult
    def find_best_path(self):
        state = self._start 
        path = [state]
        while state != self._goal:
            action = max(range(4), key=lambda a: self.q_table[state][a])
            neighbors = self.neighbors(state)
            next_state = neighbors[action] if action < len(neighbors) else state
            path.append(next_state)
            state = next_state
        return path

# Grid rajzolás + tréning + legjobb út
def find_optimal_path(start, goal, grid_map):
    grid = Grid(start, goal, grid_map)
    grid.train(1000)
    return grid.find_best_path()
