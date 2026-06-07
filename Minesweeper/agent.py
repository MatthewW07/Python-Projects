import torch
import random
import numpy as np
from collections import deque
from Minesweeper.game2 import MinesweeperAI, NUM_MINES
from Minesweeper.model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(81, 256, 82) # 81 board spaces, flag or reveal
        if self.model.load():
            print("Loading existing model.")
        else:
            print("No existing model found, starting fresh.")
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        board = game.board
        return np.array(board, dtype=int).flatten()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state, game):
        self.epsilon = 100 * (0.98 ** self.n_games)
        #self.epsilon = 100 - self.n_games
        #self.epsilon = 0
        final_move = [0 for _ in range(81)] + [0]
        if random.randint(0, 200) < self.epsilon:
            valid_actions = self._get_valid_actions(game)
            if valid_actions:
                move, action = random.choice(valid_actions)
                final_move[move] = 1
                final_move[81] = action
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            valid_actions = self._get_valid_actions(game)
            if not valid_actions:
                return final_move
            best_score = float('-inf')
            best_move, best_action = valid_actions[0]
            for move, action in valid_actions:
                if action == 1:
                    score = prediction[move].item()
                else:
                    score = prediction[81].item()
                if score > best_score:
                    best_score = score
                    best_move, best_action = move, action

            final_move[best_move] = 1
            final_move[81] = best_action

        return final_move
    
    def _get_valid_actions(self, game):
        valid_actions = []
        for i in range(81):
            x, y = i % game.w, i // game.w
            if game.board[y][x] == -1: # can reveal
                valid_actions.append((i, 1))
            if game.board[y][x] == -1 and (x, y) not in game.flagged and len(game.flagged) < NUM_MINES: # can flag
                valid_actions.append((i, -1))
        return valid_actions
            
    
def train():
    games_won = 0
    agent = Agent()
    game = MinesweeperAI()
    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old, game)

        move = final_move.index(1)
        action = final_move[81]

        pt = (move % game.w, move // game.w)
        reward, done = game.play_step(action, pt)
        state_new = agent.get_state(game)
        
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            if game.hidden_space == 0:
                games_won += 1
                print("Game won!")
            
            agent.n_games += 1
            
            print("Game:", agent.n_games, "Games won:", games_won, "Clicks:", game.clicks)

            game.reset()
            agent.train_long_memory()

            if agent.n_games % 10 == 0:
                agent.model.save()

if __name__ == '__main__':
    train()