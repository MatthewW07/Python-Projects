import neural_network_v1 as nn
import neural_network_v2 as nn2
import numpy as np
import drawing as drawing
import pickle
import os

model_path = os.path.join(os.path.dirname(__file__), "mnist.npz")
net_path1 = "net_model1.pkl"
net_path2 = "net_model2.pkl"
cur_path = net_path1
model = nn
train = True
plot  = False
load  = False
save  = True
size  = 5000
layer_sizes = (784, 128, 64, 10)

if load:
    print("Attempting to load model")
    if os.path.exists(cur_path):
        print("Loading existing model")
        file = open(cur_path, "rb")
        net = pickle.load(file)
    else:
        print("No model found")
        net = model.NeuralNetwork(layer_sizes)
else:
    print("Creating new model")
    net = model.NeuralNetwork(layer_sizes)
    

if train:
    print("Attempting to train model")
    with np.load(model_path) as data:
        training_images = data['training_images'][:size]
        training_labels = data['training_labels'][:size]
        test_images = data['test_images'][:10]
        test_labels = data['test_labels'][:10]

    print("Accuracy before training:")
    net.print_accuracy(training_images, training_labels)
    net.print_accuracy(test_images, test_labels)
    print("Training...")
    #net.learn(0.5, training_images, training_labels, test_images, test_labels, 100)
    for i in range(2):
        net.learn(0.4, training_images, training_labels, 100)
    print("Accuracy after training:")
    net.print_accuracy(training_images, training_labels)
    net.print_accuracy(test_images, test_labels)

if plot:
    net.plotTraining()

drawing = drawing.Drawing(net)
drawing.main()

if save:
    print("Saving model")
    file = open(cur_path, "wb")
    pickle.dump(net, file)


# TODO: 
# add noise to the training data to prevent memorization
# add a way for the user to input the label along with the image to train the AI