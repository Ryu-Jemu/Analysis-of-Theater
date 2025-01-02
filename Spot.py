import requests
import folium
import webbrowser

def get_coordinates_kakao(address, api_key):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('documents'):
            # return latitude and longtitude
            longitude = data['documents'][0].get('x')
            latitude = data['documents'][0].get('y')
            return float(latitude), float(longitude)
        else:
            return None  # Can't search
    else:
        return None  # Failed

# API Key & Data of each theather
api_key = "0eb2cbe6aab31c516ce4175b6bf6b102"
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
        "부산광역시 해운대구 센텀남대로 35"
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
        "부산광역시 중구 중앙대로 2"
    ],
    "메가박스": [
        "서울특별시 강남구 영동대로 513"
    ]
}

theater_coordinates = {
    "CGV": [],
    "롯데시네마": [],
    "메가박스": []
}

for theater_type, address_list in theaters.items():
    for address in address_list:
        coordinates = get_coordinates_kakao(address, api_key)
        if coordinates:
            theater_coordinates[theater_type].append({"address": address, "coordinates": coordinates})

domestic_mall = [
    "서울특별시 용산구 한강대로23길 55",  # 용산아이파크몰
    "서울특별시 강남구 영동대로 513",       # 코엑스몰
    "서울특별시 송파구 올림픽로 300",       # 롯데월드몰
    "서울특별시 서초구 신반포로 176",       # 신세계백화점 강남
    "경기도 고양시 덕양구 고양대로 1955",  # 스타필드 고양
    "서울특별시 영등포구 영중로 15",        # 타임스퀘어
    "경기도 성남시 분당구 판교역로146번길 20",  # 현대백화점 판교
    "서울특별시 중구 남대문로 81",          # 롯데백화점 본점
    "서울특별시 서초구 신반포로 176",       # 신세계 강남점
    "서울특별시 송파구 충민로 66",          # 가든5
    "경기도 하남시 미사대로 750",           # 스타필드 하남
    "서울특별시 성동구 왕십리로 410",       # 이마트타운
    "서울특별시 송파구 올림픽로 240",       # 롯데마트
    "경기도 파주시 회동길 390",             # 신세계사이먼 파주 프리미엄 아울렛
    "서울특별시 영등포구 국제금융로 10",    # 여의도 IFC몰
    "부산광역시 해운대구 센텀남대로 35",    # 부산 해운대 신세계
    "부산광역시 부산진구 가야대로 772",     # 부산 롯데백화점
    "대구광역시 동구 동부로 149",           # 신세계백화점 대구점
    "대구광역시 북구 태평로 161",           # 롯데백화점 대구점
    "광주광역시 서구 무진대로 932",         # 신세계백화점 광주점
    "서울특별시 송파구 올림픽로 240",       # 롯데월드
    "광주광역시 서구 무진대로 932",         # 광주 롯데몰
    "서울특별시 강서구 하늘길 77",          # 김포공항 롯데몰
    "경기도 하남시 위례대로 200",           # 스타필드 시티 위례
    "부산광역시 해운대구 센텀남대로 35",    # 신세계백화점 센텀시티
    "서울특별시 용산구 한강대로 405",       # 서울역 롯데몰
    "서울특별시 영등포구 영중로 15",        # 영등포 타임스퀘어
    "대전광역시 서구 대덕대로 211",         # 대전 현대백화점
    "인천광역시 연수구 송도국제대로 123",   # 인천 송도 신세계
    "울산광역시 남구 삼산로 261",           # 울산 현대백화점
    "대구광역시 수성구 유니버시아드로 180", # 대구 스타디움
    "충청남도 아산시 배방읍 장재로 213",    # 충청남도 아산 이마트타운
    "경기도 안성시 공도읍 서동대로 3930-39",# 스타필드 안성
    "인천광역시 서구 청라대로 123",         # 스타필드 청라
    "경기도 의정부시 평화로 525",           # 의정부 현대백화점
    "부산광역시 기장군 장안읍 정관로 1133", # 부산 롯데프리미엄아울렛
    "경기도 광명시 광명로 821",             # 광명 스피돔
    "대전광역시 서구 계룡로 598",           # 대전 롯데백화점
    "부산광역시 해운대구 센텀남대로 35",    # 부산 센텀시티
    "충청남도 천안시 동남구 만남로 43",     # 천안 신세계
    "경기도 안양시 동안구 시민대로 180",    # 안양 평촌 현대백화점
    "세종특별자치시 나성북1로 45",          # 세종시 롯데몰
    "전라북도 전주시 완산구 기린대로 181",  # 전주 현대백화점
    "인천광역시 연수구 송도국제대로 123",   # 인천 롯데몰
    "강원도 강릉시 임영로 187",             # 강릉 현대백화점
    "인천광역시 부평구 부평문화로 35",       # 인천 부평 현대백화점
    "부산광역시 부산진구 중앙대로 672",     # 서면 롯데백화점
    "부산광역시 기장군 장안읍 정관로 1133", # 부산 기장 아울렛
    "경기도 수원시 팔달구 매산로1가 18-1"  # 수원 AK플라자
]

domestic_mall_coordinates = []

for address in domestic_mall:
    coordinates = get_coordinates_kakao(address, api_key)
    if coordinates:
        domestic_mall_coordinates.append({"address": address, "coordinates": coordinates})

# Generate map with improved markers
map_center = list(theater_coordinates["CGV"][0]["coordinates"])  # 중심 좌표 설정
map_object = folium.Map(location=map_center, zoom_start=12)

# Add CircleMarkers for theaters without clustering
color_map = {"CGV": "orange", "롯데시네마": "red", "메가박스": "darkpurple"}
for theater_type, locations in theater_coordinates.items():
    for location in locations:
        folium.Marker(
            location=location["coordinates"],
            popup=f"{location['address']} ({theater_type})",
            icon=folium.Icon(color=color_map[theater_type], icon="info-sign")  # 물방울 모양 유지
        ).add_to(map_object)

# Add CircleMarkers for domestic_mall without clustering
for location in domestic_mall_coordinates:
    folium.CircleMarker(
        location=location["coordinates"],
        radius=6,  # 쇼핑몰 마커는 조금 더 작게 설정
        color="blue",
        fill=True,
        fill_opacity=0.6,
        popup=f"{location['address']} (Mall)"
    ).add_to(map_object)

# Save the map and open it
map_object.save("Domestic_Theater.html")
webbrowser.open("Domestic_Theater.html")
