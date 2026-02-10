from __future__ import annotations

import base64
import csv
import html
import mimetypes
import os
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List

import yaml
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
load_dotenv(ROOT / ".env")


@dataclass
class StepResult:
    name: str
    status: str  # success | failed | skipped
    message: str
    artifacts: List[Path]


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _abs_output_dir(cfg: dict) -> Path:
    out_dir = Path(cfg.get("paths", {}).get("output_dir", "outputs"))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _configured_path(out_dir: Path, cfg: dict, key: str, default_name: str) -> Path:
    name = cfg.get("outputs", {}).get(key, default_name)
    p = Path(name)
    return p if p.is_absolute() else out_dir / p


def _known_artifact_paths(out_dir: Path, cfg: dict) -> list[Path]:
    return [
        _configured_path(out_dir, cfg, "map_theaters_and_stations", "map_theaters_stations.html"),
        _configured_path(out_dir, cfg, "map_spot", "map_spot_theaters_malls.html"),
        _configured_path(out_dir, cfg, "movie_releases_plot", "movie_releases_by_year.png"),
        _configured_path(out_dir, cfg, "movie_audience_plot", "movie_audience_by_year.png"),
        _configured_path(out_dir, cfg, "movie_sales_plot", "movie_sales_by_year.png"),
        _configured_path(out_dir, cfg, "plot_3d_trendlines", "theater_3d_trendlines.png"),
        _configured_path(out_dir, cfg, "consumption_share_correlation", "consumption_share_correlation.png"),
        _configured_path(out_dir, cfg, "text_keywords_csv", "naver_keywords.csv"),
        _configured_path(out_dir, cfg, "text_wordcloud", "naver_wordcloud.png"),
        _configured_path(out_dir, cfg, "report_md", "report.md"),
        out_dir / "dashboard.html",
    ]


def _remove_files(paths: list[Path], preserve: set[str] | None = None) -> int:
    preserve = preserve or set()
    removed = 0
    seen: set[str] = set()

    for path in paths:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)

        if path.name in preserve:
            continue
        if path.exists() and path.is_file():
            path.unlink()
            removed += 1

    return removed


def _prepare_outputs_for_fresh_run(out_dir: Path, cfg: dict) -> None:
    stale = _known_artifact_paths(out_dir, cfg)
    _remove_files(stale, preserve={".gitkeep"})


def _run_step(name: str, fn: Callable[[], None], expected: List[Path]) -> StepResult:
    try:
        fn()
        produced = [p for p in expected if p.exists()]
        missing = [p.name for p in expected if not p.exists()]
        if missing:
            return StepResult(
                name=name,
                status="failed",
                message=f"실행은 완료됐지만 예상 산출물 일부가 없습니다: {', '.join(missing)}",
                artifacts=produced,
            )
        return StepResult(name=name, status="success", message="OK", artifacts=produced)
    except Exception as e:
        return StepResult(
            name=name,
            status="failed",
            message=f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=5)}",
            artifacts=[p for p in expected if p.exists()],
        )


def _step_skipped(name: str, reason: str) -> StepResult:
    return StepResult(name=name, status="skipped", message=reason, artifacts=[])


def _build_run_summary(results: List[StepResult], started_at: datetime, finished_at: datetime, out_dir: Path) -> dict:
    generated_files: List[str] = []
    skipped_steps: List[str] = []
    failed_steps: List[str] = []

    seen: set[str] = set()
    steps: list[dict] = []

    for r in results:
        artifact_names: list[str] = []
        for a in r.artifacts:
            if not a.exists():
                continue
            rel = a.name if a.parent == out_dir else str(a)
            artifact_names.append(rel)
            if rel not in seen:
                seen.add(rel)
                generated_files.append(rel)

        if r.status == "skipped":
            skipped_steps.append(r.name)
        if r.status == "failed":
            failed_steps.append(r.name)

        steps.append(
            {
                "name": r.name,
                "status": r.status,
                "message": r.message.splitlines()[0],
                "artifacts": artifact_names,
            }
        )

    return {
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 2),
        "steps": steps,
        "generated_files": generated_files,
        "skipped_steps": skipped_steps,
        "failed_steps": failed_steps,
    }


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _read_csv_preview(csv_path: Path, max_rows: int = 10) -> tuple[list[str], list[list[str]]]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        rows: list[list[str]] = []
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)
        return headers, rows


