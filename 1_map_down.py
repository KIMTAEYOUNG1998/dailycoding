import osmnx as ox

# 서울 도로 네트워크 다운로드
graph = ox.graph_from_place("Seoul, South Korea", network_type="drive")

# 그래프 저장
ox.save_graphml(graph, filepath='seoul_road_network.graphml')

print("✅ 서울 도로 네트워크 데이터가 'seoul_road_network.graphml'로 저장되었습니다!")