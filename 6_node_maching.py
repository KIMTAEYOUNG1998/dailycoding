import osmnx as ox
import numpy as np
import pandas as pd

# 1️⃣ 서울시 간소화 도로 네트워크 로드
graph = ox.load_graphml('서울시_간소화.graphml')

# 2️⃣ 노드 리스트 추출
nodes = list(graph.nodes)

# 3️⃣ 노드 인덱스와 ID 매핑 생성
node_mapping = pd.DataFrame({'node_id': nodes, 'index': range(len(nodes))})

# 4️⃣ 매핑 데이터 저장
node_mapping.to_csv('node_index_mapping.csv', index=False, encoding='utf-8-sig')

print("✅ 노드 ID와 거리 행렬 인덱스 매핑이 'node_index_mapping.csv'에 저장되었습니다!")