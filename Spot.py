"""상위 매출 극장(예시 주소)과 주요 쇼핑몰(예시 주소)을 카카오 로컬 API(주소→좌표)로 변환해 지도에 시각화합니다.

- API 키는 config.yaml 또는 환경변수로 주입합니다(코드에 직접 하드코딩 금지).
- 주소 목록(theaters/domestic_mall)은 예시 데이터이며, 필요 시 교체/확장하세요.

출력:
- outputs/map_spot_theaters_malls.html
"""

from __future__ import annotations

import os
from pathlib import Path

import folium
import requests
import yaml
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_DIR_DEFAULT = ROOT / "outputs"
load_dotenv(ROOT / ".env")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_kakao_key(cfg: dict) -> str:
    key = os.getenv("KAKAO_REST_API_KEY")
    if key:
        return key
    key = cfg.get("kakao_api", {}).get("rest_api_key", "")
    if key and not str(key).startswith("YOUR_"):
        return str(key)
    return ""


def get_coordinates_kakao(address: str, api_key: str, url: str) -> tuple[float, float] | None:
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if data.get("documents"):
        x = data["documents"][0].get("x")  # longitude
        y = data["documents"][0].get("y")  # latitude
        if x is not None and y is not None:
            return float(y), float(x)
    return None


def main() -> None:
    cfg = load_config()

    out_dir = Path(cfg.get("paths", {}).get("output_dir", str(OUTPUT_DIR_DEFAULT)))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    api_key = get_kakao_key(cfg)
    geocode_url = cfg.get("kakao_api", {}).get(
        "geocode_url", "https://dapi.kakao.com/v2/local/search/address.json"
    )
    if not api_key:
        raise RuntimeError(
            "KAKAO API 키가 필요합니다. config.yaml의 kakao_api.rest_api_key 또는 "
            "환경변수 KAKAO_REST_API_KEY를 설정하세요."
        )

    # 예시 주소(프로젝트 목적에 맞게 교체 가능)
    theaters = {
        "CGV": [
            "서울특별시 용산구 한강대로23길 55",
            "서울특별시 영등포구 경인로 846",
            "서울특별시 성동구 왕십리로 410",
            "울산광역시 남구 삼산로 288",
            "인천광역시 남동구 인하로 485",
            "광주광역시 서구 무진대로 904",
            "충청남도 천안시 동남구 만남로 43",
            "경기도 의정부시 평화로 525",
            "경기도 성남시 분당구 판교역로146번길 20",
            "부산광역시 해운대구 센텀남대로 35",
        ],
        "롯데시네마": [
            "서울특별시 송파구 올림픽로 300",
            "서울특별시 광진구 능동로 92",
            "서울특별시 강서구 하늘길 77",
            "경기도 수원시 권선구 세화로 134",
            "서울특별시 노원구 동일로 1414",
            "서울특별시 동대문구 왕산로 214",
            "서울특별시 관악구 신림로 330",
            "경기도 안양시 동안구 시민대로 180",
            "부산광역시 중구 중앙대로 2",
        ],
        "메가박스": [
            "서울특별시 강남구 영동대로 513",
        ],
    }

    domestic_mall = [
        "서울특별시 용산구 한강대로23길 55",
        "서울특별시 강남구 영동대로 513",
        "서울특별시 송파구 올림픽로 300",
        "서울특별시 서초구 신반포로 176",
        "경기도 고양시 덕양구 고양대로 1955",
        "서울특별시 영등포구 영중로 15",
        "경기도 성남시 분당구 판교역로146번길 20",
        "서울특별시 중구 남대문로 81",
        "서울특별시 송파구 충민로 66",
        "경기도 하남시 미사대로 750",
        "서울특별시 성동구 왕십리로 410",
        "서울특별시 송파구 올림픽로 240",
        "경기도 파주시 회동길 390",
    ]

    mymap = folium.Map(location=(37.5665, 126.9780), zoom_start=10)

    # 극장 마커
    color_map = {"CGV": "green", "롯데시네마": "red", "메가박스": "purple"}
    for theater_type, addresses in theaters.items():
        for addr in addresses:
            coord = get_coordinates_kakao(addr, api_key, geocode_url)
            if coord:
                folium.Marker(
                    location=list(coord),
                    popup=f"{theater_type}: {addr}",
                    tooltip=theater_type,
                    icon=folium.Icon(color=color_map.get(theater_type, "blue"), icon="film"),
                ).add_to(mymap)

    # 쇼핑몰 마커
    for addr in domestic_mall:
        coord = get_coordinates_kakao(addr, api_key, geocode_url)
        if coord:
            folium.Marker(
                location=list(coord),
                popup=f"Mall: {addr}",
                tooltip="Mall",
                icon=folium.Icon(color="black", icon="shopping-cart"),
            ).add_to(mymap)

    out_path = out_dir / cfg.get("outputs", {}).get("map_spot", "map_spot_theaters_malls.html")
    mymap.save(str(out_path))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
