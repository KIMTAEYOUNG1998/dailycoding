import networkx as nx
import pandas as pd
import osmnx as ox
import folium
import heapq  # 🚀 heapq를 사용하여 최근접 k개 후보 탐색 속도 개선

# ✅ 데이터 로드 및 간소화
graph_path = "seoul_road_network.graphml"
meta_data_path = "택배생성데이터_clustered.csv"

df = pd.read_csv(meta_data_path, encoding="utf-8-sig")
graph = ox.load_graphml(graph_path)  # 도로 네트워크

# ✅ 도로 네트워크에서 연결된 노드만 남기기 (최대 연결 그래프 선택)
connected_components = list(nx.connected_components(graph.to_undirected()))
largest_component = max(connected_components, key=len)
graph = graph.subgraph(largest_component)
print(f"🚀 연결된 노드만 포함된 그래프 노드 수: {len(graph.nodes)}")

# ✅ 거점 좌표 (클러스터 중심)
hub_coords_real = [
    (37.5431586580816, 126.948894324085),  
    (37.5992108624948, 126.78440979783),
    (37.570379, 126.990688),
    (37.575928, 126.994411),
    (37.552487, 126.937269),
    (37.564719, 126.977069),
    (37.585791, 126.925488)
]

# ✅ 연결된 노드만 선택하는 함수
def find_nearest_connected_node(lat, lon):
    """연결된 OSM 노드 중 가장 가까운 노드 찾기"""
    try:
        nearest_node = ox.distance.nearest_nodes(graph, X=lon, Y=lat)
        if nearest_node in graph and list(graph.neighbors(nearest_node)):
            return nearest_node
    except Exception:
        pass

    # ✅ 연결된 노드 중 가장 가까운 노드 찾기
    connected_nodes = [n for n in graph.nodes if list(graph.neighbors(n))]
    nearest_node = min(
        connected_nodes, 
        key=lambda n: ox.distance.great_circle(lat, lon, graph.nodes[n]['y'], graph.nodes[n]['x'])
    )
    
    return nearest_node

# ✅ 거점 노드 찾기
hub_nodes = {i: find_nearest_connected_node(lat, lon) for i, (lat, lon) in enumerate(hub_coords_real)}
df["osm_node"] = df.apply(lambda row: find_nearest_connected_node(row["위도"], row["경도"]), axis=1)

# ✅ 최단 경로 탐색 (예외 처리 포함)
def safe_shortest_path(graph, src, dst):
    try:
        return nx.shortest_path(graph, src, dst, weight="length")
    except nx.NetworkXNoPath:
        print(f"🚨 경로 없음: {src} -> {dst}, 대체 경로 탐색")
        return []

# ✅ 최근접 k개 노드 찾는 함수 (최적화)
def find_nearest_k_nodes(graph, src, delivery_nodes, k=5):
    """src에서 가장 가까운 k개의 배송지 노드를 찾는 함수"""
    candidates = []
    for node in delivery_nodes:
        try:
            distance = nx.shortest_path_length(graph, src, node, weight="length")
            heapq.heappush(candidates, (distance, node))
        except nx.NetworkXNoPath:
            continue  # 경로 없으면 건너뛰기

    return [heapq.heappop(candidates)[1] for _ in range(min(k, len(candidates)))]

# ✅ 최적 경로 탐색 (최근접 k개 후보 활용 - 속도 개선)
def find_optimal_route_with_k_nearest(cluster_id, k=10):
    cluster_data = df[df["cluster"] == cluster_id]
    start_node = hub_nodes[cluster_id]
    delivery_nodes = set(cluster_data["osm_node"].unique())  # 🚀 set()으로 관리하여 탐색 속도 개선
    
    if not delivery_nodes:
        return [start_node, start_node], 0, []

    visited = {}  # 🚀 방문 체크를 딕셔너리로 변경 (set()보다 빠름)
    optimal_route = [start_node]
    total_distance = 0
    current_node = start_node
    visited_delivery_nodes = []

    while delivery_nodes:
        visited[current_node] = True

        # ✅ 최근접 k개 후보 중 최적 선택 (미리 k개만 계산해서 최적화)
        nearest_k = find_nearest_k_nodes(graph, current_node, list(delivery_nodes), k)
        if not nearest_k:
            break  

        next_node = min(nearest_k, key=lambda n: nx.shortest_path_length(graph, current_node, n, weight="length"))

        path = safe_shortest_path(graph, current_node, next_node)
        if path:
            total_distance += nx.shortest_path_length(graph, current_node, next_node, weight="length")
            optimal_route.extend(path[:-1])
            visited_delivery_nodes.append(next_node)
            current_node = next_node
            delivery_nodes.remove(next_node)  # 🚀 방문한 노드는 삭제

    # ✅ 다시 거점으로 복귀
    path_back = safe_shortest_path(graph, current_node, start_node)
    if path_back:
        total_distance += nx.shortest_path_length(graph, current_node, start_node, weight="length")
        optimal_route.extend(path_back[1:])

    return optimal_route, total_distance, visited_delivery_nodes

# ✅ 모든 클러스터에 대해 최적 경로 찾기 및 즉시 저장
color_palette = ['red', 'blue', 'green', 'purple', 'darkgreen', 'orange', 'gray']

for i, cluster_id in enumerate(df["cluster"].unique()):
    route, distance, visited_delivery_nodes = find_optimal_route_with_k_nearest(cluster_id, k=5)

    # ✅ 지도 생성 (클러스터별 개별 지도)
    center = [df[df["cluster"] == cluster_id]["위도"].mean(), df[df["cluster"] == cluster_id]["경도"].mean()]
    map_cluster = folium.Map(location=center, zoom_start=12)

    # ✅ 해당 클러스터의 거점만 지도에 표시
    hub_lat, hub_lon = hub_coords_real[cluster_id]
    folium.Marker(
        location=[hub_lat, hub_lon],
        popup=f"거점 {cluster_id}",
        icon=folium.Icon(color="black", icon="cloud")
    ).add_to(map_cluster)

    # ✅ 배송지 도착 순서 매핑
    delivery_order = {node: idx+1 for idx, node in enumerate(visited_delivery_nodes)}

    # ✅ 클러스터별 배송지 표시
    cluster_data = df[df["cluster"] == cluster_id]
    route_color = color_palette[i % len(color_palette)]

    for _, row in cluster_data.iterrows():
        node = row["osm_node"]
        order_num = delivery_order.get(node, "?")  

        folium.Marker(
            location=[row["위도"], row["경도"]],
            icon=folium.DivIcon(
                html=f"""
                    <div style="
                        font-size: 14pt; 
                        color: black; 
                        background: white; 
                        padding: 8px; 
                        border-radius: 50%;
                        border: 2px solid black;
                        text-align: center;
                        width: 35px;
                        height: 35px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;">
                        {order_num}
                    </div>
                """
            )
        ).add_to(map_cluster)

    # ✅ 클러스터별 경로 추가
    route_coords = [(graph.nodes[node]["y"], graph.nodes[node]["x"]) for node in route if node in graph.nodes]
    folium.PolyLine(
        locations=route_coords,
        color=route_color,
        weight=3,
        popup=f"Cluster {cluster_id} - Distance: {distance:.2f}m"
    ).add_to(map_cluster)

    # ✅ 🚀 클러스터 개별 즉시 저장
    file_name = f"optimal_delivery_routes_cluster_{cluster_id}.html"
    map_cluster.save(file_name)
    print(f"✅ 클러스터 {cluster_id} 즉시 저장 완료! 파일: {file_name}")

print(f"✅ 모든 클러스터 최적 경로 계산 완료!") 
