import osmnx as ox
import networkx as nx
import folium

# 1️⃣ 서울 도로 네트워크 불러오기
graph = ox.load_graphml('seoul_road_network_simplified_filtered.graphml')

# 2️⃣ Dead-end 도로 및 작은 도로 반복 제거
main_road_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']

for i in range(10):
    print(f"🚧 {i+1}/10 반복 중...")

    # Dead-end 도로 제거
    degree = dict(graph.degree())
    remove_nodes = [node for node, deg in degree.items() if deg < 2]
    graph.remove_nodes_from(remove_nodes)

    # 작은 도로 제거
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    remove_edges = edges[~edges['highway'].isin(main_road_types)].index
    graph.remove_edges_from(remove_edges)

    # 방향 그래프를 무향 그래프로 변환
    undirected_graph = graph.to_undirected()

    # 가장 큰 연결 성분만 유지
    largest_component = max(nx.connected_components(undirected_graph), key=len)
    graph = undirected_graph.subgraph(largest_component).copy()

# 3️⃣ 간소화된 그래프 저장
ox.save_graphml(graph, filepath='seoul_road_network_simplified_filtered_iterative.graphml')

# 4️⃣ 통계 계산
stats = ox.basic_stats(graph)
print("📊 반복적으로 간소화된 서울 도로 네트워크 통계 📊")
for key, value in stats.items():
    print(f"{key}: {value}")

# 5️⃣ Folium 지도로 시각화
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
center = (37.5665, 126.9780)  # 서울 중심 좌표
m = folium.Map(location=center, zoom_start=12)

for _, edge in edges.iterrows():
    coords = [(point[1], point[0]) for point in edge['geometry'].coords]
    folium.PolyLine(coords, color='green', weight=2, opacity=0.8).add_to(m)

# 6️⃣ 시각화 지도 저장
m.save('seoul_road_network_simplified_iterative_map.html')
print("✅ 반복적으로 Dead-end 도로와 작은 도로를 제거한 네트워크가 'seoul_road_network_simplified_iterative_map.html'에 저장되었습니다!")
