import numpy as np
import pandas as pd
import osmnx as ox
from sklearn.preprocessing import StandardScaler
from k_means_constrained import KMeansConstrained
from geopy.distance import great_circle
import folium

# 1️⃣ 거리 행렬, 노드 매핑, 도로 네트워크 로드
distance_matrix = np.load('all_node_distances.npy')
node_mapping = pd.read_csv('node_index_mapping.csv', encoding='utf-8-sig')
graph = ox.load_graphml('서울시_간소화.graphml')

# 2️⃣ 데이터 로드 및 준비
df = pd.read_csv('meta_data.csv', encoding='utf-8-sig')
df = df.loc[df.index.repeat(df['화물 개수'])].reset_index(drop=True)
df['화물 개수'] = 1

# 3️⃣ 물류 데이터를 가장 가까운 노드와 매핑
closest_nodes = df.apply(lambda row: ox.distance.nearest_nodes(graph, row['경도'], row['위도']), axis=1)
df['closest_node'] = closest_nodes
node_indices = df['closest_node'].map(node_mapping.set_index('node_id')['index'])

# 4️⃣ 거리 기반 feature 생성
node_distances = distance_matrix[node_indices]
scaled_distances = StandardScaler().fit_transform(node_distances)

# 5️⃣ 기존 코드에서 계산된 거리 feature 추가
hub_coords_real = [(37.5431587, 126.9488943), (37.5992108, 126.7844098), (37.570379, 126.990688),
                   (37.575928, 126.994411), (37.552487, 126.937269), (37.564719, 126.977069), (37.585791, 126.925488)]

delivery_center_lat, delivery_center_lon = df['위도'].mean(), df['경도'].mean()
hub_coords_adjusted = [(delivery_center_lat + (lat - np.mean([c[0] for c in hub_coords_real]))*100, 
                        delivery_center_lon + (lon - np.mean([c[1] for c in hub_coords_real]))*100) 
                       for lat, lon in hub_coords_real]
for i, hub in enumerate(hub_coords_adjusted):
    df[f'distance_to_hub_{i}'] = df.apply(lambda row: great_circle((row['위도'], row['경도']), hub).miles ** 3, axis=1)

# 6️⃣ 모든 feature 결합
features = np.hstack((df[['위도', '경도']].values, scaled_distances, df[[f'distance_to_hub_{i}' for i in range(len(hub_coords_adjusted))]].values))

# 7️⃣ 클러스터링 수행
num_clusters = len(hub_coords_real)
kmeans = KMeansConstrained(n_clusters=num_clusters, size_min=len(df)//num_clusters, size_max=(len(df)//num_clusters)+1, random_state=42)
df['cluster'] = kmeans.fit_predict(features)

# 8️⃣ 지도 시각화
color_list = ['red', 'blue', 'green', 'purple','pink','orange','gray']
df['color'] = df['cluster'].apply(lambda x: color_list[x % len(color_list)])
map_ = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=12)
for idx, (lat, lon) in enumerate(hub_coords_real):
    folium.Marker(location=[lat, lon], popup=f"택배 거점 {idx+1} (원래 위치)", icon=folium.Icon(color='black')).add_to(map_)
df_sampled = df.groupby('cluster', group_keys=False).apply(lambda x: x.sample(frac=1/10, random_state=42))
for _, row in df_sampled.iterrows():
    folium.Marker(location=[row['위도'], row['경도']], popup=f"Cluster {row['cluster']}", icon=folium.Icon(color=row['color'])).add_to(map_)
map_.save('map_weighted_adjusted.html')
print("✅ 물류 데이터와 도로 네트워크 기반 최적화 클러스터링 완료! 'map_weighted_adjusted.html' 파일을 확인하세요.")
