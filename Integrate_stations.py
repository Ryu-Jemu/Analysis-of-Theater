"""극장(엑셀), 지하철역(엑셀)을 결합해 Folium 지도를 생성합니다.

- 극장 주소는 Kakao Local API(주소→좌표)로 변환합니다.
- 역 좌표는 Domestic_station.xlsx의 '역위도', '역경도'를 우선 사용합니다.
- 서울교통공사 역의 '역사도로명주소'가 있다면 추가로 주소→좌표 변환을 수행할 수 있습니다.

출력:
- outputs/updated_map_with_stations_and_new_places.html
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import folium
import pandas as pd
import requests
import yaml
from folium.plugins import MarkerCluster


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_DIR_DEFAULT = ROOT / "outputs"


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


def get_coordinates(address: str, api_key: str, url: str) -> tuple[str | None, str | None]:
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        return None, None
    result = r.json()
    if result.get("documents"):
        return result["documents"][0].get("y"), result["documents"][0].get("x")
    return None, None


def clean_address(address: str) -> str:
    address = address.strip()
    address = re.sub(r"\s+", " ", address)
    address = re.sub(r"\(.*?\)", "", address)
    address = re.sub(r"\s*\d+층", "", address)
    address = re.sub(r"\s*\d+~", "", address)
    address = re.sub(r"\s*(로|길|번길)\s+", r"\1", address)
    address = re.sub(r"\s*(로|길|번길)", r"\1", address)
    address = re.sub(r"(\d+)(번길|길|로|대로|가|동)", r"\1 \2", address)
    address = re.sub(r"(\d+)\s*번\s*길", r"\1번길", address)
    address = re.sub(r"(\w+)\s*(로|길|대로|번길)", r"\1\2", address)
    address = re.sub(r"(\d+)([A-Za-z])", r"\1 \2", address)
    address = re.sub(r"\s*(스퀘어|플라자|타워|아울렛|현대시티|드림어반|W)$", "", address)
    return address.strip()


def load_station_coordinates(file_path: Path) -> pd.DataFrame:
    data = pd.read_excel(file_path, engine="openpyxl")
    if "역위도" not in data.columns or "역경도" not in data.columns:
        raise KeyError("열 이름 '역위도' 또는 '역경도'가 없습니다.")
    return data[["역위도", "역경도"]].dropna()


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

    theater_xlsx = ROOT / cfg.get("paths", {}).get("theater_xlsx", "Domestic_theater.xlsx")
    station_xlsx = ROOT / cfg.get("paths", {}).get("station_xlsx", "Domestic_station.xlsx")

    sheet_name = "2023년 전국 극장 리스트"
    data = pd.read_excel(theater_xlsx, sheet_name=sheet_name, engine="openpyxl")
    data.columns = data.columns.str.strip()

    if "영화관명" not in data.columns or "소재지" not in data.columns:
        raise KeyError("엑셀에 '영화관명' 또는 '소재지' 컬럼이 없습니다. 파일/시트를 확인하세요.")

    cgv_addresses = list(set(data[data["영화관명"].str.contains("CGV", na=False)]["소재지"]))
    lotte_addresses = list(set(data[data["영화관명"].str.contains("롯데시네마", na=False)]["소재지"]))
    mega_addresses = list(set(data[data["영화관명"].str.contains("메가박스", na=False)]["소재지"]))

    def process_addresses(address_list: list[str]) -> list[str]:
        cleaned = [clean_address(addr) for addr in address_list if isinstance(addr, str)]
        return sorted(set(cleaned))

    processed_cgv = process_addresses(cgv_addresses)
    processed_lotte = process_addresses(lotte_addresses)
    processed_mega = process_addresses(mega_addresses)

    mymap = folium.Map(location=(37.5665, 126.9780), zoom_start=10)
    cluster = MarkerCluster().add_to(mymap)

    def add_markers(addresses: list[str], color: str) -> None:
        for addr in addresses:
            lat, lng = get_coordinates(addr, api_key, geocode_url)
            if lat and lng:
                folium.Marker(
                    location=[float(lat), float(lng)],
                    popup=addr,
                    tooltip="주소",
                    icon=folium.Icon(color=color, icon="info-sign"),
                ).add_to(cluster)

    add_markers(processed_cgv, "green")
    add_markers(processed_lotte, "red")
    add_markers(processed_mega, "purple")

    # 역 좌표(엑셀 컬럼 사용)
    station_data = load_station_coordinates(station_xlsx)
    for _, row in station_data.iterrows():
        folium.CircleMarker(
            location=[row["역위도"], row["역경도"]],
            radius=4,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.9,
            tooltip="역",
        ).add_to(mymap)

    # 추가 POI(예시)
    new_places = [
        "경기도 용인시 처인구 포곡읍 에버랜드로 199",
        "경기도 과천시 막계동 55 서울랜드",
        "경기도 용인시 기흥구 민속촌로 90",
        "경기도 가평군 상면 수목원로 432",
        "경기도 양주시 은현면 두리길 155",
    ]

    for place in new_places:
        lat, lng = get_coordinates(place, api_key, geocode_url)
        if lat and lng:
            folium.Marker(
                location=[float(lat), float(lng)],
                popup=place,
                tooltip="POI",
                icon=folium.Icon(color="black", icon="info-sign"),
            ).add_to(mymap)

    # (선택) 서울교통공사 역 주소 기반 추가 표시
    station_raw = pd.read_excel(station_xlsx, engine="openpyxl")
    if "운영기관명" in station_raw.columns and "역사도로명주소" in station_raw.columns:
        filtered = station_raw[station_raw["운영기관명"] == "서울교통공사"]
        addresses = filtered["역사도로명주소"].dropna().astype(str).apply(clean_address).tolist()
        for addr in addresses:
            lat, lng = get_coordinates(addr, api_key, geocode_url)
            if lat and lng:
                folium.CircleMarker(
                    location=[float(lat), float(lng)],
                    radius=4,
                    color="navy",
                    fill=True,
                    fill_color="navy",
                    fill_opacity=0.7,
                    tooltip="서울교통공사(주소기반)",
                ).add_to(mymap)

    out_path = out_dir / cfg.get("outputs", {}).get("map_theaters_and_stations", "map_theaters_stations.html")
    mymap.save(str(out_path))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
