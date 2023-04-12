import math

from geopy.distance import distance

from src.model.node import Node


def euclidean_distance(first_node: Node, second_node: Node) -> float:
    """
    :param first_node: the first node
    :param second_node: the second node
    :return: the Euclidean distance between the two nodes
    """
    return math.sqrt(math.pow(first_node.y - second_node.y, 2) + math.pow(first_node.x - second_node.x, 2))


def geodesic_distance(first_coords: tuple[float, float], second_coords: tuple[float, float]) -> float:
    """
    :param first_coords: the coordinates of the first location on Earth's surface
    :param second_coords: the coordinates of the second location on Earth's surface
    :return: the geodesic distance between the two locations (in meters)
    """
    return distance(first_coords, second_coords).meters
