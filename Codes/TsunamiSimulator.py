import numpy as np
import os
import matplotlib.pyplot as plt

class TsunamiSimulatorVariableRho:
    def __init__(
        self, wave_source, wave_height, grid_shape, spread_map,
        dx=1.0, dt=0.1, mu=1.0, damping_width=1, save_frames=False
    ):
        self.grid_shape = grid_shape
        self.nx, self.ny = grid_shape
        self.dx = dx
        self.dt = dt
        self.mu = mu
        self.save_frames = save_frames

        # パディング付きの形状
        padded_shape = (self.nx + 2, self.ny + 2)

        self.u_prev = np.zeros(padded_shape)
        self.u_curr = np.zeros(padded_shape)
        self.u_max = np.zeros(padded_shape)

        # 波の伝わりやすさ（小さい＝遅い、大きい＝速い）
        self.spread = np.pad(spread_map, pad_width=1, mode='edge')

        # 発生源（津波震源）
        x0, y0 = wave_source
        self.u_curr[x0 + 1, y0 + 1] = wave_height

        # 境界減衰
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
        # 津波の波速（spread_map で変動）
        c = np.sqrt(self.mu / self.spread)

        lap = self.laplacian(self.u_curr)

        u_next = (
            2 * self.u_curr - self.u_prev
            + (c ** 2) * (self.dt ** 2) * lap
        )

        # 境界の波を弱める
        u_next *= self.damping

        # 最大波高の記録
        self.u_max = np.maximum(self.u_max, np.abs(u_next))

        self.u_prev = self.u_curr
        self.u_curr = u_next

    def save_frame(self, step, output_dir="frames"):
        os.makedirs(output_dir, exist_ok=True)
        trimmed_u = self.u_curr[1:-1, 1:-1]

        plt.figure(figsize=(6, 5))
        plt.imshow(trimmed_u, cmap="Blues", vmin=0, vmax=np.max(trimmed_u))
        plt.colorbar(label="Water Level (m)")
        plt.title(f"Tsunami Step {step}")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/frame_{step:05d}.png")
        plt.close()

    def run(self, steps=200, save_interval=10, output_dir="frames"):
        for step in range(steps):
            self.step()
            if self.save_frames and step % save_interval == 0:
                self.save_frame(step, output_dir)
        return self.u_max[1:-1, 1:-1]



### 動画作成（地震コードと同じ）
def make_video_from_frames(frame_dir="frames", output_path="tsunami.mp4", fps=10):
    import imageio
    files = sorted([os.path.join(frame_dir, f) for f in os.listdir(frame_dir) if f.endswith(".png")])
    images = [imageio.imread(f) for f in files]
    imageio.mimsave(output_path, images, fps=fps)



if __name__ == "__main__":
    import imageio

    # デバッグ用にシンプルなサイズ
    tile_width  = 50
    tile_height = 50

    # 波の伝わりやすさ（均一）
    spread = np.ones((tile_width, tile_height)) * 1.0

    sim = TsunamiSimulator(
        wave_source=(25, 25),   # 津波発生地点（中央）
        wave_height=5.0,        # 初期波高
        grid_shape=(tile_width, tile_height),
        spread_map=spread,      # 波の伝わりやすさ
        mu=1.0,
        dt=0.3,
        save_frames=True
    )

    # フレーム出力先
    output_dir = "./tsunami_frames"

    # 200ステップ実行、10ステップごとに画像保存
    sim.run(steps=200, save_interval=10, output_dir=output_dir)

    # 動画生成
    make_video_from_frames(
        frame_dir=output_dir,
        output_path="./tsunami_simulation.mp4",
        fps=10
    )
