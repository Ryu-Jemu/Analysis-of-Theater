from __future__ import annotations

import os
from pathlib import Path
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_korean_font_path() -> str | None:
    env_path = os.getenv("KOREAN_FONT_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    preferred_names = [
        "NanumGothic",
        "Nanum Gothic",
        "Apple SD Gothic Neo",
        "AppleGothic",
        "Malgun Gothic",
        "Noto Sans CJK KR",
        "Noto Sans KR",
    ]
    for name in preferred_names:
        try:
            path = font_manager.findfont(name, fallback_to_default=False)
            if path and Path(path).exists():
                return path
        except Exception:
            continue
    return None


def _apply_plot_font() -> None:
    plt.rcParams["axes.unicode_minus"] = False
    font_path = _resolve_korean_font_path()
    if font_path:
        font_name = font_manager.FontProperties(fname=font_path).get_name()
        plt.rcParams["font.family"] = font_name


def _plot_two_series(df: pd.DataFrame, x_col: str, y_col: str, cat_col: str, out_path: Path, title: str, ylabel: str) -> None:
    # 카테고리별로 분리(예: Korean vs Foreign)
    categories = list(df[cat_col].dropna().unique())

    plt.figure(figsize=(14, 8))
    for cat in categories:
        sub = df[df[cat_col] == cat].sort_values(x_col)
        plt.plot(sub[x_col], sub[y_col], marker="o", label=str(cat))

    plt.xticks(sorted(df[x_col].unique()), rotation=45)
    plt.grid(axis="x", linestyle="--")
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.legend(title="Category")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main() -> None:
    cfg = load_config()

    out_dir = Path(cfg.get("paths", {}).get("output_dir", "outputs"))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = cfg.get("outputs", {})
    releases_png = outputs.get("movie_releases_plot", "movie_releases_by_year.png")
    audience_png = outputs.get("movie_audience_plot", "movie_audience_by_year.png")
    sales_png = outputs.get("movie_sales_plot", "movie_sales_by_year.png")

    csv_name = cfg.get("paths", {}).get("movie_indicators_csv", "data_movie_indicators_by_year.csv")
    data = pd.read_csv(ROOT / csv_name, encoding="utf-8-sig")

    data["Year of 연도"] = data["Year of 연도"].astype(int)
    data["분류"] = data["분류"].replace({"한국영화": "Korean Films", "외국영화": "Foreign Films"})

    _apply_plot_font()

    _plot_two_series(
        data,
        x_col="Year of 연도",
        y_col="개봉편수",
        cat_col="분류",
        out_path=out_dir / releases_png,
        title="Number of Releases by Year (Korean vs Foreign Films)",
        ylabel="Number of Releases",
    )

    _plot_two_series(
        data,
        x_col="Year of 연도",
        y_col="관객수(만)",
        cat_col="분류",
        out_path=out_dir / audience_png,
        title="Audience (10k) by Year (Korean vs Foreign Films)",
        ylabel="Audience (10k)",
    )

        # CSV에 따라 매출 컬럼명이 다를 수 있어 fallback 처리
    sales_col = "매출액(억원)" if "매출액(억원)" in data.columns else ("매출액(억)" if "매출액(억)" in data.columns else "매출액")

    _plot_two_series(
        data,
        x_col="Year of 연도",
        y_col=sales_col,
        cat_col="분류",
        out_path=out_dir / sales_png,
        title="Sales by Year (Korean vs Foreign Films)",
        ylabel=sales_col,
    )


if __name__ == "__main__":
    main()
