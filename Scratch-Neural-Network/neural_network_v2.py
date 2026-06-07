import numpy as np
import matplotlib.pyplot as plt

class NeuralNetwork:
    def __init__(self, layerSizes: tuple[int], activation: str = 'sigmoid'):
        self.layerSizes = layerSizes
        self.weights = [np.random.randn(nodesOut, nodesIn) * np.sqrt(1.0 / nodesIn) for nodesIn, nodesOut in zip(layerSizes[:-1], layerSizes[1:])]
        self.biases = [np.zeros((s, 1)) for s in layerSizes[1:]]
        self.activation = activation

        self.epochs = []
        self.losses = []
        self.trainingAccuracies = []
        self.testingAccuracies = []

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

    def learn(self, learnRate: float, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[np.ndarray[float]], testingImages, testingLabels, verbose: int = 100):
        epoch = 0
        epochLoss = 0.0
        for image, label in zip(images, labels):
            epoch += 1
            image = np.asarray(image)
            if image.ndim == 1:
                image = image.reshape(-1, 1)
            label = np.asarray(label)
            if label.ndim == 1:
                label = label.reshape(-1, 1)

            a = image
            zs = []
            activations = [a]
            for w, b in zip(self.weights, self.biases):
                z = np.dot(w, a) + b
                a = self.Activation(z)
                zs.append(z)
                activations.append(a)

            epochLoss += self.crossEntropyLoss(activations[-1], label)

            # delta is 0.5 * dCost/da * da/dz, or nodeValues
            delta = (activations[-1] - label) * self.ActivationDerivative(zs[-1]) # * 2
            nablaW = [np.zeros(w.shape) for w in self.weights] # costGradientW / new weights
            nablaB = [np.zeros(b.shape) for b in self.biases] # costGradientB / new biases
            nablaW[-1] = np.dot(delta, activations[-2].T)
            nablaB[-1] = delta

            for layer in range(2, len(self.layerSizes)):
                z = zs[-layer]
                sp = self.ActivationDerivative(z)
                delta = np.dot(self.weights[-layer+1].T, delta) * sp
                nablaW[-layer] = np.dot(delta, activations[-layer-1].T)
                nablaB[-layer] = delta

            self.weights = [w - learnRate * nw for w, nw in zip(self.weights, nablaW)]
            self.biases = [b - learnRate * nb for b, nb in zip(self.biases, nablaB)]

            avgLoss = epochLoss / len(images)

            if epoch % verbose == 0:
                learnRate *= 0.99
                self.trainingAccuracies.append(self.accuracy(images, labels))
                self.testingAccuracies.append(self.accuracy(testingImages, testingLabels))
                self.losses.append(avgLoss)
                self.epochs.append(epoch)


    def accuracy(self, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[float], batchSize: int = 250) -> float:
        correct = 0.0
        sample = np.random.choice(len(images), batchSize, False)
        for idx in sample:
            image, label = images[idx], labels[idx]
            prediction = self.predict(image)
            if np.argmax(prediction) == np.argmax(label):
                correct += 1
        return correct / len(sample) * 100

    def Activation(self, x: np.ndarray[float]) -> np.ndarray[float]:
        if self.activation == 'sigmoid':
            clipped = np.clip(x, -100, 100)
            return 1 / (1 + np.exp(-clipped))
        elif self.activation == 'relu':
            return np.maximum(0, x)

    def ActivationDerivative(self, x: np.ndarray[float]) -> np.ndarray[float]:
        if self.activation == 'sigmoid':
            activation = self.Activation(x)
            return activation * (1 - activation)
        elif self.activation == 'relu':
            return np.where(x > 0, 1, 0)
        
    def crossEntropyLoss(self, predictions: np.ndarray[float], label: np.ndarray[float]) -> float:
        predictions = np.clip(predictions, 1e-6, 1-1e-6)
        return -np.sum(label * np.log(predictions))
    
    def plotTraining(self):
        if not self.epochs:
            print("No training data")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # Accuracy
        ax1.plot(self.epochs, self.trainingAccuracies, label="Training Accuracy")
        ax1.plot(self.epochs, self.testingAccuracies, label="Test Accuracy")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Accuracy (%)")
        ax1.set_title("Training & Testing Accuracy")
        ax1.legend()
        ax1.grid(True)

        # Loss
        ax2.plot(self.epochs, self.losses, label="Loss", color="red")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Loss")
        ax2.set_title("Training Loss")
        ax2.legend()
        ax2.grid(True)

        plt.show()
        