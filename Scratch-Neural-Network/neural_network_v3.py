import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

data = np.load("mnist.npz")

trainingImages = data['training_images']
trainingLabels = data['training_labels']
testImages = data['test_images']
testLabels =data['test_labels']
validationImages = data['validation_images']
validationLabels = data['validation_labels']

device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
print(f"Using {device} device")

class NeuralNetwork(nn.Module):
    def __init__(self, layerSizes: tuple[int]) -> None:
        super(NeuralNetwork, self).__init__()
        self.layers = []
        for nodesIn, nodesOut in zip(layerSizes[:-1], layerSizes[1:]):
            self.layers.append(nn.Linear(nodesIn, nodesOut))
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        out = None
        for layer in self.layers:
            out = layer(x) if out is None else layer(out)
            out = self.relu(out)
        return out
    
model = NeuralNetwork((784, 512, 512, 10)).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epoch = 0
epochLoss = 0.0
for image, label in zip(trainingImages, trainingLabels):
    image = torch.from_numpy(image).float().to(device)
    label = torch.from_numpy(label).long().to(device)
    optimizer.zero_grad()
    output = model(image)
    loss = criterion(output, label)
    loss.backward()
    optimizer.step()

    epoch += 1
    epochLoss += loss.item()
