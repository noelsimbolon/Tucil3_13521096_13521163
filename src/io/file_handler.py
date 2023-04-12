from model.node import Node
from algorithm.main_algorithm import Engine


class FileInputHandler:

    @staticmethod
    def load_file(path: str) -> (list[Node], list[list[float]]):
        file1 = open(path, 'r')

        lines = file1.readlines()
        node_count = -1
        node_list: list[Node] = []
        adj_matrix: list[list[float]] = []
        line_idx = -1
        for i, line in enumerate(lines):
            try:
                if i == 0:  # matrix size / node count
                    node_count = int(line)
                    adj_matrix = [[] for _ in range(node_count)]
                    continue

                if 0 < i < node_count + 1:
                    node_id = i -1
                    coordinates = line.split(' ')
                    if len(coordinates) != 2:
                        RuntimeError("error while processing file")
                    node_list.append(Node(node_id, float(coordinates[0]), float(coordinates[1])))

                    continue

                if i >= node_count + 1:
                    weights = line.split(' ')
                    if len(weights) != node_count:
                        RuntimeError("error while processing file")

                    v_idx = i - (node_count + 1)
                    adj_matrix[v_idx] = ([0.0 for _ in range(node_count)])
                    for j, weight in enumerate(weights):
                        adj_matrix[v_idx][j] = float(weight)

            except (ValueError, IndexError):
                raise RuntimeError("error while processing file")

        return node_list, adj_matrix


if __name__ == '__main__':
    (node_list, adj_matrix) = FileInputHandler.load_file(
        "/home/zidane/kuliah/Semester-4/IF2211-Strategi-Algoritma/Tucil/Tucil3_13521096_13521163/src/app/matrix.txt")
    print(adj_matrix)
    (cost, listnode) = Engine.search_ucs(0, 5, node_list, adj_matrix)
    print(cost)

    for node in node_list:
        print(node.x, node.y)