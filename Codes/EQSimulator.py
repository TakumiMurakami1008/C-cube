import numpy as np

class EQSimulator:
    def __init__(self, epicenter, magnitude, alpha=10):
        self.epicenter = epicenter
        self.magnitude = magnitude
        self.alpha = alpha

    def compute_intensity(self, X, Y):
        """
        フィールドにおける振動の強さを計算
        """

        x0, y0 = self.epicenter
        distance = np.sqrt((X - self.x0)**2 + (Y - self.y0)**2)
        intensity = self.magnitude * np.exp(-distance / self.alpha)
        return intensity
    
    
