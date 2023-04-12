from __future__ import annotations


class Node:
    def __init__(self, node_id: int, x: float, y: float):
        # a node must be retrievable from node list by its node id
        self.node_id = node_id
        self.x = x
        self.y = y

    def __eq__(self, compare_object: Node) -> bool:
        return self.node_id == compare_object.node_id

    def __str__(self):
        return str(self.node_id)
