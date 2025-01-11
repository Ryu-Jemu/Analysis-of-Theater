import requests
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import csv

# API authentication credentials
client_id = "_____"  
client_secret = "_____"  

# API endpoint for Naver Blog Search
url = "______" 

# Search keyword
query = "메가박스" 

# Request parameters
params = {
    "query": query,  
    "display": 100,  # Number of results per request (max: 100)
    "start": 1,  
    "sort": "sim"  
}

# Request headers including authentication
headers = {
    "X-Naver-Client-Id": client_id,  
    "X-Naver-Client-Secret": client_secret  
}

# Make the API request
response = requests.get(url, headers=headers, params=params)

plt.rcParams['font.family'] = 'Malgun Gothic'  # For Windows users

# Check if the API call is successful
if response.status_code == 200:  
    data = response.json()  

    
    text_data = []
    for item in data["items"]:
        text_data.append(item["title"])  
        text_data.append(item["description"])  

    text = " ".join(text_data)
    okt = Okt()  
    tokens = okt.nouns(text)  

    # Remove stopwords (words that are not useful for analysis)
    stopwords = [
    "CGV", "롯데시네마", "메가박스", "영화", "상영관", "극장", "좌석", 
    "예매", "상영", "시간표", "영화관", "고객센터", "블로그", "후기", "포스팅",
    "링크", "사진", "공유", "작성", "추천", "조회", "댓글", "좋아요", "대해", 
    "은", "는", "이", "가", "을", "를", "의", "와", "과", "도", "에", "에서", 
    "보다", "으로", "또는", "그리고", "해서", "그러나", "너무", "정말", "많이", 
    "아주", "그냥", "그래서", "이제", "다시", "이렇게", "저렇게", "😀", "😢", "❤️",
    "!", "?", ".", ",", "/", "@", "#", "%", "2024", "11월", "2023년", "정보","대한"
    ]

    filtered_tokens = [token for token in tokens if token not in stopwords and len(token) > 1]
    word_counts = Counter(filtered_tokens)

    # **Save keywords to a CSV file**
    csv_file_path = "extracted_keywords.csv"  
    with open(csv_file_path, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)  
        writer.writerows(word_counts.items()) 
    print(f"Keywords have been saved to '{csv_file_path}'.")

    # **Generate a word cloud**
    font_path = "C:/Windows/Fonts/malgun.ttf"  # Path to Korean font for Windows
    wordcloud = WordCloud(
        font_path=font_path,  
        background_color="white",  
        width=800,  
        height=600,  
        max_words=50  # Limit the word cloud to the top 50 words
    ).generate_from_frequencies(word_counts)  
    # Visualize the word cloud
    plt.figure(figsize=(10, 8))  
    plt.imshow(wordcloud, interpolation="bilinear")  
    plt.axis("off")  
    plt.title(f"'{query}' Related Word Cloud", fontsize=15)  
    plt.show()  
else:
    # Print error details if the API call fails
    print(f"Error Code: {response.status_code}") 
    print(f"Error Message: {response.text}")  