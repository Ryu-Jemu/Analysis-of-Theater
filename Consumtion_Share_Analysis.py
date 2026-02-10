from __future__ import annotations

from pathlib import Path
import yaml
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


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

    out_name = cfg.get("outputs", {}).get("consumption_share_correlation", "consumption_share_correlation.png")

    data_extended = {
        "지역": ["서울", "경기", "인천", "강원", "충청/대전/세종", "경상/대구/부산/울산", "전라/광주", "제주"],
        "민간소비지출액_2020": [2295, 1867, 1813, 1774, 1758, 1824, 1788, 1899],
        "점유율_2020": [23.1, 27.1, 5.3, 2.3, 10.2, 22.6, 8.4, 1.2],
        "민간소비지출액_2021": [2455, 1996, 1898, 1863, 1937, 1944, 1859, 1997],
        "점유율_2021": [23.8, 28.0, 4.9, 2.2, 10.1, 21.7, 8.4, 1.1],
        "민간소비지출액_2022": [2662, 2181, 2113, 2024, 2107, 2106, 2020, 2227],
        "점유율_2022": [25.3, 25.6, 5.1, 2.5, 10.0, 21.8, 8.4, 1.2],
    }

    plt.rcParams["axes.unicode_minus"] = False

    df = pd.DataFrame(data_extended)
    years = [2020, 2021, 2022]

    def calculate_correlation(year: int) -> tuple[float, float]:
        c_col = f"민간소비지출액_{year}"
        s_col = f"점유율_{year}"
        return pearsonr(df[c_col], df[s_col])

    # 콘솔 출력
    for y in years:
        corr, p = calculate_correlation(y)
        print(f"{y}년: 상관계수 = {corr:.3f}, p-value = {p:.3f}")

    # 시각화 저장
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, y in enumerate(years):
        c_col = f"민간소비지출액_{y}"
        s_col = f"점유율_{y}"
        axes[i].scatter(df[c_col], df[s_col])
        axes[i].set_title(f"{y}")
        axes[i].set_xlabel("Private Consumption Expenditure")
        axes[i].set_ylabel("Share (%)")

    plt.tight_layout()
    plt.savefig(out_dir / out_name, dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
