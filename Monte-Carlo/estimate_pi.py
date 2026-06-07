import numpy as np
import matplotlib.pyplot as plt


class MonteCarlo:
    def __init__(self, n=10000, trials=100):
        self.n = n
        self.trials = trials

    def estimate_pi(self):
        points = np.random.rand(self.n, 2)
        magnitudes = np.linalg.norm(points, axis=1)
        valid_points = magnitudes <= 1

        inside = valid_points.sum()
        ratio = inside / self.n

        return 4 * ratio
    
    def simulate(self):
        estimates = np.array([self.estimate_pi() for _ in range(self.trials)])
        return estimates

    def plot_results(self):
        estimates = self.simulate()

        print(f"Average: {estimates.mean()}")
        print(f"Standard Dev: {estimates.std(ddof=1)}")

        plt.figure(figsize=(10, 5))
        """Line Plot"""
        # plt.plot(range(1, trials+1), estimates, marker="o", linestyle="-", label="Estimate")
        # plt.axhline(np.pi, linestyle="--", label="π")

        """Histogram"""
        plt.hist(estimates, bins=40, edgecolor="black", alpha=0.75)
        plt.axvline(np.pi, linestyle="--", label="π")

        plt.xlabel("Trial")
        plt.ylabel("Estimate of π")
        plt.title(f"Monte Carlo Estimates of π ({self.trials} trials, n={self.n} each)")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    mc = MonteCarlo(n=10000, trials=1000)
    mc.plot_results()