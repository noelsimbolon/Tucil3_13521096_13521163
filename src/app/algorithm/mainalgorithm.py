import heapq

from mathcommon.common import *
from model.node import Node


class Engine:

    @staticmethod
    def __heuristic(informed: bool, start_node: Node = None, goal_node: Node = None) -> float:
        if not informed:
            return 0
        return euclidean_distance(start_node, goal_node)

    @staticmethod
    def __trace_path(dijkstra_table: list[(float, int)], node_list: list[Node],
                     goal_index: int) -> list[Node]:
        current_index = goal_index
        path: list[Node] = []
        cost: float = 0

        while current_index != -1:
            cost += dijkstra_table[current_index][0]
            path.append(node_list[current_index])
            current_index = dijkstra_table[current_index][1]

        print(cost)
        path.reverse()
        return path

    @staticmethod
    def search_path(start_index: int, goal_index: int, informed: bool,
                    node_list: list[Node], adj_matrix: list[list[float]]) -> list[Node]:
        # format: (shortest distance, source node id)
        dijkstra_table = [(float('inf'), 0) for _ in range(len(node_list))]
        # TODO: check this
        dijkstra_table[start_index] = (0, -1)

        queue = []
        # format: (shortest distance, node)
        heapq.heappush(queue, (Engine.__heuristic(informed, node_list[start_index], node_list[goal_index]), start_index))

        while len(queue) > 0:
            node_index: int = heapq.heappop(queue)[1]
            current_node: Node = node_list[node_index]

            if current_node == node_list[goal_index]:
                # found goal
                return Engine.__trace_path(dijkstra_table, node_list, goal_index)

            for i, weight in enumerate(adj_matrix[node_index]):
                if -0.0001 <= adj_matrix[node_index][i] <= 0.0001:
                    continue

                node = node_list[i]

                weight = dijkstra_table[current_node.node_id][0]
                weight += adj_matrix[node_index][i]
                weight += Engine.__heuristic(informed, node, node_list[goal_index])

                if dijkstra_table[node.node_id][0] > weight or dijkstra_table[node.node_id][0] == float('inf'):
                    dijkstra_table[node.node_id] = (weight, current_node.node_id)
                    heapq.heappush(queue, (weight, node.node_id))

            # for node in current_node.neighbors:
            #     weight = dijkstra_table[current_node.node_id][0]
            #     weight += euclidean_distance(current_node.point, node.point)
            #     weight += Engine.__heuristic(informed, node, node_list[goal_index])
            #
            #     if dijkstra_table[node.node_id][0] > weight or dijkstra_table[node.node_id][0] == float('inf'):
            #         dijkstra_table[node.node_id] = (weight, current_node.node_id)
            #         heapq.heappush(queue, (weight, node.node_id))

    @staticmethod
    def search_astar(start_index: int, goal_index: int, node_list: list[Node],
                     adj_matrix: list[list[float]]) -> list[Node]:
        return Engine.search_path(start_index, goal_index, True, node_list, adj_matrix)

    @staticmethod
    def search_ucs(start_index: int, goal_index: int, node_list: list[Node],
                   adj_matrix: list[list[float]]) -> list[Node]:
        return Engine.search_path(start_index, goal_index, False, node_list, adj_matrix)
