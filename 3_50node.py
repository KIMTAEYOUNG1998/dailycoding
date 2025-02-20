import osmnx as ox
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
import folium

# 1️⃣ 서울 도로 네트워크 불러오기
graph = ox.load_graphml('서울시_간소화.graphml')

# 2️⃣ 교차로 노드(차수 ≥ 3)만 필터링
intersection_nodes = [node for node, deg in dict(graph.degree()).items() if deg >= 3]

# 3️⃣ 교차로 노드 좌표 추출
node_list = list(intersection_nodes)
coords = np.array([[graph.nodes[n]['y'], graph.nodes[n]['x']] for n in node_list])

# 4️⃣ K-Means로 50개 클러스터 생성
kmeans = KMeans(n_clusters=50, random_state=42)
kmeans.fit(coords)
labels = kmeans.labels_

# 5️⃣ 각 클러스터에서 중심 좌표와 가장 가까운 교차로 노드 선택
top_nodes = []
for i in range(50):
    cluster_nodes = np.where(labels == i)[0]
    center = kmeans.cluster_centers_[i]
    distances = np.linalg.norm(coords[cluster_nodes] - center, axis=1)
    closest_node_index = cluster_nodes[np.argmin(distances)]
    top_nodes.append(node_list[closest_node_index])

# 6️⃣ 대표 노드 출력
print("선정된 50개 교차로 대표 노드:")
print(top_nodes)

# 7️⃣ Folium 지도 시각화
center = (37.5665, 126.9780)  # 서울 중심 좌표
m = folium.Map(location=center, zoom_start=12)

# 전체 도로망 추가
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
for _, edge in edges.iterrows():
    coords = [(point[1], point[0]) for point in edge['geometry'].coords]
    folium.PolyLine(coords, color='gray', weight=1, opacity=0.6).add_to(m)

# 대표 노드 시각화
for node in top_nodes:
    folium.Marker(
        location=(graph.nodes[node]['y'], graph.nodes[node]['x']),
        popup=f"Node {node}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# 8️⃣ 지도 저장
m.save('seoul_road_network_kmeans_50_intersections.html')
print("✅ K-Means로 선정된 50개 교차로 대표 노드가 'seoul_road_network_kmeans_50_intersections.html'에 저장되었습니다!")
