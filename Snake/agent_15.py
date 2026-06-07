import torch
import random
import numpy as np
from collections import deque
from SnakeAI.game import SnakeGameAI, Direction, Point
from SnakeAI.model import Linear_QNet, QTrainer
from SnakeAI.helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(15, 256, 3)
        if self.model.load():
            print("Loading existing model.")
        else:
            print("No existing model found, starting fresh.")
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        head = game.snake[0]

        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        def get_near_body(game):
            head = game.snake[0]
            body_features = []

            directions = [ (-20, 0), (20, 0), (0, -20), (0, 20), (-20, -20), (20, -20), (-20, 20), (20, 20) ]

            for dx, dy in directions:
                new_point = Point(head.x + dx, head.y + dy)
                body_features.append(1 if new_point in game.snake[1:] else 0)

            return body_features # 8
        
        def get_escape_route(game):
            head = game.snake[0]
            escape_features = []

            directions = [ (-20, 0), (20, 0), (0, -20), (0, 20) ]

            for dx, dy in directions:
                available = 0
                new_point = Point(head.x + dx, head.y + dy)

                if not game.is_collision(new_point):
                    for steps in range(1, 6):
                        test_point = Point(head.x + dx * steps, head.y + dy * steps)
                        if not game.is_collision(test_point):
                            available += 1
                        else:
                            break
                            
                escape_features.append(available)

            return escape_features # 4
        
        def get_available_space(game, start_point, max_depth=5):
            if game.is_collision(start_point):
                return 0
            
            visited = set()
            queue = [start_point]
            count = 0

            while queue and count < max_depth:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                count += 1

                for dx, dy in [(20, 0), (-20, 0), (0, 20), (0, -20)]:
                    next_point = Point(current.x + dx, current.y + dy)
                    if not game.is_collision(next_point) and next_point not in visited:
                        queue.append(next_point)

            return count
        
        space_l = get_available_space(game, point_l)
        space_r = get_available_space(game, point_r)
        space_u = get_available_space(game, point_u)
        space_d = get_available_space(game, point_d)
        space_features = [
            space_l, space_r, space_u, space_d
        ]

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
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        state = state + get_escape_route(game)
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        #self.epsilon = 80 - self.n_games
        self.epsilon = 0
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


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

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            #plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()