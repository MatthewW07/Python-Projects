import numpy as np
import math

class NeuralNetwork:
    def __init__(self, layerSizes: tuple[int]):
        self.layerSizes = layerSizes
        self.layers = [Layer(a, b) for a, b in zip(layerSizes[:-1], layerSizes[1:])]
        weight_shapes = [(a, b) for a, b in zip(layerSizes[1:], layerSizes[:-1])]
        self.weights = [np.random.randn(nodesOut, nodesIn) * np.sqrt(1.0 / nodesIn) for nodesIn, nodesOut in zip(layerSizes[:-1], layerSizes[1:])]
        #self.weights = [np.random.standard_normal(s) * np.sqrt(2.0 / s[1]) for s in weight_shapes]
        self.biases = [np.zeros((s, 1)) for s in layerSizes[1:]]

    # Seb's version is "CalculateOutputs()"
    def predict(self, inputs: np.ndarray[float]) -> np.ndarray[float]:
        a = inputs.reshape(-1, 1)
        for w, b in zip(self.weights, self.biases):
            z = np.dot(w, a) + b
            a = Activation(z)
        return a
    
        # Previous code
        for idx, layer in enumerate(self.layers):
            a = layer.calculateOutput(a, self.weights[idx], self.biases[idx])
        return a

        # Previous code
        for layer in self.layers:
            z = layer.calculateOutput(a)
            for i in range(len(z)):
                a[i] = Activation(z, i)
                layer.activations[i] = a[i]
        return a
    
    def print_accuracy(self, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[float]) -> None:
        num_correct = 0
        for image, label in zip(images, labels):
            prediction = self.predict(image)
            if np.argmax(prediction) == np.argmax(label):
                num_correct += 1
        print('{0}/{1} accuracy: {2}%'.format(num_correct, len(images), num_correct / len(images) * 100))

    def singleCost(self, image: np.ndarray[float], label: np.ndarray[float]) -> float:
        outputs: np.ndarray[float] = self.predict(image)
        cost = np.sum(np.square(outputs - label))
        return cost
    
    def Cost(self, images: np.ndarray[np.ndarray[float]], labels: np.ndarray[np.ndarray[float]]) -> float:
        total: float = 0.0
        for image, label in zip(images, labels):
            total += self.singleCost(image, label)
        return total / len(images)
    
    def CrossEntropyLoss(self, predictions: np.ndarray[float], label: np.ndarray[float]) -> float:
        predictions = np.clip(predictions, 1e-6, 1 - 1e-6)
        return - np.sum(label * np.log(predictions))

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
            weightedInputs = [] # length is the number of layers - 1 (represents between layers)
            activations = [a] # length is the number of layers
            for w, b in zip(self.weights, self.biases):
                z = np.dot(w, a) + b
                a = Activation(z)
                weightedInputs.append(z)
                activations.append(a)

            epochLoss += self.CrossEntropyLoss(activations[-1], label)

            # Create Gradients
            delta = 2 * (activations[-1] * label) * ActivationDerivative(weightedInputs[-1])
            costGradientW = [np.zeros(w.shape) for w in self.weights]
            costGradientB = [np.zeros(b.shape) for b in self.biases]
            costGradientW[-1] = delta * activations[-2].T
            costGradientB[-1] = delta
            numLayers = len(self.layerSizes)
            for i in range(2, numLayers):
                idx = numLayers - i
                delta = np.dot(self.weights[idx].T, delta) * ActivationDerivative(weightedInputs[idx-1])
                costGradientW[idx] = np.dot(delta, activations[idx-1].T)
                costGradientB[idx] = delta

            # Apply Gradients
            self.weights = [w - learnRate * newW for w, newW in zip(self.weights, costGradientW)]
            self.biases = [b - learnRate * newB for b, newB in zip(self.biases, costGradientB)]

            avgLoss = epochLoss / epoch

    def updateAllGradients(self, prediction: np.ndarray[float], label: np.ndarray[float]) -> None:
        # There is a weight and bias gradient for each layer
        # To update any gradient, we need it's derivative/direction
        # If it is a weight gradient, it is the derivative of Loss as the Weights change
        # If it is a bias gradient, it is the derivative of Loss as the Biases change

        """
        DERIVATIVES:
        dCost/dw = dCost/da * da/dz * dz/dw
            dCost/da_i = 2 * (a_i - label)
            da_i/dz_i = A(z_i) * (1 - A(z_i))
            dz_i/dw_i = a_(i-1)
        the graph where we need gradient descent is the cost function according to the weights
        nodeValues = dCost/da_i * da_i/dz_i

        The weights will be updated using the derivative as w = w - lr * dCost/dw
        """
        dCost_dai = 2 * (prediction - label)
        dai_dzi = ActivationDerivative()
        pass
        

    
