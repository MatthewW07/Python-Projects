import random
import numpy as np
from collections import deque
import torch
from minesweeper_ai.game2 import MinesweeperAI
from minesweeper_ai.model2 import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 512
LR = 0.001

class Agent:
    def __init__(self, env: MinesweeperAI):
        self.env = env
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        input_size = env.w * env.h * 2
        output_size = env.w * env.h
        self.model = Linear_QNet(input_size, 256, output_size)
        try:
            if self.model.load():
                print("Loading existing model")
            else:
                print("No existing model found")
        except Exception:
            print("Model load failed")

        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self):
        obs = self.env.get_observation()
        return np.array(obs, dtype=np.float32).ravel()
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) == 0:
            return
        elif len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = list(self.memory)

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = max(0, 0.8 - (self.n_games * 0.02))

        valid_cells = self.env.available_actions()
        if not valid_cells:
            return random.randint(0, self.env.w * self.env.h - 1)
        
        if random.random() < self.epsilon:
            x, y = random.choice(valid_cells)
            return y * self.env.w + x
        
        state0 = torch.tensor(state, dtype=torch.float)
        with torch.no_grad():
            q_vals = self.model(state0).cpu().numpy().flatten()

        mask = np.full_like(q_vals, -1e9, dtype=float)
        for (x, y) in valid_cells:
            mask[y * self.env.w + x] = q_vals[y * self.env.w + x]
        action_idx = int(np.argmax(mask))
        return action_idx
    
def train(episodes=150):
    env = MinesweeperAI()
    agent = Agent(env)

    win_count = 0

    for ep in range(1, episodes + 1):
        env.reset()
        state_old = agent.get_state()
        done = False
        step_count = 0
        ep_reward = 0.0

        while not done:
            step_count += 1
            action_idx = agent.get_action(state_old)
            x = action_idx % env.w
            y = action_idx // env.w

            obs2, reward, done = env.step((x, y))
            state_new = np.array(obs2, dtype=np.float32).ravel()

            agent.train_short_memory(state_old, action_idx, reward, state_new, done)
            agent.remember(state_old, action_idx, reward, state_new, done)

            state_old = state_new
            ep_reward += reward

        agent.n_games += 1
        if env.hidden_space == 0:
            win_count += 1

        #print(f"Game: {ep}, Win count: {win_count}, Reward: {ep_reward}, Epsilon: {agent.epsilon}")
        agent.train_long_memory()

        if ep % 10 == 0:
            agent.model.save()
            print(f"Game: {ep}, Win count: {win_count}, Reward: {ep_reward}, Epsilon: {agent.epsilon}")

    return agent

if __name__ == '__main__':
    trained_agent = train(episodes=300)