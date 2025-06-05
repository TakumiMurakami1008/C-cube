# import numpy as np

# # class EQSimulator:
# #     def __init__(self, epicenter, magnitude, alpha=10):
# #         self.epicenter = epicenter # 震源地のxy座標。 tuple(int, int): (x0, y0)
# #         self.magnitude = magnitude # マグニチュード値。 （int）
# #         self.alpha = alpha # 減衰係数
        
# #     def compute_intensity(self, X, Y):
# #         """
# #         フィールドにおける振動の強さを計算
# #         """

# #         x0, y0 = self.epicenter
# #         distance = np.sqrt((X - x0)**2 + (Y - y0)**2)
# #         intensity = self.magnitude * np.exp(-distance / self.alpha)
# #         return intensity

# class EQSimulatorVariableRho:
#     def __init__(self, epicenter, magnitude, grid_shape, rho_map, dx=1.0, dt=0.1, mu=1.0):
#         self.epicenter = epicenter # 震源座標（x,y）
#         self.magnitude = magnitude # マグニチュード値（float）
#         self.dx = dx
#         self.dt = dt
#         self.mu = mu  # 一様な剛性。もし空間変化も考えるなら mu_map にする
#         self.rho = rho_map  # 密度マップ（2D配列）

#         self.nx, self.ny = grid_shape
#         self.u_prev = np.zeros(grid_shape)
#         self.u_curr = np.zeros(grid_shape)
#         self.u_max = np.zeros(grid_shape)

#         x0, y0 = epicenter
#         self.u_curr[x0, y0] = magnitude

#     def laplacian(self, u):
#         return (
#             -4 * u
#             + np.roll(u, 1, axis=0)
#             + np.roll(u, -1, axis=0)
#             + np.roll(u, 1, axis=1)
#             + np.roll(u, -1, axis=1)
#         ) / (self.dx ** 2)

#     def step(self):
#         # 各点での波動速度 c(x, y)
#         c = np.sqrt(self.mu / self.rho)

#         # 変化する速度に対応した項を計算
#         u_next = (
#             2 * self.u_curr - self.u_prev
#             + (c ** 2) * (self.dt ** 2) * self.laplacian(self.u_curr)
#         )

#         self.u_max = np.maximum(self.u_max, np.abs(u_next))
#         self.u_prev = self.u_curr
#         self.u_curr = u_next

#     def run(self, steps=10000):
#         for _ in range(steps):
#             self.step()
#         return self.u_max


import numpy as np

class EQSimulatorVariableRho:
    def __init__(self, epicenter, magnitude, grid_shape, rho_map, dx=1.0, dt=0.1, mu=1.0, damping_width= 1):
        self.epicenter = epicenter
        self.magnitude = magnitude
        self.dx = dx
        self.dt = dt
        self.mu = mu
        self.rho = rho_map

        self.nx, self.ny = grid_shape
        self.u_prev = np.zeros(grid_shape)
        self.u_curr = np.zeros(grid_shape)
        self.u_max = np.zeros(grid_shape)

        x0, y0 = epicenter
        self.u_curr[x0, y0] = magnitude

        # 吸収境界用の減衰マスクを作成
        self.damping = self._create_damping_mask(grid_shape, damping_width)

    def _create_damping_mask(self, shape, width):
        nx, ny = shape
        damping = np.ones(shape)
        for i in range(width):
            factor = (1 - i / width) ** 2  # 境界に近づくほど強く減衰
            damping[i, :] *= factor         # 上端
            damping[-i - 1, :] *= factor    # 下端
            damping[:, i] *= factor         # 左端
            damping[:, -i - 1] *= factor    # 右端
        return damping

    def laplacian(self, u):
        return (
            -4 * u
            + np.roll(u, 1, axis=0)
            + np.roll(u, -1, axis=0)
            + np.roll(u, 1, axis=1)
            + np.roll(u, -1, axis=1)
        ) / (self.dx ** 2)

    def step(self):
        c = np.sqrt(self.mu / self.rho)
        u_next = (
            2 * self.u_curr - self.u_prev
            + (c ** 2) * (self.dt ** 2) * self.laplacian(self.u_curr)
        )

        # 境界条件を固定せず、吸収境界で波を減衰
        u_next *= self.damping

        self.u_max = np.maximum(self.u_max, np.abs(u_next))
        self.u_prev = self.u_curr
        self.u_curr = u_next

    def run(self, steps=10000):
        for _ in range(steps):
            self.step()
        return self.u_max