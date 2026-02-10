from __future__ import annotations

from pathlib import Path
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    cfg = load_config()

    out_dir = Path(cfg.get("paths", {}).get("output_dir", "outputs"))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    out_name = cfg.get("outputs", {}).get("plot_3d_trendlines", "theater_3d_trendlines.png")

    data = {
        "상영관": [20, 21, 18, 12, 12, 10, 10, 11, 14, 8, 9, 10, 8, 8, 8, 10, 8, 7, 11, 10],
        "좌석수": [3893, 4276, 3593, 2714, 2213, 2127, 1840, 2487, 3390, 1895, 1889, 1855, 1737, 1494, 1522, 1648, 1523, 1432, 2409, 2172],
        "연간관객수": [290, 257, 170, 125, 99, 96, 91, 86, 82, 78, 78, 78, 76, 72, 71, 70, 69, 67, 64, 64],
    }
    df = pd.DataFrame(data)

    plt.rcParams["axes.unicode_minus"] = False

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    X = df["상영관"].values.reshape(-1, 1)
    Y = df["좌석수"].values.reshape(-1, 1)
    Z = df["연간관객수"].values

    ax.scatter(X, Y, Z, s=50, label="Data Points")

    model1 = LinearRegression().fit(X, Z)
    Z_pred1 = model1.predict(X)
    ax.plot(X.flatten(), Y.flatten(), Z_pred1, label="Trend: Screens vs Audience")

    model2 = LinearRegression().fit(Y, Z)
    Z_pred2 = model2.predict(Y)
    ax.plot(X.flatten(), Y.flatten(), Z_pred2, label="Trend: Seats vs Audience")

    ax.set_title("3D Relationship: Screens / Seats / Annual Audience")
    ax.set_xlabel("Screens")
    ax.set_ylabel("Seats")
    ax.set_zlabel("Annual Audience (10k)")

    ax.legend()
    plt.tight_layout()
    plt.savefig(out_dir / out_name, dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
