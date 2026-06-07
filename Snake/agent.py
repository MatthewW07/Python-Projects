import torch
import random
import numpy as np
from collections import deque
from .game import SnakeGameAI, Direction, Point
from .model import Linear_QNet, QTrainer
from .helper import plot

MAX_MEMORY = 100000
BATCH_SIZE = 512
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # Random behavior
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() if max reached
        self.model = Linear_QNet(15, 256, 3)
        if self.model.load():
            print("Loading existing model.")
        else:
            print("No existing model found, starting fresh.")
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.position_history = deque(maxlen=8)
    
    def get_state(self, game):
        head = game.snake[0]
        snake_len = len(game.snake)

        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        point_l2 = Point(head.x - 40, head.y)
        point_r2 = Point(head.x + 40, head.y)
        point_u2 = Point(head.x, head.y - 40)
        point_d2 = Point(head.x, head.y + 40)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        cur_position = (head.x, head.y)
        self.position_history.append(cur_position)

        loop_detected = 0
        if len(self.position_history) >= 4:
            recent_positions = list(self.position_history)[-4:]
            if cur_position in recent_positions[:-1]:
                loop_detected = 1

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # Danger straight 2
            (dir_r and game.is_collision(point_r2)) or 
            (dir_l and game.is_collision(point_l2)) or 
            (dir_u and game.is_collision(point_u2)) or 
            (dir_d and game.is_collision(point_d2)),

            # Danger right 2
            (dir_u and game.is_collision(point_r2)) or 
            (dir_d and game.is_collision(point_l2)) or 
            (dir_l and game.is_collision(point_u2)) or 
            (dir_r and game.is_collision(point_d2)),

            # Danger left 2
            (dir_d and game.is_collision(point_r2)) or 
            (dir_u and game.is_collision(point_l2)) or 
            (dir_r and game.is_collision(point_u2)) or 
            (dir_l and game.is_collision(point_d2)),

            # move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location 
            game.food.x < game.head.x, # food left
            game.food.x > game.head.x, # food right
            game.food.y < game.head.y, # food up
            game.food.y > game.head.y, # food down

            loop_detected
        ]

        #state = np.array(state_part + history_state, dtype=float)
        state = np.array(state, dtype=int)
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #     self.trainer.train_step(state, action, reward, next_state, done)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        # random moves: tradeoff between exploration / exploitation
        #self.epsilon = 100 * (0.99 ** self.n_games) # Exponential decay
        #self.epsilon = max(1, 80 - self.n_games * 0.8) # Piecewise linear decay
        self.epsilon = 80 - self.n_games # Regular decrease
        #self.epsilon = 0 # No exploration
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
          
        return final_move
    
def action_to_dir(cur_dir, action):
        dir_to_num = {
            Direction.RIGHT: 1,
            Direction.LEFT: 2,
            Direction.UP: 3,
            Direction.DOWN: 4
        }
        cur_dir = dir_to_num[cur_dir]
        clock_wise = [1, 4, 2, 3]
        idx = clock_wise.index(cur_dir)

        if np.array_equal(action, [1, 0, 0]):
            # Straight
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            # Right Turn
            new_dir = clock_wise[(idx + 1) % 4]
        else:
            # Left Turn
            new_dir = clock_wise[(idx - 1) % 4]

        return new_dir
    
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game:', agent.n_games, 'Score:', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            # plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()