# 次回TODO: プレイヤーの建物アンロック状況、建物等画像の用意

import numpy as np
import os
import matplotlib.pyplot as plt

class TsunamiSimulatorVariableRho:
    def __init__(self, epicenter, magnitude, grid_shape, rho_map, dx=1.0, dt=0.1, mu=1.0, damping_width=1, save_frames=False):
        self.grid_shape = grid_shape
        self.nx, self.ny = grid_shape
        self.dx = dx
        self.dt = dt
        self.mu = mu
        self.save_frames = save_frames

        # 1マス拡張した形状
        padded_shape = (self.nx + 2, self.ny + 2)

        self.u_prev = np.zeros(padded_shape)
        self.u_curr = np.zeros(padded_shape)
        self.u_max = np.zeros(padded_shape)

        # 密度マップも1マス拡張
        self.rho = np.pad(rho_map, pad_width=1, mode='edge')

        # 震源の位置を1ずらす（パディングを考慮）
        x0, y0 = epicenter
        self.u_curr[x0 + 1, y0 + 1] = magnitude

        # 減衰マスク
        self.damping = self._create_damping_mask(padded_shape, damping_width)

    def _create_damping_mask(self, shape, width):
        nx, ny = shape
        damping = np.ones(shape)
        for i in range(width):
            factor = (1 - i / width) ** 2
            damping[i, :] *= factor
            damping[-i - 1, :] *= factor
            damping[:, i] *= factor
            damping[:, -i - 1] *= factor
        return damping

    def laplacian(self, u):
        lap = np.zeros_like(u)
        lap[1:-1, 1:-1] = (
            -4 * u[1:-1, 1:-1]
            + u[0:-2, 1:-1]
            + u[2:, 1:-1]
            + u[1:-1, 0:-2]
            + u[1:-1, 2:]
        ) / (self.dx ** 2)
        return lap

    def step(self):
        c = np.sqrt(self.mu / self.rho)
        lap = self.laplacian(self.u_curr)
        u_next = (
            2 * self.u_curr - self.u_prev
            + (c ** 2) * (self.dt ** 2) * lap
        )
        u_next *= self.damping

        self.u_max = np.maximum(self.u_max, np.abs(u_next))
        self.u_prev = self.u_curr
        self.u_curr = u_next

    def save_frame(self, step, output_dir="frames"):
        """内部領域だけを描画・保存"""
        os.makedirs(output_dir, exist_ok=True)
        trimmed_u = self.u_curr[1:-1, 1:-1]
        plt.figure(figsize=(6, 5))
        plt.imshow(trimmed_u, cmap="seismic", vmin=-self.u_curr.max(), vmax=self.u_curr.max())
        plt.colorbar(label="Displacement")
        plt.title(f"Step {step}")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/frame_{step:05d}.png")
        plt.close()

    def run(self, steps=200, save_interval=10, output_dir="frames"):
        for step in range(steps):
            self.step()
            if self.save_frames and step % save_interval == 0:
                self.save_frame(step, output_dir=output_dir)
        # 内部領域だけ返す
        return self.u_max[1:-1, 1:-1]



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
    
    sim = TsunamiSimulatorVariableRho(
            epicenter=(2, 5), #震源​
            magnitude=10, #地震の規模​
            grid_shape= (tile_width, tile_height),
            rho_map=np.ones((tile_width, tile_height)), #地盤密度を持つ配列​
            mu=0.5, #弾性係数​
            dt=0.3,
            save_frames= True
        )

    sim.run(steps=200, save_interval=10, output_dir="../Debug_folder/frames")
    make_video_from_frames("../Debug_folder/frames", "../Debug_folder/quake_simulation.mp4", fps=10)