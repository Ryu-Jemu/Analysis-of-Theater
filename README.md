<<<<<<< HEAD
# Movie Theater and Transportation Data Visualization Project

## Overview
**Purpose**  
To analyze and visualize movie theaters and public transportation data in South Korea, providing insights into spatial relationships and locational dynamics.

**Key Features**  
- Visualizing movie theater and subway station locations on an interactive map.  
- Performing 3D statistical analysis on movie theater-related data.  
- Collecting accurate geolocation data using Geocoding APIs.  
- Creating user-friendly interactive maps.  

---

## Features
- **Movie Theater Data Visualization**  
  Clustering and mapping the locations of CGV, Lotte Cinema, and Megabox.  
- **Subway Station Integration**  
  Integrating subway station data into a unified visualization.  
- **3D Statistical Analysis**  
  Analyzing screen count, seat count, and annual audience data in 3D.  
- **Interactive Map Creation**  
  Generating web-based maps using the Folium library.  

---

## Requirements
- **Python Version**: 3.8 or later  
- **Required Libraries**:  
  - pandas, numpy  
  - folium, matplotlib  
  - scikit-learn, requests, openpyxl  

**Installation**:  
```bash
pip install pandas numpy folium matplotlib scikit-learn requests openpyxl
=======
# Analysis-of-Theater

전국 **극장(영화관)** · **지하철역** · **POI(쇼핑몰/장소)** 데이터를 활용해  
- Folium 기반 **지도 시각화(HTML)**  
- 연도별 영화 지표 **시계열 시각화(PNG)**  
- (선택) 네이버 검색 API 기반 **텍스트 키워드 분석(CSV/PNG)**  
을 한 번의 실행으로 생성하는 분석 레포지토리입니다.

---

## 1) 한 번에 실행하기 (권장)

```bash
# 의존성 설치
pip install -r requirements.txt

# 단일 실행(모든 산출물 + 리포트 생성)
./run.sh
```

실행이 끝나면 `outputs/report.md`가 자동 생성됩니다.

---

## 2) 설정(config.yaml)

입력 파일/출력 파일명/실행 단계 on-off를 `config.yaml`에서 제어합니다.

### 입력 파일
- `paths.theater_xlsx`: `data_theaters_domestic.xlsx`
- `paths.station_xlsx`: `data_stations_domestic.xlsx`
- `paths.movie_indicators_csv`: `data_movie_indicators_by_year.csv`

### API 키(선택)
지도(지오코딩)·텍스트 분석을 실행하려면 아래 환경변수를 설정하세요.

```bash
export KAKAO_REST_API_KEY="..."
export NAVER_CLIENT_ID="..."
export NAVER_CLIENT_SECRET="..."
```

> 키는 코드/레포에 하드코딩하지 않습니다.

---

## 3) 산출물(outputs)

`config.yaml > outputs`에서 파일명을 관리합니다. 기본값은 아래와 같습니다.

- 지도
  - `outputs/map_theaters_stations.html` (극장 + 역)
  - `outputs/map_spot_theaters_malls.html` (예시 주소 기반 POI)
- 영화 지표 시각화
  - `outputs/movie_releases_by_year.png`
  - `outputs/movie_audience_by_year.png`
  - `outputs/movie_sales_by_year.png`
- 3D 분석
  - `outputs/theater_3d_trendlines.png`
- 소비지출-점유율 상관
  - `outputs/consumption_share_correlation.png`
- (선택) 텍스트 키워드 분석
  - `outputs/naver_keywords.csv`
  - `outputs/naver_wordcloud.png`
- 자동 리포트
  - `outputs/report.md`

---

## 4) 스크립트 구성

- `pipeline.py` : 전체 파이프라인 실행(단일 엔트리포인트) + 리포트 생성
- `run.sh` : 쉘 원클릭 실행 스크립트
- `Integrate_stations.py` : 극장/역 지도 생성
- `Spot.py` : (예시) 극장/쇼핑몰 POI 지도 생성
- `Visualization.py` : 연도별 영화 지표 시각화
- `Graph3D.py` : 3D 산점도 + 추세선(예시 데이터)
- `Consumtion_Share_Analysis.py` : 상관 분석(예시 데이터)
- `text_analysis.py` : 네이버 검색 API 기반 키워드/워드클라우드(선택)

---

## 5) 주의 사항
- 네이버/카카오 API 사용 시 각 서비스의 이용약관 및 호출 제한(rate limit)을 준수하세요.
>>>>>>> e1d4b36 (config 구성 및 파이프라인 구현)
