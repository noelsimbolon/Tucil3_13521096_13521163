from ..model.node import Node


class FileInputHandler:
    @staticmethod
    def load_file(path: str) -> (list[Node], list[list[float]]):
        file1 = open(path, 'r')

        lines = file1.readlines()
        node_count = -1
        node_list: list[Node] = []
        adj_matrix: list[list[float]] = []

        for i, line in enumerate(lines):
            try:
                if i == 0:  # matrix size / node count
                    node_count = int(line)
                    adj_matrix = [[] for _ in range(node_count)]
                    continue

                if 0 < i < node_count + 1:
                    node_id = i - 1
                    coordinates = line.split(' ')
                    if len(coordinates) != 2:
                        raise RuntimeError("Error while processing file.")
                    node_list.append(Node(node_id, float(coordinates[0]), float(coordinates[1])))

                    continue

                if i >= node_count + 1:
                    weights = line.split(' ')
                    if len(weights) != node_count:
                        raise RuntimeError("Error while processing file.")

                    v_idx = i - (node_count + 1)
                    adj_matrix[v_idx] = ([0.0 for _ in range(node_count)])
                    for j, weight in enumerate(weights):
                        adj_matrix[v_idx][j] = float(weight)

            except (ValueError, IndexError):
                raise RuntimeError("Error while processing file.")

        return node_list, adj_matrix
