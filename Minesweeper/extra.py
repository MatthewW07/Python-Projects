# Small runnable PyTorch example: Minesweeper probability-map model + encoder + tiny training loop
# This will:
# 1. Generate random Minesweeper boards (mines + numbers)
# 2. Reveal a small fraction of safe cells to create an "observed" board
# 3. Encode the observed board into channels (one-hot counts 0..8 + covered mask + optional scalar)
# 4. Train a tiny CNN to predict a probability map (safe vs mine) for covered cells
#
# Copy/paste or run directly. No external files required.

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random

# --------------------------- Utilities: board generation ---------------------------
def generate_board(H, W, n_mines, seed=None):
    """Return (mines_bool: HxW ndarray, counts: HxW int ndarray)"""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    cells = H * W
    # choose mine positions
    idx = np.random.choice(cells, size=n_mines, replace=False)
    mines = np.zeros(cells, dtype=np.uint8)
    mines[idx] = 1
    mines = mines.reshape(H, W)
    counts = np.zeros((H, W), dtype=np.int64)
    # compute neighbor counts
    for r in range(H):
        for c in range(W):
            if mines[r, c]:
                counts[r, c] = -1  # mine marker for clarity
            else:
                r0, r1 = max(0, r-1), min(H-1, r+1)
                c0, c1 = max(0, c-1), min(W-1, c+1)
                counts[r, c] = int(np.sum(mines[r0:r1+1, c0:c1+1]))
    return mines, counts

def reveal_random_safe_cells(mines, counts, reveal_prob=0.15, seed=None):
    """Randomly reveal a subset of safe (non-mine) cells. Returns revealed_mask (bool) and revealed_counts (int array)"""
    if seed is not None:
        np.random.seed(seed)
    H, W = mines.shape
    revealed_mask = np.zeros((H, W), dtype=bool)
    # reveal only safe cells with probability reveal_prob
    for r in range(H):
        for c in range(W):
            if not mines[r, c]:
                if np.random.rand() < reveal_prob:
                    revealed_mask[r, c] = True
    revealed_counts = np.zeros_like(counts)
    revealed_counts[revealed_mask] = counts[revealed_mask]
    return revealed_mask, revealed_counts

# --------------------------- Encoder ---------------------------
def encode_board_onehot(revealed_counts, revealed_mask, flags=None, remaining_mines_norm=None):
    """
    Build channels for the network.
    - one-hot counts for 0..8 -> 9 channels (zeros if not revealed)
    - covered_mask channel (1 if covered / unknown)
    - flag_mask channel (1 if flagged; zeros if flags None)
    - optional remaining_mines scalar duplicated
    Returns tensor shape (C, H, W) as float32
    """
    H, W = revealed_counts.shape
    # one-hot 0..8
    one_hot = np.zeros((9, H, W), dtype=np.float32)
    for v in range(9):
        one_hot[v] = (revealed_mask & (revealed_counts == v)).astype(np.float32)
    covered = (~revealed_mask).astype(np.float32)[None, ...]  # 1 x H x W
    if flags is None:
        flag_ch = np.zeros((1, H, W), dtype=np.float32)
    else:
        flag_ch = flags.astype(np.float32)[None, ...]
    channels = [one_hot, covered, flag_ch]
    tensor = np.concatenate(channels, axis=0)  # shape (C, H, W)
    if remaining_mines_norm is not None:
        scalar = np.full((1, H, W), float(remaining_mines_norm), dtype=np.float32)
        tensor = np.concatenate([tensor, scalar], axis=0)
    return torch.from_numpy(tensor).float()

