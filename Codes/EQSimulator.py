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
    def __init__(self, epicenter, magnitude, grid_shape, rho_map, dx=1.0, dt=0.1, mu=1.0, damping_width= 1, save_frames = False):
        self.epicenter = epicenter
        self.magnitude = magnitude
        self.dx = dx
        self.dt = dt
        self.mu = mu
        self.rho = rho_map

        self.save_frames = save_frames

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

    # def laplacian(self, u):
    #     return (
    #         -4 * u
    #         + np.roll(u, 1, axis=0)
    #         + np.roll(u, -1, axis=0)
    #         + np.roll(u, 1, axis=1)
    #         + np.roll(u, -1, axis=1)
    #     ) / (self.dx ** 2)
    def laplacian(self, u):
        lap = np.zeros_like(u)
        lap[1:-1, 1:-1] = (
            -4 * u[1:-1, 1:-1]
            + u[0:-2, 1:-1]  # 上
            + u[2:, 1:-1]    # 下
            + u[1:-1, 0:-2]  # 左
            + u[1:-1, 2:]    # 右
        ) / (self.dx ** 2)
        return lap

    def step(self):
        c = np.sqrt(self.mu / self.rho)
        lap = self.laplacian(self.u_curr)
        u_next = (
            2 * self.u_curr - self.u_prev
            + (c ** 2) * (self.dt ** 2) * lap
        )

        # 吸収境界マスクで波を徐々に減衰させる
        u_next *= self.damping

        # ※ 境界はゼロにせず、「damping」だけで吸収させるのが吸収境界
        self.u_max = np.maximum(self.u_max, np.abs(u_next))
        self.u_prev = self.u_curr
        self.u_curr = u_next

    # def step(self):
    #     c = np.sqrt(self.mu / self.rho)
    #     u_next = (
    #         2 * self.u_curr - self.u_prev
    #         + (c ** 2) * (self.dt ** 2) * self.laplacian(self.u_curr)
    #     )

    #     # 境界条件を固定せず、吸収境界で波を減衰
    #     u_next *= self.damping

    #     self.u_max = np.maximum(self.u_max, np.abs(u_next))
    #     self.u_prev = self.u_curr
    #     self.u_curr = u_next

    def save_frame(self, step, output_dir="frames"):
        """現在の状態を画像として保存"""
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(6, 5))
        plt.imshow(self.u_curr, cmap="seismic", vmin=-self.magnitude, vmax=self.magnitude)
        plt.colorbar(label="Displacement")
        plt.title(f"Step {step}")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/frame_{step:05d}.png")
        plt.close()

    def run(self, steps=1000, save_interval=10, output_dir="frames"):

        for step in range(steps):
            self.step()
            if self.save_frames:
                if step % save_interval == 0:
                    self.save_frame(step, output_dir=output_dir)
        return self.u_max
    
    # def run(self, steps=10000):
    #     for _ in range(steps):
    #         self.step()
    #     return self.u_max


### デバッグ用

def make_video_from_frames(frame_dir="frames", output_path="simulation.mp4", fps=10):
    files = sorted([os.path.join(frame_dir, f) for f in os.listdir(frame_dir) if f.endswith(".png")])
    images = [imageio.imread(f) for f in files]
    imageio.mimsave(output_path, images, fps=fps)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import os
    import imageio
    from pathlib import Path
    import json

    file_path = Path("../Config") / f"map_config.json"
    # with open(f"map_stage{stage_num}.json", "r") as f:
    with open(file_path, "r", encoding="utf-8_sig") as f:
        map_data = json.load(f)
        tile_width = map_data["tile_width"] 
        tile_height = map_data["tile_width"] 
    
    sim = EQSimulatorVariableRho(
            epicenter=(2, 5), #震源​
            magnitude=10, #地震の規模​
            grid_shape= (tile_width, tile_height),
            rho_map=np.ones((tile_width, tile_height)), #地盤密度を持つ配列​
            mu=1.0, #弾性係数​
            dt=0.05,
            save_frames= True
        )

    sim.run(steps=500, save_interval=10, output_dir="../Debug_folder/frames")
    make_video_from_frames("../Debug_folder/frames", "../Debug_folder/quake_simulation.mp4", fps=10)