import numpy as np

class DefineMagnitude:
    @staticmethod
    def define_magnitude(stage_data):
        """ステージデータからマグニチュードを定義"""
        mag_params = stage_data.get("magnitude_distribution", {})
        mean = mag_params.get("mean", 7.0)
        std = mag_params.get("std", 0.5)
        min_mag = mag_params.get("min", 6.0)
        max_mag = mag_params.get("max", 9.0)

        # 正規分布から乱数を生成し、範囲でクリップ
        magnitude = np.random.normal(loc=mean, scale=std)
        magnitude = np.clip(magnitude, min_mag, max_mag)

        return magnitude
    
def main():
    test_stage_data = {
        "magnitude_distribution":{
            "min" : 6.0,
            "max" : 9.0,
            "mean" : 7.5,
            "std" : 0.8
        }
    }
    for i in range(5):
        magnitude = DefineMagnitude.define_magnitude(stage_data=test_stage_data)
        print(f"試行 {i+1}: マグニチュード = {magnitude:.2f}")

if __name__ == "__main__":
    main()
