import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

data_extended = {
    "지역": ["서울", "경기", "인천", "강원", "충청/대전/세종", "경상/대구/부산/울산", "전라/광주", "제주"],
    "민간소비지출액_2020": [2295, 1867, 1813, 1774, 1758, 1824, 1788, 1899],
    "점유율_2020": [23.1, 27.1, 5.3, 2.3, 10.2, 22.6, 8.4, 1.2],
    "민간소비지출액_2021": [2455, 1996, 1898, 1863, 1937, 1944, 1859, 1997],
    "점유율_2021": [23.8, 28.0, 4.9, 2.2, 10.1, 21.7, 8.4, 1.1],
    "민간소비지출액_2022": [2662, 2181, 2113, 2024, 2107, 2106, 2020, 2227],
    "점유율_2022": [25.3, 25.6, 5.1, 2.5, 10.0, 21.8, 8.4, 1.2]
}

plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 사용자
plt.rcParams['font.family'] = 'AppleGothic'  # Mac 사용자

years = [2020, 2021, 2022]
fig, axes = plt.subplots(1, 3, figsize = (15,5))

df_extended = pd.DataFrame(data_extended)

def calculate_correlation(dataframe, year):
    consumption_column = f"민간소비지출액_{year}"
    share_column = f"점유율_{year}"
    correlation, p_value = pearsonr(dataframe[consumption_column], dataframe[share_column])
    return correlation, p_value

correlation_results = {
    year: calculate_correlation(df_extended, year) for year in [2020, 2021, 2022]
}

for year, (correlation, p_value) in correlation_results.items():
    print(f"{year}년: 상관계수 = {correlation:.3f}, P-value = {p_value:.3f}")

for i, year in enumerate(years):
    consumption_column = f"민간소비지출액_{year}"
    share_column = f"점유율_{year}"
    
    # 각 연도별 산포도 그리기
    axes[i].scatter(df_extended[consumption_column], df_extended[share_column], color='blue')
    axes[i].set_title(f"{year}년 민간소비지출액과 점유율")
    axes[i].set_xlabel("1인당 민간소비지출액 (만 원)")
    axes[i].set_ylabel("지역 점유율 (%)")
    axes[i].grid(True)
    
    for j, txt in enumerate(df_extended["지역"]):
        axes[i].annotate(txt, (df_extended[consumption_column][j], df_extended[share_column][j]), 
            textcoords="offset points", xytext=(0,5), ha='center')


plt.tight_layout()
plt.show()