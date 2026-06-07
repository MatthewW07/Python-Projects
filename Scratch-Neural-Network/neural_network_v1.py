import numpy as np
import matplotlib.pyplot as plt

class NeuralNetwork:
    def __init__(self, layerSizes: tuple[int]):
        self.layerSizes = layerSizes
        self.weights = [np.random.randn(nodesOut, nodesIn) * np.sqrt(1.0 / nodesIn) for nodesIn, nodesOut in zip(layerSizes[:-1], layerSizes[1:])]
        self.biases = [np.zeros((s, 1)) for s in layerSizes[1:]]

    def predict(self, inputs: np.ndarray[float]) -> np.ndarray[float]:
        a = inputs.reshape(-1, 1)
        for w, b in zip(self.weights, self.biases):
            z = np.dot(w, a) + b
            a = self.Activation(z)
        return a
    
    def print_accuracy(self, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[float]) -> None:
        num_correct = 0
        for image, label in zip(images, labels):
            prediction = self.predict(image)
            if np.argmax(prediction) == np.argmax(label):
                num_correct += 1
        print('{0}/{1} accuracy: {2}%'.format(num_correct, len(images), num_correct / len(images) * 100))
    
    def CrossEntropyCost(self, predictions: np.ndarray[float], label: np.ndarray[float]) -> float:
        predictions = np.clip(predictions, 1e-6, 1 - 1e-6)
        return - np.sum(label * np.log(predictions))

    def learn(self, learnRate: float, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[np.ndarray[float]], verbose: int = 100) -> bool:
        epoch = 0
        epochLoss = 0.0

        for image, label in zip(images, labels):
            epoch += 1
            image = self.addNoise(image)
            image = np.asarray(image)
            if image.ndim == 1:
                image = image.reshape(-1, 1)
            label = np.asarray(label)
            if label.ndim == 1:
                label = label.reshape(-1, 1)

            a = image
            weightedInputs = [] # length is the number of layers - 1 (represents between layers)
            activations = [a] # length is the number of layers
            for w, b in zip(self.weights, self.biases):
                z = np.dot(w, a) + b
                a = self.Activation(z)
                weightedInputs.append(z)
                activations.append(a)

            epochLoss += self.CrossEntropyCost(activations[-1], label)

            # Create Gradients
            delta = (activations[-1] - label) * self.ActivationDerivative(weightedInputs[-1])
            costGradientW = [np.zeros(w.shape) for w in self.weights]
            costGradientB = [np.zeros(b.shape) for b in self.biases]
            costGradientW[-1] = np.dot(delta, activations[-2].T)
            costGradientB[-1] = delta
            
            numLayers = len(self.layerSizes)
            for i in range(2, numLayers):
                #idx = numLayers - i
                idx = -i
                delta = np.dot(self.weights[idx+1].T, delta) * self.ActivationDerivative(weightedInputs[idx])
                costGradientW[idx] = np.dot(delta, activations[idx-1].T)
                costGradientB[idx] = delta

            # Apply Gradients
            self.weights = [w - learnRate * newW for w, newW in zip(self.weights, costGradientW)]
            self.biases = [b - learnRate * newB for b, newB in zip(self.biases, costGradientB)]
            
        return True

    def addNoise(self, image):
        noise = np.random.exponential(scale=0.2, size=image.shape[0])
        noise = noise / (np.max(noise) + 1e-9)
        noise = noise.reshape(image.shape[0], image.shape[1])
        return image + noise
    
    def Activation(self, x: np.ndarray[float]) -> np.ndarray[float]:
        clipped = np.clip(x, -100, 100)
        return 1 / (1 + np.exp(-clipped))
        
    # dA/dZ
    def ActivationDerivative(self, x: np.ndarray[float]) -> np.ndarray[float]:
        activation = self.Activation(x)
        return activation * (1 - activation)