import osmnx as ox
import networkx as nx
import numpy as np
import os
from tqdm import tqdm

def calculate_distances_with_checkpoint(graph, top_nodes, save_interval=5, filename="distance_matrix_50_nodes.npy"):
    nodes = list(graph.nodes)
    num_top_nodes = len(top_nodes)
    num_nodes = len(nodes)
    distance_matrix = np.zeros((num_top_nodes, num_nodes))

    # 중간 저장된 파일이 있으면 로드
    if os.path.exists(filename):
        distance_matrix = np.load(filename)
        start_index = np.count_nonzero(distance_matrix[:, 0])  # 계산된 행 개수
        print(f"🔄 이전에 계산된 {start_index}/{num_top_nodes}개 노드의 거리를 복원했습니다.")
    else:
        start_index = 0

    for i in tqdm(range(start_index, num_top_nodes), desc="대표 노드 거리 계산"):
        source = top_nodes[i]
        lengths = nx.single_source_dijkstra_path_length(graph, source, weight='length')

        for j, node in enumerate(nodes):
            distance_matrix[i, j] = lengths.get(node, np.inf)

        # save_interval마다 중간 저장
        if (i + 1) % save_interval == 0 or (i + 1) == num_top_nodes:
            np.save(filename, distance_matrix)
            print(f"✅ {i+1}/{num_top_nodes} 노드 계산 완료, 중간 결과 '{filename}'에 저장됨")

    return distance_matrix

if __name__ == "__main__":
    graph = ox.load_graphml('서울시_간소화.graphml')
    top_nodes = [436808709, 2824550328, 436833635, 1906215104, 2589198381, 414684396, 9283138095, 2111825358, 1791473931, 1936512296,
                 414685283, 436848379, 7195666603, 11641428833, 436853220, 3540457899, 5287045374, 1936511372, 2418534615, 1835367875,
                 414686051, 10772669451, 9813541694, 414684838, 733859376, 414683393, 5119449053, 436880977, 414685964, 2279755237,
                 2343557898, 4744225606, 4875096513, 436718742, 2802920774, 436843544, 2824501228, 3355067061, 1925498351, 4163787275,
                 436867704, 1019336014, 2934404608, 436883204, 2931503804, 9040007342, 2288464686, 461779338, 1905595394, 2619561052]

    distance_matrix = calculate_distances_with_checkpoint(graph, top_nodes, save_interval=1, filename="distance_matrix_50_nodes.npy")
    print("🚀 모든 거리 계산 완료!")
