import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Union, Sequence

MODEL_DIR = "./Minesweeper_AI/MinesweeperModel"

class Linear_QNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.net = nn.Sequential(
            nn.Linear(self.input_size, self.hidden_size), nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size), nn.ReLU(),
            nn.Linear(self.hidden_size, self.output_size)
        ).to(self.device)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not torch.is_tensor(x):
            x = torch.tensor(x, dtype=torch.float, device=self.device)
        else:
            x = x.to(self.device)
        if x.dim() == 1:
            x = x.unsqueeze(0)
            out = self.net(x)
            return out.squeeze(0)
        return self.net(x)
    
    def save(self):
        model_folder_path = MODEL_DIR
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = "model" + str(self.input_size) + ".pth"
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self) -> bool:
        model_folder_path = MODEL_DIR
        file_name = "model" + str(self.input_size) + ".pth"
        file_name = os.path.join(model_folder_path, file_name)

        if os.path.exists(file_name):
            self.load_state_dict(torch.load(file_name))
            return True
        return False
    
class QTrainer:
    def __init__(self, model: Linear_QNet, lr: float = 0.001, gamma: float = 0.99):
        self.model = model
        self.gamma = gamma
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

    def _to_tensor(self, x, dtype=torch.float):
        if isinstance(x, torch.Tensor):
            t = x
        else:
            t = torch.tensor(x, dtype=dtype)
        return t
    
    def train_step(self,
                   states: Union[np.ndarray, Sequence],
                   actions: Union[int, Sequence],
                   rewards: Union[float, Sequence],
                   next_states: Union[np.ndarray, Sequence],
                   dones: Union[bool, Sequence]) -> float:
        
        states = np.array(states, dtype=np.float32)
        actions = np.array(actions, dtype=np.int64)
        rewards = np.array(rewards, dtype=np.float32)
        next_states = np.array(next_states, dtype=np.float32)
        dones = np.array(dones, dtype=np.float32)

        if states.ndim == 1:
            states = states.reshape(1, -1)
            actions = actions.reshape(1,)
            rewards = rewards.reshape(1,)
            next_states = next_states.reshape(1, -1)
            dones = dones.reshape(1,)

        states = self._to_tensor(states, dtype=torch.float)
        actions = self._to_tensor(actions, dtype=torch.long)
        rewards = self._to_tensor(rewards, dtype=torch.float)
        next_states = self._to_tensor(next_states, dtype=torch.float)
        dones = self._to_tensor(dones, dtype=torch.float)

        self.model.train()
        pred_q_all = self.model(states)
        actions = actions.view(-1, 1)
        pred_q = pred_q_all.gather(1, actions).squeeze(1)

        with torch.no_grad():
            next_q_all = self.model(next_states)
            next_q_max, _ = next_q_all.max(dim=1)
            target_q = rewards + self.gamma * next_q_max * (1 - dones)

        loss = self.criterion(pred_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()