import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression

data = {
    "상영관": [20, 21, 18, 12, 12, 10, 10, 11, 14, 8, 9, 10, 8, 8, 8, 10, 8, 7, 11, 10],
    "좌석수": [3893, 4276, 3593, 2714, 2213, 2127, 1840, 2487, 3390, 1895, 1889, 1855, 1737, 1494, 1522, 1648, 1523, 1432, 2409, 2172],
    "연간관객수": [290, 257, 170, 125, 99, 96, 91, 86, 82, 78, 78, 78, 76, 72, 71, 70, 69, 67, 64, 64]
}
df = pd.DataFrame(data)

plt.rcParams['font.family'] = 'Malgun Gothic'  # For Windows users
plt.rcParams['font.family'] = 'AppleGothic'  # Mac 사용자

#Generate 3D graph
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

X = df["상영관"].values.reshape(-1, 1)
Y = df["좌석수"].values.reshape(-1, 1)
Z = df["연간관객수"].values

ax.scatter(X, Y, Z, c='b', label='Data Points', s=50)

#Add Trendline
model1 = LinearRegression().fit(X, Z)
Z_pred1 = model1.predict(X)
ax.plot(X.flatten(), Y.flatten(), Z_pred1, color='r', label='Trendline: 상영관-연간관객수')
model2 = LinearRegression().fit(Y, Z)
Z_pred2 = model2.predict(Y)
ax.plot(X.flatten(), Y.flatten(), Z_pred2, color='g', label='Trendline: 좌석수-연간관객수')

ax.set_title("3D Plot with Trendlines")
ax.set_xlabel("상영관")
ax.set_ylabel("좌석수")
ax.set_zlabel("연간관객수")
ax.legend()
plt.show()
