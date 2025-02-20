import numpy as np
import os
from tqdm import tqdm

def calculate_all_distances_from_representatives(distance_matrix_file, top_nodes, output_file='all_node_distances.npy'):
    # 50개 대표 노드 거리 행렬 로드
    distance_matrix = np.load(distance_matrix_file)
    num_nodes = distance_matrix.shape[1]

    # 전체 노드 간 거리 행렬 초기화
    all_distances = np.zeros((num_nodes, num_nodes))

    for i in tqdm(range(num_nodes), desc="전체 노드 거리 계산"):
        for j in range(num_nodes):
            if i == j:
                all_distances[i, j] = 0  # 자기 자신과의 거리는 0
            else:
                # i와 j의 대표 노드 찾기
                nearest_rep_i = np.argmin(distance_matrix[:, i])
                nearest_rep_j = np.argmin(distance_matrix[:, j])

                # 거리 계산: i-대표i + 대표i-대표j + j-대표j
                dist = (distance_matrix[nearest_rep_i, i] +
                        distance_matrix[nearest_rep_j, j] +
                        distance_matrix[nearest_rep_i, nearest_rep_j])

                all_distances[i, j] = dist

    np.save(output_file, all_distances)
    print(f"✅ 전체 노드 간 거리가 '{output_file}'에 저장되었습니다!")


if __name__ == "__main__":
    distance_matrix_file = 'distance_matrix_50_nodes.npy'
    top_nodes = [436808709, 2824550328, 436833635, 1906215104, 2589198381, 414684396, 9283138095, 2111825358, 1791473931, 1936512296,
                 414685283, 436848379, 7195666603, 11641428833, 436853220, 3540457899, 5287045374, 1936511372, 2418534615, 1835367875,
                 414686051, 10772669451, 9813541694, 414684838, 733859376, 414683393, 5119449053, 436880977, 414685964, 2279755237,
                 2343557898, 4744225606, 4875096513, 436718742, 2802920774, 436843544, 2824501228, 3355067061, 1925498351, 4163787275,
                 436867704, 1019336014, 2934404608, 436883204, 2931503804, 9040007342, 2288464686, 461779338, 1905595394, 2619561052]

    calculate_all_distances_from_representatives(distance_matrix_file, top_nodes, output_file='all_node_distances.npy')
