"""네이버 검색 API(블로그) 결과의 제목/요약(description)을 이용해 키워드 빈도 분석 및 워드클라우드를 생성합니다.

- 데이터 수집은 '공식 API'를 사용합니다.
- API 키는 config.yaml 또는 환경변수로 주입합니다(코드에 직접 하드코딩 금지).

출력:
- outputs/naver_keywords.csv
- outputs/naver_wordcloud.png
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import requests
import yaml
from dotenv import load_dotenv
from matplotlib import font_manager
from wordcloud import WordCloud


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_DIR_DEFAULT = ROOT / "outputs"
load_dotenv(ROOT / ".env")


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_env_or_config(cfg: dict, key: str, env_key: str) -> str:
    value = os.getenv(env_key)
    if value:
        return value
    # dotted key 지원: naver_api.client_id
    cur = cfg
    for part in key.split("."):
        cur = cur.get(part, {})
    if isinstance(cur, str) and cur and not cur.startswith("YOUR_"):
        return cur
    return ""


def extract_tokens(text: str) -> list[str]:
    try:
        from konlpy.tag import Okt

        return Okt().nouns(text)
    except Exception:
        # JVM/KoNLPy 미설치 환경을 위한 간단한 폴백 토큰화
        return re.findall(r"[가-힣A-Za-z0-9]{2,}", text)


def resolve_korean_font_path() -> str | None:
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

    for f in font_manager.fontManager.ttflist:
        name = (f.name or "").lower()
        if any(k in name for k in ["nanum", "gothic", "malgun", "noto sans cjk kr", "applegothic"]):
            if f.fname and Path(f.fname).exists():
                return f.fname
    return None


def main() -> None:
    cfg = load_config()

    out_dir = Path(cfg.get("paths", {}).get("output_dir", str(OUTPUT_DIR_DEFAULT)))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    client_id = get_env_or_config(cfg, "naver_api.client_id", "NAVER_CLIENT_ID")
    client_secret = get_env_or_config(cfg, "naver_api.client_secret", "NAVER_CLIENT_SECRET")
    url = cfg.get("naver_api", {}).get("blog_search_url", "https://openapi.naver.com/v1/search/blog.json")

    if not client_id or not client_secret:
        raise RuntimeError(
            "NAVER API 키가 필요합니다. config.yaml의 naver_api.client_id/client_secret 또는 "
            "환경변수 NAVER_CLIENT_ID/NAVER_CLIENT_SECRET을 설정하세요."
        )

    query = cfg.get("naver_api", {}).get("query", "메가박스")
    params = {
        "query": query,
        "display": int(cfg.get("naver_api", {}).get("display", 100)),
        "start": int(cfg.get("naver_api", {}).get("start", 1)),
        "sort": cfg.get("naver_api", {}).get("sort", "sim"),
    }
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    text_data: list[str] = []
    for item in data.get("items", []):
        text_data.append(item.get("title", ""))
        text_data.append(item.get("description", ""))

    text = " ".join(text_data)

    # 형태소 분석(명사 추출). 실패 시 정규식 기반 폴백 사용.
    tokens = extract_tokens(text)

    stopwords = {
        "CGV", "롯데시네마", "메가박스", "영화", "상영관", "극장", "좌석",
        "예매", "상영", "시간표", "영화관", "고객센터", "블로그", "후기", "포스팅",
        "링크", "사진", "공유", "작성", "추천", "조회", "댓글", "좋아요", "대해",
        "은", "는", "이", "가", "을", "를", "의", "와", "과", "도", "에", "에서",
        "보다", "으로", "또는", "그리고", "해서", "그러나", "너무", "정말", "많이",
        "아주", "그냥", "그래서", "이제", "다시", "이렇게", "저렇게",
        "!", "?", ".", ",", "/", "@", "#", "%",
    }

    filtered = [t for t in tokens if t not in stopwords and len(t) > 1]
    counts = Counter(filtered)

    # CSV 저장
    csv_path = out_dir / cfg.get("outputs", {}).get("text_keywords_csv", "naver_keywords.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count"])
        writer.writerows(counts.most_common())

    # 워드클라우드 이미지 저장
    plt.rcParams["axes.unicode_minus"] = False
    font_path = resolve_korean_font_path()
    if not font_path:
        raise RuntimeError(
            "한글 폰트를 찾지 못했습니다. KOREAN_FONT_PATH를 설정하거나 "
            "NanumGothic/AppleGothic 계열 폰트를 설치하세요."
        )
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_path).get_name()
    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=1000,
        height=700,
        max_words=80,
    ).generate_from_frequencies(counts)

    img_path = out_dir / cfg.get("outputs", {}).get("text_wordcloud", "naver_wordcloud.png")
    plt.figure(figsize=(10, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(img_path, dpi=200)
    plt.close()

    print(f"Saved: {csv_path}")
    print(f"Saved: {img_path}")


if __name__ == "__main__":
    main()
