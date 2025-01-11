import pandas as pd
import re
import requests
import folium
import webbrowser
from folium.plugins import MarkerCluster

def get_coordinates(address, api_key):
    url = "_____" #Enter api address
    headers = {"Authorization": f"KakaoAK {api_key}"} # Modify according to your api key
    params = {"query": address}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['documents']:
            return result['documents'][0]['y'], result['documents'][0]['x']
    return None, None

def load_station_coordinates(file_path):
    """
    Domestic_station 파일에서 역의 위도와 경도를 불러오는 함수
    """
    data = pd.read_excel(file_path, engine='openpyxl')
    if '역위도' not in data.columns or '역경도' not in data.columns:
        raise KeyError("열 이름 '역위도' 또는 '역경도'가 없습니다.")
    return data[['역위도', '역경도']].dropna()

API_KEY = "_____" #Enter your api key
file_path = "Domestic_theater.xlsx"
sheet_name = '2023년 전국 극장 리스트'
data = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
data.columns = data.columns.str.strip()

if '영화관명' not in data.columns:
    raise KeyError("열 이름 '영화관명'이 없습니다. 데이터를 확인하세요.")

try:
    cgv_addresses = list(set(data[data["영화관명"].str.contains("CGV", na=False)]["소재지"]))
    lotte_addresses = list(set(data[data["영화관명"].str.contains("롯데시네마", na=False)]["소재지"]))
    mega_addresses = list(set(data[data["영화관명"].str.contains("메가박스", na=False)]["소재지"]))
except KeyError as e:
    raise KeyError(f"열 이름 '소재지'를 찾을 수 없습니다. {e}")

def clean_address(address):
    if not isinstance(address, str):
        return address
    address = address.strip()
    address = re.sub(r'\s+', ' ', address)
    address = re.sub(r'\(.*?\)', '', address)
    address = re.sub(r'\s*\d+층', '', address)
    address = re.sub(r'\s*\d+~', '', address)
    address = re.sub(r'\s*(로|길|번길)\s+', r'\1', address)
    address = re.sub(r'\s*(로|길|번길)', r'\1', address)
    address = re.sub(r'(\d+)(번길|길|로|대로|가|동)', r'\1 \2', address)
    address = re.sub(r'(\d+)\s*번\s*길', r'\1번길', address)
    address = re.sub(r'(\w+)\s*(로|길|대로|번길)', r'\1\2', address)
    address = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', address)
    address = re.sub(r'\s*(스퀘어|플라자|타워|아울렛|현대시티|드림어반|W)$', '', address)
    return address

def process_addresses(address_list):
    cleaned_addresses = [clean_address(addr) for addr in address_list]
    unique_addresses = sorted(set(cleaned_addresses))
    return unique_addresses

processed_cgv_addresses = process_addresses(cgv_addresses)
processed_lotte_addresses = process_addresses(lotte_addresses)
processed_mega_addresses = process_addresses(mega_addresses)

map_center = (37.5665, 126.9780)
mymap = folium.Map(location=map_center, zoom_start=10)
marker_cluster = MarkerCluster().add_to(mymap)

def add_markers(addresses, color):
    for addr in addresses:
        lat, lng = get_coordinates(addr, API_KEY)
        if lat and lng:
            folium.Marker(
                location=[float(lat), float(lng)],
                popup=addr,
                tooltip="주소 클릭",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(mymap)
        else:
            print(f"좌표 변환 실패: {addr}")

add_markers(processed_cgv_addresses, "green")
add_markers(processed_lotte_addresses, "red")
add_markers(processed_mega_addresses, "purple")

station_file_path = "Domestic_station.xlsx"
station_data = load_station_coordinates(station_file_path)

for _, row in station_data.iterrows():
    folium.CircleMarker(
        location=[row['역위도'], row['역경도']],
        radius=5,  
        color='blue',  
        fill=True,
        fill_color='blue',  
        fill_opacity=1,  
        popup=f"역 위치: {row['역위도']}, {row['역경도']}",
        tooltip="역 정보"
    ).add_to(mymap)
    
new_places = [
    "경기도 용인시 처인구 포곡읍 에버랜드로 199", 
    "경기도 과천시 막계동 55 서울랜드",  
    "경기도 용인시 기흥구 민속촌로 90",  
    "경기도 가평군 상면 수목원로 432",
    "경기도 가평군 상면 수목원로 12",  
    "경기도 양주시 은현면 두리길 155"  
]

def add_new_places_markers(places, color="black"):
    for place in places:
        lat, lng = get_coordinates(place, API_KEY)
        if lat and lng:
            folium.Marker(
                location=[float(lat), float(lng)],
                popup=place,
                tooltip="장소 클릭",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(mymap)
        else:
            print(f"좌표 변환 실패: {place}")

add_new_places_markers(new_places, color="black")


def add_station_markers_with_address(file_path, api_key):
    station_data = pd.read_excel(file_path, engine='openpyxl')

    filtered_stations = station_data[station_data['운영기관명'] == '서울교통공사']
    addresses = filtered_stations['역사도로명주소'].dropna().apply(clean_address)

    for address in addresses:
        lat, lng = get_coordinates(address, api_key)
        if lat and lng:
            folium.CircleMarker(
                location=[float(lat), float(lng)],
                radius=5,  
                color='blue',  
                fill=True,
                fill_color='blue',  
                fill_opacity=1,  
                popup=f"주소: {address}\n위도: {lat}\n경도: {lng}",
                tooltip="역 정보"
            ).add_to(mymap)
        else:
            print(f"좌표 변환 실패: {address}")

station_file_path = "Domestic_station.xlsx"
add_station_markers_with_address(station_file_path, API_KEY)

mymap.save("updated_map_with_stations_and_new_places.html")
webbrowser.open("updated_map_with_stations_and_new_places.html")
