import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 

plt.rcParams['font.family'] = 'Arial'  
plt.rcParams['axes.unicode_minus'] = False

file_path = "연도별 영화 지표_Full Data_data.csv"
data = pd.read_csv(file_path)

data["Year of 연도"] = data["Year of 연도"].astype(int)

data["분류"] = data["분류"].replace({"한국영화": "Korean Films", "외국영화": "Foreign Films"})

sns.set_style('whitegrid')
sns.set_palette("Set2")

# Number of releases visualization
plt.figure(figsize=(14,8))
sns.lineplot(data=data, x="Year of 연도", y="개봉편수", hue="분류", marker="o")
plt.xticks(ticks=data["Year of 연도"].unique(), rotation=45)  
plt.grid(axis='x', linestyle='--')  
plt.title("Comparison of Number of Releases by Year (Korean vs Foreign Films)")
plt.xlabel("Year")
plt.ylabel("Number of Releases")
plt.legend(title="Film Category")
plt.show()

# Number of audiences visualization
plt.figure(figsize=(14, 8))
sns.lineplot(data=data, x="Year of 연도", y="관객수(만)", hue="분류", marker="o")
plt.xticks(ticks=data["Year of 연도"].unique(), rotation=45)
plt.grid(axis='x', linestyle='--')  
plt.title("Comparison of Audience Numbers by Year (Million)")
plt.xlabel("Year")
plt.ylabel("Audience (Million)")
plt.legend(title="Film Category")
plt.show()

# Revenue visualization
plt.figure(figsize=(14, 8))
sns.lineplot(data=data, x="Year of 연도", y="매출액(억)", hue="분류", marker="o")
plt.xticks(ticks=data["Year of 연도"].unique(), rotation=45)
plt.grid(axis='x', linestyle='--') 
plt.title("Comparison of Revenue by Year (Billion)")
plt.xlabel("Year")
plt.ylabel("Revenue (Billion)")
plt.legend(title="Film Category")
plt.show()
