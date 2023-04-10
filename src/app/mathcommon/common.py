from model.node import Node

import math


def euclidean_distance(node_1: Node, node_2: Node) -> float:
    return math.sqrt(math.pow(node_1.y - node_2.y, 2) + math.pow(node_1.x - node_2.x, 2))