def build_dashboard(outputs_dir: str, config: dict, run_summary: dict) -> str:
    out_dir = Path(outputs_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    discovered = {
        "movie_releases": _configured_path(out_dir, config, "movie_releases_plot", "movie_releases_by_year.png"),
        "movie_audience": _configured_path(out_dir, config, "movie_audience_plot", "movie_audience_by_year.png"),
        "movie_sales": _configured_path(out_dir, config, "movie_sales_plot", "movie_sales_by_year.png"),
        "trend_3d": _configured_path(out_dir, config, "plot_3d_trendlines", "theater_3d_trendlines.png"),
        "consumption": _configured_path(
            out_dir, config, "consumption_share_correlation", "consumption_share_correlation.png"
        ),
        "wordcloud": _configured_path(out_dir, config, "text_wordcloud", "naver_wordcloud.png"),
        "map_theaters": _configured_path(out_dir, config, "map_theaters_and_stations", "map_theaters_stations.html"),
        "map_spot": _configured_path(out_dir, config, "map_spot", "map_spot_theaters_malls.html"),
        "keywords_csv": _configured_path(out_dir, config, "text_keywords_csv", "naver_keywords.csv"),
    }

    status_label = {"success": "성공", "failed": "실패", "skipped": "스킵"}

    def image_card(title: str, filename: str, path: Path) -> str:
        if not path.exists():
            return (
                "<article class='card missing-card'>"
                f"<h3>{html.escape(title)}</h3>"
                f"<p class='missing'>미생성(스킵/실패): {html.escape(filename)}</p>"
                "</article>"
            )

        data_uri = _data_uri(path)
        return (
            "<article class='card'>"
            f"<h3>{html.escape(title)}</h3>"
            f"<a href='{data_uri}' target='_blank' rel='noopener noreferrer'>"
            f"<img src='{data_uri}' alt='{html.escape(title)}' loading='lazy'/>"
            "</a>"
            f"<p class='meta'>인라인 임베드 ({html.escape(path.name)})</p>"
            "</article>"
        )

    def map_card(title: str, filename: str, path: Path) -> str:
        if not path.exists():
            return (
                "<article class='card missing-card'>"
                f"<h3>{html.escape(title)}</h3>"
                f"<p class='missing'>미생성(스킵/실패): {html.escape(filename)}</p>"
                "</article>"
            )

        srcdoc = html.escape(path.read_text(encoding="utf-8", errors="ignore"), quote=True)
        return (
            "<article class='card map-card'>"
            f"<h3>{html.escape(title)}</h3>"
            f"<iframe title='{html.escape(title)}' loading='lazy' srcdoc=\"{srcdoc}\"></iframe>"
            f"<p class='meta'>인라인 임베드 ({html.escape(path.name)})</p>"
            "</article>"
        )

    generated_html = "".join(
        f"<li><code>{html.escape(name)}</code></li>" for name in run_summary.get("generated_files", [])
    ) or "<li>생성된 파일이 없습니다.</li>"

    skipped_html = "".join(
        f"<li>{html.escape(name)}</li>" for name in run_summary.get("skipped_steps", [])
    ) or "<li>스킵된 단계가 없습니다.</li>"

    failed_html = "".join(
        f"<li>{html.escape(name)}</li>" for name in run_summary.get("failed_steps", [])
    ) or "<li>실패 단계가 없습니다.</li>"

    step_rows: list[str] = []
    for step in run_summary.get("steps", []):
        s = html.escape(step.get("status", ""))
        step_rows.append(
            "<tr>"
            f"<td>{html.escape(step.get('name', '-'))}</td>"
            f"<td class='status {s}'>{html.escape(status_label.get(step.get('status', ''), step.get('status', '-')))}</td>"
            f"<td>{html.escape(step.get('message', '-'))}</td>"
            "</tr>"
        )

    csv_preview_html = "<p class='missing'>미생성(스킵/실패): naver_keywords.csv</p>"
    csv_path = discovered["keywords_csv"]
    if csv_path.exists():
        try:
            headers, rows = _read_csv_preview(csv_path, max_rows=10)
            head_html = "".join(f"<th>{html.escape(col)}</th>" for col in headers)
            row_html = "".join(
                "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
            )
            csv_preview_html = (
                "<h3>키워드 CSV 미리보기 (상위 10행)</h3>"
                "<div class='table-wrap'>"
                "<table>"
                f"<thead><tr>{head_html}</tr></thead>"
                f"<tbody>{row_html}</tbody>"
                "</table>"
                "</div>"
            )
        except Exception as e:
            csv_preview_html = f"<p class='missing'>CSV 미리보기 실패: {html.escape(type(e).__name__ + ': ' + str(e))}</p>"

    dashboard_html = f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Analysis-of-Theater Dashboard</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --line: #d6dde8;
      --ok: #0f766e;
      --fail: #b91c1c;
      --skip: #9a3412;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .container {{ width: min(1600px, 96vw); margin: 0 auto; padding: 24px 0 60px; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    h2 {{ margin: 0 0 14px; font-size: 22px; }}
    h3 {{ margin: 0 0 10px; font-size: 17px; }}
    .meta {{ color: var(--muted); margin: 10px 0 0; font-size: 14px; }}
    .section {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px; margin-top: 16px; }}
    .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }}
    .card {{ border: 1px solid var(--line); border-radius: 10px; padding: 12px; background: #fff; }}
    .missing {{ color: var(--fail); font-weight: 600; }}
    .missing-card {{ background: #fff9f9; }}
    img {{ width: 100%; border-radius: 8px; border: 1px solid var(--line); display: block; }}
    iframe {{ width: 100%; min-height: 900px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .map-card {{ grid-column: 1 / -1; }}
    code {{ background: #edf2ff; padding: 2px 6px; border-radius: 6px; }}
    ul {{ margin: 0; padding-left: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border: 1px solid var(--line); padding: 8px; text-align: left; }}
    th {{ background: #f2f5fb; }}
    .table-wrap {{ overflow-x: auto; }}
    .status {{ font-weight: 700; }}
    .status.success {{ color: var(--ok); }}
    .status.failed {{ color: var(--fail); }}
    .status.skipped {{ color: var(--skip); }}
    @media (max-width: 900px) {{
      .summary-grid {{ grid-template-columns: 1fr; }}
      iframe {{ min-height: 900px; }}
    }}
  </style>
</head>
<body>
  <main class=\"container\">
    <header class=\"section\">
      <h1>Analysis-of-Theater 통합 대시보드</h1>
      <p class=\"meta\">단일 파일 모드: 실행 직후 PNG/HTML/CSV 중간 산출물은 자동 삭제됩니다.</p>
      <div class=\"summary-grid\" style=\"margin-top:14px\">
        <section>
          <h3>실행 요약</h3>
          <ul>
            <li>시작: {html.escape(str(run_summary.get('started_at', '-')))}</li>
            <li>종료: {html.escape(str(run_summary.get('finished_at', '-')))}</li>
            <li>소요 시간: {html.escape(str(run_summary.get('duration_seconds', '-')))}초</li>
          </ul>
        </section>
        <section>
          <h3>스킵된 단계</h3>
          <ul>{skipped_html}</ul>
          <h3 style=\"margin-top:14px\">실패 단계</h3>
          <ul>{failed_html}</ul>
        </section>
      </div>
      <section style=\"margin-top:14px\">
        <h3>중간 생성 파일(생성 후 정리됨)</h3>
        <ul>{generated_html}</ul>
      </section>
      <section style=\"margin-top:14px\">
        <h3>단계별 결과</h3>
        <div class=\"table-wrap\">
          <table>
            <thead>
              <tr><th>단계</th><th>상태</th><th>메시지</th></tr>
            </thead>
            <tbody>
              {''.join(step_rows)}
            </tbody>
          </table>
        </div>
      </section>
    </header>

    <section class=\"section\">
      <h2>A. 영화 지표</h2>
      <div class=\"cards\">
        {image_card('연도별 개봉편수', 'movie_releases_by_year.png', discovered['movie_releases'])}
        {image_card('연도별 관객수', 'movie_audience_by_year.png', discovered['movie_audience'])}
        {image_card('연도별 매출', 'movie_sales_by_year.png', discovered['movie_sales'])}
      </div>
    </section>

    <section class=\"section\">
      <h2>B. 지도</h2>
      <div class=\"cards\">
        {map_card('극장 + 지하철역 지도', 'map_theaters_stations.html', discovered['map_theaters'])}
        {map_card('극장 + 쇼핑몰 지도', 'map_spot_theaters_malls.html', discovered['map_spot'])}
      </div>
    </section>

    <section class=\"section\">
      <h2>C. 기타 분석</h2>
      <div class=\"cards\">
        {image_card('3D 관계 분석', 'theater_3d_trendlines.png', discovered['trend_3d'])}
        {image_card('소비지출-점유율 상관', 'consumption_share_correlation.png', discovered['consumption'])}
        {image_card('네이버 워드클라우드', 'naver_wordcloud.png', discovered['wordcloud'])}
      </div>
    </section>

    <section class=\"section\">
      <h2>D. 키워드 데이터</h2>
      {csv_preview_html}
    </section>
  </main>
</body>
</html>
"""

    dashboard_path = out_dir / "dashboard.html"
    dashboard_path.write_text(dashboard_html, encoding="utf-8")
    return str(dashboard_path)


def main() -> int:
    started_at = datetime.now()
    cfg = load_config()
    out_dir = _abs_output_dir(cfg)

    _prepare_outputs_for_fresh_run(out_dir, cfg)

    expected_files = {
        "지도(극장+역)": [_configured_path(out_dir, cfg, "map_theaters_and_stations", "map_theaters_stations.html")],
        "지도(극장+쇼핑몰 예시)": [_configured_path(out_dir, cfg, "map_spot", "map_spot_theaters_malls.html")],
        "영화 지표 시각화": [
            _configured_path(out_dir, cfg, "movie_releases_plot", "movie_releases_by_year.png"),
            _configured_path(out_dir, cfg, "movie_audience_plot", "movie_audience_by_year.png"),
            _configured_path(out_dir, cfg, "movie_sales_plot", "movie_sales_by_year.png"),
        ],
        "3D 분석": [_configured_path(out_dir, cfg, "plot_3d_trendlines", "theater_3d_trendlines.png")],
        "소비지출-점유율 상관": [
            _configured_path(out_dir, cfg, "consumption_share_correlation", "consumption_share_correlation.png")
        ],
        "텍스트 키워드 분석": [
            _configured_path(out_dir, cfg, "text_keywords_csv", "naver_keywords.csv"),
            _configured_path(out_dir, cfg, "text_wordcloud", "naver_wordcloud.png"),
        ],
    }

    results: list[StepResult] = []

    if cfg.get("pipeline", {}).get("run_maps", True):
        try:
            import Integrate_stations

            results.append(_run_step("지도(극장+역)", Integrate_stations.main, expected_files["지도(극장+역)"]))
        except Exception as e:
            results.append(StepResult("지도(극장+역)", "failed", f"ImportError/InitError: {e}", []))

        try:
            import Spot

            results.append(_run_step("지도(극장+쇼핑몰 예시)", Spot.main, expected_files["지도(극장+쇼핑몰 예시)"]))
        except Exception as e:
            results.append(StepResult("지도(극장+쇼핑몰 예시)", "failed", f"ImportError/InitError: {e}", []))
    else:
        results.append(_step_skipped("지도(극장+역)", "config.pipeline.run_maps=false"))
        results.append(_step_skipped("지도(극장+쇼핑몰 예시)", "config.pipeline.run_maps=false"))

    if cfg.get("pipeline", {}).get("run_movie_visualization", True):
        try:
            import Visualization

            results.append(_run_step("영화 지표 시각화", Visualization.main, expected_files["영화 지표 시각화"]))
        except Exception as e:
            results.append(StepResult("영화 지표 시각화", "failed", f"ImportError/InitError: {e}", []))
    else:
        results.append(_step_skipped("영화 지표 시각화", "config.pipeline.run_movie_visualization=false"))

    if cfg.get("pipeline", {}).get("run_3d_analysis", True):
        try:
            import Graph3D

            results.append(_run_step("3D 분석", Graph3D.main, expected_files["3D 분석"]))
        except Exception as e:
            results.append(StepResult("3D 분석", "failed", f"ImportError/InitError: {e}", []))
    else:
        results.append(_step_skipped("3D 분석", "config.pipeline.run_3d_analysis=false"))

    if cfg.get("pipeline", {}).get("run_consumption_share_analysis", True):
        try:
            import Consumtion_Share_Analysis

            results.append(
                _run_step("소비지출-점유율 상관", Consumtion_Share_Analysis.main, expected_files["소비지출-점유율 상관"])
            )
        except Exception as e:
            results.append(StepResult("소비지출-점유율 상관", "failed", f"ImportError/InitError: {e}", []))
    else:
        results.append(_step_skipped("소비지출-점유율 상관", "config.pipeline.run_consumption_share_analysis=false"))

    if cfg.get("pipeline", {}).get("run_text_analysis", True):
        try:
            import text_analysis

            results.append(_run_step("텍스트 키워드 분석", text_analysis.main, expected_files["텍스트 키워드 분석"]))
        except Exception as e:
            results.append(StepResult("텍스트 키워드 분석", "failed", f"ImportError/InitError: {e}", []))
    else:
        results.append(_step_skipped("텍스트 키워드 분석", "config.pipeline.run_text_analysis=false"))

    finished_at = datetime.now()
    run_summary = _build_run_summary(results, started_at, finished_at, out_dir)

    dashboard_path = out_dir / "dashboard.html"
    try:
        dashboard_path_str = build_dashboard(str(out_dir), cfg, run_summary)
        dashboard_path = Path(dashboard_path_str)
        if not dashboard_path.is_absolute():
            dashboard_path = (ROOT / dashboard_path).resolve()
        print(f"[OK] Dashboard generated: {dashboard_path}")
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        fallback = (
            "<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>Dashboard Error</title></head><body>"
            "<h1>대시보드 생성 실패</h1>"
            f"<p>{html.escape(err)}</p>"
            "</body></html>"
        )
        dashboard_path.write_text(fallback, encoding="utf-8")
        print(f"[WARN] Dashboard generation failed: {err}")

    cleanup_targets = _known_artifact_paths(out_dir, cfg)
    removed = _remove_files(cleanup_targets, preserve={"dashboard.html", ".gitkeep"})
    print(f"[OK] Temporary artifacts cleaned: {removed} files removed")

    return 0 if all(r.status != "failed" for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
