from __future__ import annotations

import json
import os
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import yaml


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class StepResult:
    name: str
    ok: bool
    message: str
    artifacts: List[Path]


def _abs_output_dir(cfg: dict) -> Path:
    out_dir = Path(cfg.get("paths", {}).get("output_dir", "outputs"))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _run_step(name: str, fn: Callable[[], None], expected: List[Path]) -> StepResult:
    try:
        fn()
        produced = [p for p in expected if p.exists()]
        missing = [p.name for p in expected if not p.exists()]
        if missing:
            return StepResult(
                name=name,
                ok=False,
                message=f"실행은 완료됐지만 예상 산출물 일부가 없습니다: {', '.join(missing)}",
                artifacts=produced,
            )
        return StepResult(name=name, ok=True, message="OK", artifacts=produced)
    except Exception as e:
        return StepResult(
            name=name,
            ok=False,
            message=f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=5)}",
            artifacts=[p for p in expected if p.exists()],
        )


def generate_report(cfg: dict, results: List[StepResult]) -> Path:
    out_dir = _abs_output_dir(cfg)
    report_name = cfg.get("outputs", {}).get("report_md", "report.md")
    report_path = out_dir / report_name

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: List[str] = []
    lines.append(f"# Analysis-of-Theater 실행 리포트")
    lines.append("")
    lines.append(f"- 생성 시각: {now}")
    lines.append(f"- 출력 폴더: `{out_dir.relative_to(ROOT)}`")
    lines.append("")

    # 설정 요약 (민감 정보 제외)
    naver_set = bool(os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET")) or (
        cfg.get("naver_api", {}).get("client_id", "").strip()
        and not str(cfg.get("naver_api", {}).get("client_id", "")).startswith("YOUR_")
    )
    kakao_set = bool(os.getenv("KAKAO_REST_API_KEY")) or (
        cfg.get("kakao_api", {}).get("rest_api_key", "").strip()
        and not str(cfg.get("kakao_api", {}).get("rest_api_key", "")).startswith("YOUR_")
    )

    lines.append("## 설정 상태")
    lines.append(f"- Kakao API 키 설정: {'✅' if kakao_set else '❌'} (지도가 필요한 단계)")
    lines.append(f"- Naver API 키 설정: {'✅' if naver_set else '❌'} (텍스트 분석 단계)")
    lines.append("")

    lines.append("## 실행 결과 요약")
    for r in results:
        lines.append(f"- **{r.name}**: {'✅ 성공' if r.ok else '❌ 실패/스킵'} — {r.message.splitlines()[0]}")
    lines.append("")

    lines.append("## 산출물")
    # 중복 제거
    all_artifacts: List[Path] = []
    seen = set()
    for r in results:
        for a in r.artifacts:
            if a.exists() and a.name not in seen:
                all_artifacts.append(a)
                seen.add(a.name)

    if not all_artifacts:
        lines.append("- (산출물 없음)")
    else:
        for a in all_artifacts:
            rel = a.relative_to(out_dir)
            if a.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                lines.append(f"### {a.name}")
                lines.append(f"![]({rel.as_posix()})")
                lines.append("")
            else:
                lines.append(f"- [{a.name}]({rel.as_posix()})")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    cfg = load_config()
    out_dir = _abs_output_dir(cfg)

    outputs = cfg.get("outputs", {})
    expected_files = {
        "지도(극장+역)": [out_dir / outputs.get("map_theaters_and_stations", "map_theaters_stations.html")],
        "지도(극장+쇼핑몰 예시)": [out_dir / outputs.get("map_spot", "map_spot_theaters_malls.html")],
        "영화 지표 시각화": [
            out_dir / outputs.get("movie_releases_plot", "movie_releases_by_year.png"),
            out_dir / outputs.get("movie_audience_plot", "movie_audience_by_year.png"),
            out_dir / outputs.get("movie_sales_plot", "movie_sales_by_year.png"),
        ],
        "3D 분석": [out_dir / outputs.get("plot_3d_trendlines", "theater_3d_trendlines.png")],
        "소비지출-점유율 상관": [out_dir / outputs.get("consumption_share_correlation", "consumption_share_correlation.png")],
        "텍스트 키워드 분석": [
            out_dir / outputs.get("text_keywords_csv", "naver_keywords.csv"),
            out_dir / outputs.get("text_wordcloud", "naver_wordcloud.png"),
        ],
    }

    results: List[StepResult] = []

    # Lazy imports (의존성 누락 시에도 다른 단계는 최대한 진행)
    if cfg.get("pipeline", {}).get("run_maps", True):
        try:
            import Integrate_stations
            results.append(_run_step("지도(극장+역)", Integrate_stations.main, expected_files["지도(극장+역)"]))
        except Exception as e:
            results.append(StepResult("지도(극장+역)", False, f"ImportError/InitError: {e}", []))

        try:
            import Spot
            results.append(_run_step("지도(극장+쇼핑몰 예시)", Spot.main, expected_files["지도(극장+쇼핑몰 예시)"]))
        except Exception as e:
            results.append(StepResult("지도(극장+쇼핑몰 예시)", False, f"ImportError/InitError: {e}", []))

    if cfg.get("pipeline", {}).get("run_movie_visualization", True):
        try:
            import Visualization
            results.append(_run_step("영화 지표 시각화", Visualization.main, expected_files["영화 지표 시각화"]))
        except Exception as e:
            results.append(StepResult("영화 지표 시각화", False, f"ImportError/InitError: {e}", []))

    if cfg.get("pipeline", {}).get("run_3d_analysis", True):
        try:
            import Graph3D
            results.append(_run_step("3D 분석", Graph3D.main, expected_files["3D 분석"]))
        except Exception as e:
            results.append(StepResult("3D 분석", False, f"ImportError/InitError: {e}", []))

    if cfg.get("pipeline", {}).get("run_consumption_share_analysis", True):
        try:
            import Consumtion_Share_Analysis
            results.append(_run_step("소비지출-점유율 상관", Consumtion_Share_Analysis.main, expected_files["소비지출-점유율 상관"]))
        except Exception as e:
            results.append(StepResult("소비지출-점유율 상관", False, f"ImportError/InitError: {e}", []))

    if cfg.get("pipeline", {}).get("run_text_analysis", True):
        try:
            import text_analysis
            results.append(_run_step("텍스트 키워드 분석", text_analysis.main, expected_files["텍스트 키워드 분석"]))
        except Exception as e:
            results.append(StepResult("텍스트 키워드 분석", False, f"ImportError/InitError: {e}", []))

    report_path = generate_report(cfg, results)
    print(f"[OK] Report generated: {report_path}")

    # return non-zero if any step failed
    return 0 if all(r.ok for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
