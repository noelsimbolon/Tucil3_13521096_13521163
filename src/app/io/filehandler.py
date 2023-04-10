from model.node import Node


class FileInputHandler:

    @staticmethod
    def load_file(path: str) -> (list[Node], list[list[float]]):
        file1 = open(path, 'r')

        lines = file1.readlines()
        node_count = -1
        node_list: list[Node] = []
        adj_matrix: list[list[float]] = [[]]
        for i, line in enumerate(lines):
            if i == 0:  # matrix size / node count
                try:
                    node_count = int(line)
                except ValueError:
                    raise "error while processing file"
                continue

            if 0 < i < node_count + 1:
                node_id = i -1
                coordinates = line.split(' ')
                if len(coordinates) != 2:
                    raise "error while processing file"
                try:
                    node_list.append(Node(node_id, float(coordinates[0]), float(coordinates[1])))
                except ValueError:
                    raise "error while processing file"

                continue

            if i >= node_count + 1:
                weights = line.split(' ')
                if len(weights) != node_count:
                    raise "error while processing file"
                try:
                    adj_matrix.append([0.0 for _ in range(node_count)])
                    v_idx = i - (node_count + 1)
                    for j, weight in enumerate(weights):
                        adj_matrix[v_idx][j] = float(weight)

                except ValueError:
                    raise "error while processing file"

                continue

        return node_list, adj_matrix