def Activation(x: np.ndarray[float]) -> np.ndarray[float]:
    clipped = np.clip(x, -100, 100)
    return 1 / (1 + np.exp(-clipped))
    
# dA/dZ
def ActivationDerivative(x: np.ndarray[float]) -> np.ndarray[float]:
    activation = Activation(x)
    return activation * (1 - activation)


class Layer:
    def __init__(self, nodesIn: int, nodesOut: int) -> None:
        self.nodesIn = nodesIn
        self.nodesOut = nodesOut
        self.costGradientW = np.zeros((nodesOut, nodesIn))
        self.costGradientB = np.zeros((nodesOut, 1))
        self.inputs = np.zeros((nodesIn, 1))
        self.weightedInputs = np.zeros((nodesOut, 1))
        self.activations = np.zeros((nodesOut, 1))

    def applyGradients(self, learnRate: float, weights: np.ndarray[np.ndarray[float]], biases: np.ndarray[float]) -> tuple[np.ndarray[np.ndarray[float]], np.ndarray[float]]:
        weights -= self.costGradientW * learnRate
        biases -= self.costGradientB * learnRate
        self.costGradientW.fill(0)
        self.costGradientB.fill(0)

    # UNUSED
    def calculateOutput(self, inputs: np.ndarray[float], weights: np.ndarray[np.ndarray[float]], biases: np.ndarray[float]) -> np.ndarray:
        # New version (with np matrices)
        inputs = np.asarray(inputs)
        if inputs.ndim == 1:
            inputs = inputs.reshape(-1, 1)
        self.inputs = inputs
        self.weightedInputs = np.matmul(weights, inputs) + biases
        self.activations = Activation(self.weightedInputs)
        return self.activations

        # Old version
        for nodeOut in range(self.nodesOut):
            weightedInput = biases[nodeOut]
            for nodeIn in range(self.nodesIn):
                self.inputs[nodeIn] = inputs[nodeIn]
                weightedInput += inputs[nodeIn] * weights[nodeOut][nodeIn]
            self.weightedInputs[nodeOut] = weightedInput
        return self.weightedInputs

        # Previous code
        for nodeOut in range(self.nodesOut):
            weightedInput = self.biases[nodeOut]
            for nodeIn in range(self.nodesIn):
                self.inputs[nodeIn] = inputs[nodeIn]
                weightedInput += inputs[nodeIn] * self.weights[nodeIn][nodeOut]
            self.weightedInputs[nodeOut] = weightedInput
        return self.weightedInputs
    
    # UNUSED
    def nodeCost(outputActivation: float, expectedOutput: float) -> float:
        error: float = outputActivation - expectedOutput
        return error * error

    def nodeCostDerivative(self, activations: np.ndarray[float], label: np.ndarray[float]) -> np.ndarray[float]:
        return 2 * (activations - label)
    
    def CalculateOutputLayerNodeValues(self, label: np.ndarray[float]) -> np.ndarray[float]:
        costDerivative: np.ndarray[float] = self.nodeCostDerivative(self.activations, label)
        activationDerivative: np.ndarray[float] = ActivationDerivative(self.weightedInputs)
        nodeValues: np.ndarray[float] = costDerivative * activationDerivative
        return nodeValues
        
        # Old version
        nodeValues = [0] * len(label)
        for i in range(len(label)):
            costDerivative: float = self.nodeCostDerivative(self.activations[i], label[i])
            activationDerivative: float = ActivationDerivative(self.weightedInputs[i])
            nodeValues[i] = costDerivative * activationDerivative
        return nodeValues

    def CalculateHiddenLayerNodeValues(self, weights: np.ndarray[np.ndarray[float]], oldNodeValues: np.ndarray[float]):
        newNodeValues = np.matmul(weights.T, oldNodeValues)
        newNodeValues = newNodeValues * ActivationDerivative(self.weightedInputs)
        return newNodeValues

    def updateGradients(self, nodeValues: np.ndarray[float]) -> None:
        nodeValues = np.asarray(nodeValues)
        if nodeValues.ndim == 1:
            nodeValues = nodeValues.reshape(-1, 1)
        self.costGradientW += np.matmul(nodeValues, self.inputs.T)
        self.costGradientB += nodeValues