# --------------------------- Tiny CNN Model ---------------------------
class MinesweeperNet(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        # small stack of convolutions. Keep receptive field at least 3x3.
        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
        # final conv maps to 1 channel (logit for "safe")
        self.out_conv = nn.Conv2d(32, 1, kernel_size=1)
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        logits = self.out_conv(x)  # shape N x 1 x H x W
        probs = torch.sigmoid(logits)
        return probs, logits

# --------------------------- Training helpers ---------------------------
def make_training_batch(batch_size, H, W, n_mines, reveal_prob=0.15):
    """Create batch of encoded inputs and targets.
    Returns:
      inputs: tensor (B, C, H, W)
      targets: tensor (B, 1, H, W) with 1 for safe, 0 for mine
      train_mask: tensor (B, 1, H, W) with 1 where we compute loss (covered cells only)
    """
    inputs = []
    targets = []
    train_masks = []
    for _ in range(batch_size):
        mines, counts = generate_board(H, W, n_mines)
        revealed_mask, revealed_counts = reveal_random_safe_cells(mines, counts, reveal_prob)
        enc = encode_board_onehot(revealed_counts, revealed_mask)  # C x H x W
        inputs.append(enc.numpy())
        # target: for covered cells, 1 if safe, 0 if mine.
        covered = (~revealed_mask).astype(np.float32)
        safe_map = (~mines).astype(np.float32)  # 1 if safe
        target = safe_map[None, ...]  # 1 x H x W
        train_mask = covered[None, ...]  # covered positions are where we want to predict
        # (we could also exclude a subset but this is fine)
        targets.append(target)
        train_masks.append(train_mask)
    inputs = torch.from_numpy(np.stack(inputs, axis=0)).float()  # B x C x H x W
    targets = torch.from_numpy(np.stack(targets, axis=0)).float()  # B x 1 x H x W
    train_masks = torch.from_numpy(np.stack(train_masks, axis=0)).float()
    return inputs, targets, train_masks

def masked_bce_loss(logits, target, mask):
    """Compute BCE on masked positions. logits assumed raw logits (not sigmoid)"""
    # Flatten masked positions and compute BCE
    # We'll use logits input to allow numerical stability
    bce = F.binary_cross_entropy_with_logits(logits, target, reduction='none')  # B x 1 x H x W
    masked = bce * mask
    # average over number of masked elements (avoid division by zero)
    denom = mask.sum()
    if denom.item() == 0:
        return masked.sum() * 0.0  # no masked positions -> zero loss
    return masked.sum() / denom

# --------------------------- Demo training loop ---------------------------
def demo_train(epochs=60, batch_size=32, H=10, W=10, n_mines=10):
    device = torch.device("cpu")
    # channels = 9(one-hot) + 1 covered + 1 flag = 11
    in_channels = 11
    model = MinesweeperNet(in_channels).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for ep in range(1, epochs+1):
        inputs, targets, masks = make_training_batch(batch_size, H, W, n_mines)
        inputs = inputs.to(device)
        targets = targets.to(device)
        masks = masks.to(device)
        model.train()
        probs, logits = model(inputs)
        loss = masked_bce_loss(logits, targets, masks)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if ep % 10 == 0 or ep == 1:
            print(f"Epoch {ep:3d} loss={loss.item():.4f}")
    # Show an example prediction
    model.eval()
    with torch.no_grad():
        inputs, targets, masks = make_training_batch(1, H, W, n_mines, reveal_prob=0.12)
        inputs = inputs.to(device); targets = targets.to(device); masks = masks.to(device)
        probs, logits = model(inputs)
        p = probs[0,0].cpu().numpy()
        t = targets[0,0].cpu().numpy()
        m = masks[0,0].cpu().numpy()
        print("\nExample prediction (probabilities) for covered cells (masked cells shown, others = -1):")
        display = np.full_like(p, -1.0)
        display[m==1] = p[m==1]
        np.set_printoptions(precision=2, suppress=True)
        print(display)
        print("\nCorresponding ground-truth (1=safe, 0=mine) for covered cells:")
        gt = np.full_like(t, -1.0)
        gt[m==1] = t[m==1]
        print(gt)
    return model

# Run the demo training
if __name__ == "__main__":
    demo_model = demo_train(epochs=60, batch_size=64, H=10, W=10, n_mines=12)
