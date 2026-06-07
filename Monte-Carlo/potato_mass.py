import numpy as np
import matplotlib.pyplot as plt

diameter = 2
length = 4
density = 1.087
mean = 1.087
std = 0.010

class MonteCarlo:
    def __init__(self, mean, std, n, trials):
        self.mean = mean
        self.std = std
        self.n = n
        self.trials = trials

    def one_trial(self):
        samples = np.random.normal(loc=self.mean, scale=self.std, size=self.n)
        return np.mean(samples)
    
    def simulation(self):
        estimates = np.array([self.one_trial() for _ in range(self.trials)])
        return estimates
    
    def plot_results(self):
        estimates = self.simulation()

        print(f"Average: {estimates.mean()}")
        print(f"Standard Dev: {estimates.std(ddof=1)}")

        plt.figure(figsize=(10, 5))
        """Line Plot"""
        # plt.plot(range(1, trials+1), estimates, marker="o", linestyle="-", label="Estimate")
        # plt.axhline(np.pi, linestyle="--", label="π")

        """Histogram"""
        plt.hist(estimates, bins=25, edgecolor="black", alpha=0.5)

        plt.xlabel("Trial")
        plt.ylabel("Estimate of π")
        plt.title(f"Monte Carlo Estimates({self.trials} trials, n={self.n} each)")
        plt.legend()
        plt.show()
        

mc = MonteCarlo(mean, std, 10000, 1000)
mc.plot_results()