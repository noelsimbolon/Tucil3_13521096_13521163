import customtkinter
import tkintermapview
from tkintermapview.canvas_path import CanvasPath
from tkintermapview.canvas_position_marker import CanvasPositionMarker

from src.algorithm.main_algorithm import Engine
from src.common import distance_operations
from src.gui import util
from src.model.node import Node


class MapTab(customtkinter.CTkFrame):
    # Algorithm arguments
    starting_index: int = 0
    destination_index: int = 0
    nodes: list[Node] = []  # List of available Nodes
    adj_matrix: list[list[float]] = []  # Two-dimensional list to hold the adjacency matrix

    # Output
    route: list[Node] = []  # List of route Nodes
    distance: float = 0

    # Map attributes
    markers: list[CanvasPositionMarker] = []  # Markers represent nodes
    paths: list[CanvasPath] = []  # Paths represent edges

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        button_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='bold')
        entry_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.map_input_frame = MapInputFrame(master=self, width=180)
        self.map_input_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky='nswe')

        # Add path
        self.add_path_button = customtkinter.CTkButton(master=self.map_input_frame,
                                                       text='Add Path',
                                                       font=button_font,
                                                       command=self.add_path_event)
        self.add_path_button.grid(row=5, column=0, padx=20, pady=(10, 0))

        # Clear map
        self.clear_map_button = customtkinter.CTkButton(master=self.map_input_frame,
                                                        text='Clear Map',
                                                        font=button_font,
                                                        command=self.clear_map_event)
        self.clear_map_button.grid(row=6, column=0, padx=20, pady=(10, 0))

        # Start
        self.start_button = customtkinter.CTkButton(master=self.map_input_frame,
                                                    text='Start',
                                                    font=button_font,
                                                    command=self.find_shortest_route_and_visualize_route)
        self.start_button.grid(row=14, column=0, padx=20, pady=(10, 0))

        self.map_output_frame = MapOutputFrame(master=self)
        self.map_output_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky='nswe')

        # Search map entry
        self.search_map_entry = customtkinter.CTkEntry(master=self.map_output_frame,
                                                       width=400,
                                                       placeholder_text='Search map',
                                                       font=entry_font)
        self.search_map_entry.grid(row=0, column=0, padx=0, pady=10)
        self.search_map_entry.bind('<Return>', self.search_event)

        # Search map button
        self.search_map_button = customtkinter.CTkButton(master=self.map_output_frame,
                                                         text='Search',
                                                         font=button_font,
                                                         command=self.search_event)
        self.search_map_button.grid(row=0, column=1, padx=0, pady=10)

        # Map widget
        self.map = tkintermapview.TkinterMapView(master=self.map_output_frame,
                                                 corner_radius=10)
        self.map.grid(row=1, rowspan=2, column=0, columnspan=3, padx=(0, 0), pady=(0, 0), sticky='nswe')
        self.map.set_address('Lebak Siliwangi')
        self.map.add_right_click_menu_command(label="Add Marker",
                                              command=self.add_marker_event,
                                              pass_coords=True)

    def add_marker_event(self, coords) -> None:
        marker_id = len(MapTab.markers)
        marker_address = tkintermapview.convert_coordinates_to_address(coords[0], coords[1])
        new_marker = self.map.set_marker(coords[0],
                                         coords[1],
                                         text=f'{marker_id}. {marker_address.street}')

        MapTab.markers.append(new_marker)
        MapTab.nodes.append(Node(marker_id, coords[0], coords[1]))

    def add_path_event(self) -> None:
        # If there are less than two markers on the map
        if len(MapTab.markers) < 2:
            self.map_input_frame.map_message.configure(text='Not enough markers.',
                                                       text_color='red')
            return

        # If the first node or the second node is not valid,
        # display error message until it is valid
        if not (MapTab.is_index_valid(self.map_input_frame.first_node_entry.get()) and
                MapTab.is_index_valid(self.map_input_frame.second_node_entry.get())):

            # Clear status message
            self.map_input_frame.map_message.configure(text="")

            # If the first node is not valid
            if not MapTab.is_index_valid(self.map_input_frame.first_node_entry.get()):
                self.map_input_frame.map_message.configure(text="Invalid first node.",
                                                           text_color='red')
                return
            else:
                self.map_input_frame.map_message.configure(text="")

            # If the second node is not valid
            if not MapTab.is_index_valid(self.map_input_frame.second_node_entry.get()):
                self.map_input_frame.map_message.configure(text="Invalid second node.",
                                                           text_color='red')
                return
            else:
                self.map_input_frame.map_message.configure(text="")

        # If the first and second node is the same
        if int(self.map_input_frame.first_node_entry.get()) == int(self.map_input_frame.second_node_entry.get()):
            self.map_input_frame.map_message.configure(text='Cannot add path.',
                                                       text_color='red')
            return

        first_node_position: tuple[float, float] = 0.0, 0.0
        second_node_position: tuple[float, float] = 0.0, 0.0

        for node in MapTab.nodes:
            if node.node_id == int(self.map_input_frame.first_node_entry.get()):
                first_node_position = (node.x, node.y)
            if node.node_id == int(self.map_input_frame.second_node_entry.get()):
                second_node_position = (node.x, node.y)

        # If MapTab.paths is empty, add path without checking
        if len(MapTab.paths) == 0:
            new_path = self.map.set_path([first_node_position, second_node_position])
            MapTab.paths.append(new_path)
            self.map_input_frame.map_message.configure(text="Path added.",
                                                       text_color='green')
            return

        # Check if the path already exists
        should_add = True
        for path in MapTab.paths:
            if (path.position_list[0] == first_node_position and path.position_list[1] == second_node_position) or \
                    (path.position_list[0] == first_node_position and path.position_list[1] == first_node_position):
                should_add = False

        if should_add:
            new_path = self.map.set_path([first_node_position, second_node_position])
            MapTab.paths.append(new_path)
            self.map_input_frame.map_message.configure(text="Path added.",
                                                       text_color='green')
            return

        self.map_input_frame.map_message.configure(text="Path already exists.",
                                                   text_color='red')

    def clear_map_event(self) -> None:
        # Reset all class attribute
        MapTab.starting_index = 0
        MapTab.destination_index = 0
        MapTab.nodes = []
        MapTab.adj_matrix = []

        MapTab.route = []
        MapTab.distance = 0

        MapTab.markers = []
        MapTab.paths = []

        # Delete all markers and paths from the map
        self.map.delete_all_marker()
        self.map.delete_all_path()

        # Clear any output
        self.map_output_frame.result_tab_view.route_label.configure(text='')
        self.map_output_frame.result_tab_view.distance_label.configure(text='')
        self.map_input_frame.status_message.configure(text='')

        self.map_input_frame.map_message.configure(text='Map cleared.',
                                                   text_color='green')

    def search_event(self, event=None) -> None:
        self.map.set_address(self.search_map_entry.get())

    def find_shortest_route_and_visualize_route(self) -> None:
        # If there is less than 2 markers on the map
        if len(MapTab.markers) < 2:
            self.map_input_frame.status_message.configure(text="Not enough markers.",
                                                          text_color='red')
            return

        # If there is no path
        if len(MapTab.paths) == 0:
            self.map_input_frame.status_message.configure(text="Add a path first.",
                                                          text_color='red')
            return

        # If the starting node or the destination node is not valid,
        # display error message until it is valid
        if not (MapTab.is_index_valid(self.map_input_frame.starting_node_entry.get()) and
                MapTab.is_index_valid(self.map_input_frame.destination_node_entry.get())):

            # Clear status message
            self.map_input_frame.status_message.configure(text="")

            # If the starting node index is not valid
            if not MapTab.is_index_valid(self.map_input_frame.starting_node_entry.get()):
                self.map_input_frame.status_message.configure(text="Invalid starting node.",
                                                              text_color='red')
                return
            else:
                self.map_input_frame.status_message.configure(text="")

            # If the destination node index is not valid
            if not MapTab.is_index_valid(self.map_input_frame.destination_node_entry.get()):
                self.map_input_frame.status_message.configure(text="Invalid destination node.",
                                                              text_color='red')
                return
            else:
                self.map_input_frame.status_message.configure(text="")

        try:
            self.find_shortest_route()
        except TypeError:
            # There is no route from the starting node to the destination node
            self.map_input_frame.status_message.configure(text="No route found.",
                                                          text_color='red')
            return

        self.visualize_route()
        self.show_route_and_distance()

    def find_shortest_route(self) -> None:
        MapTab.starting_index = int(self.map_input_frame.starting_node_entry.get())
        MapTab.destination_index = int(self.map_input_frame.destination_node_entry.get())

        MapTab.fill_adj_matrix()

        # Start algorithm
        if self.map_input_frame.algorithm_options.get() == 'A*':
            # A-star path-finding
            MapTab.distance, MapTab.route = Engine.search_astar(MapTab.starting_index,
                                                                MapTab.destination_index,
                                                                MapTab.nodes,
                                                                MapTab.adj_matrix)
        else:
            # UCS path-finding
            MapTab.distance, MapTab.route = Engine.search_ucs(MapTab.starting_index,
                                                              MapTab.destination_index,
                                                              MapTab.nodes,
                                                              MapTab.adj_matrix)

    @staticmethod
    def fill_adj_matrix() -> None:
        # First, we clear the adjacency matrix
        MapTab.adj_matrix = []

        # Then, we create a list of tuples.
        # Each tuple represents the nodes that are adjacent
        # The integer values in the tuples are node IDs
        adjacent_nodes: list[tuple[Node, Node]] = []
        while len(adjacent_nodes) < len(MapTab.paths):

            for path in MapTab.paths:
                first_node = None
                second_node = None

                for node in MapTab.nodes:
                    if path.position_list[0] == (node.x, node.y):
                        first_node = node
                        break

                for node in MapTab.nodes:
                    if path.position_list[1] == (node.x, node.y):
                        second_node = node
                        break

                adjacent_nodes.append((first_node, second_node))

        # Fill adj_matrix with 0.0
        for i in range(len(MapTab.nodes)):
            MapTab.adj_matrix.append([0.0 for _ in range(len(MapTab.nodes))])

        # Fill adj_matrix with the geodesic distance as weights
        for adj_node in adjacent_nodes:
            MapTab.adj_matrix[adj_node[0].node_id][adj_node[1].node_id] = \
                distance_operations.geodesic_distance((adj_node[0].x, adj_node[0].y), (adj_node[1].x, adj_node[1].y))

            MapTab.adj_matrix[adj_node[1].node_id][adj_node[0].node_id] = \
                distance_operations.geodesic_distance((adj_node[0].x, adj_node[0].y), (adj_node[1].x, adj_node[1].y))

    def visualize_route(self) -> None:
        # Resets all the path color
        new_map_paths = []
        for path in MapTab.paths:
            new_map_paths.append(self.map.set_path(position_list=path.position_list))
        MapTab.paths = new_map_paths

        # Color the route paths
        i = 0
        while i < len(MapTab.route) - 1:
            for path in MapTab.paths:
                if i + 1 < len(MapTab.route):
                    if (path.position_list[0] == (MapTab.route[i].x, MapTab.route[i].y) and
                        path.position_list[1] == (MapTab.route[i + 1].x, MapTab.route[i + 1].y)) or \
                            (path.position_list[1] == (MapTab.route[i].x, MapTab.route[i].y) and
                             path.position_list[0] == (MapTab.route[i + 1].x, MapTab.route[i + 1].y)):
                        MapTab.paths.remove(path)
                        MapTab.paths.append(self.map.set_path(position_list=path.position_list,
                                                              color='yellow green'))
                        i += 1
                else:
                    break

        self.map_input_frame.status_message.configure(text='Route visualized.',
                                                      text_color='green')

    def show_route_and_distance(self) -> None:
        # Convert the route to string, example: 2-1-6-3-7
        route = ''
        for route_node in MapTab.route:
            route += f'{route_node.node_id}-'
        route = route[:-1]  # Remove trailing hyphen

        self.map_output_frame.result_tab_view.route_label.configure(text=route)
        self.map_output_frame.result_tab_view.distance_label.configure(text=f'{MapTab.distance:.5f} m')

    @staticmethod
    def is_index_valid(index: int) -> bool:
        """
        Validates the node index
        :param index: marker's index/label
        :return: True if the index is valid, False otherwise
        """
        try:
            if 0 <= int(index) <= len(MapTab.markers) - 1:
                return True
        except ValueError:
            return False

        return False


class MapInputFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Custom-defined fonts
        title_font = customtkinter.CTkFont(family='Segoe UI', size=-18, weight='bold')
        message_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        input_label_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='bold')
        entry_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        select_theme_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        select_algorithm_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')

        # Expandable empty space between the Start button and UI theme options
        self.grid_rowconfigure(16, weight=1)

        # App title
        self.app_title = customtkinter.CTkLabel(master=self,
                                                text='Compass',
                                                font=title_font)
        self.app_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # First node
        self.first_node = customtkinter.CTkLabel(master=self,
                                                 text='First node:',
                                                 font=input_label_font)
        self.first_node.grid(row=1, column=0, padx=20, pady=0)

        self.first_node_entry = customtkinter.CTkEntry(master=self,
                                                       placeholder_text="Marker number",
                                                       font=entry_font)
        self.first_node_entry.grid(row=2, column=0, padx=20, pady=0)

        # Second node
        self.second_node_label = customtkinter.CTkLabel(master=self,
                                                        text='Second node:',
                                                        font=input_label_font)
        self.second_node_label.grid(row=3, column=0, padx=20, pady=0)

        self.second_node_entry = customtkinter.CTkEntry(master=self,
                                                        placeholder_text="Marker number",
                                                        font=entry_font)
        self.second_node_entry.grid(row=4, column=0, padx=20, pady=(0, 5))

        # Add path button is defined in MapTab

        # Clear map button is defined in MapTab

        self.map_message = customtkinter.CTkLabel(master=self,
                                                  text='',
                                                  font=message_font)
        self.map_message.grid(row=7, column=0, padx=20, pady=(0, 0))

        # Starting node and destination node
        self.starting_node_label = customtkinter.CTkLabel(master=self,
                                                          text='Starting node:',
                                                          font=input_label_font)
        self.starting_node_label.grid(row=8, column=0, padx=20, pady=0)

        self.starting_node_entry = customtkinter.CTkEntry(master=self,
                                                          placeholder_text="Marker number",
                                                          font=entry_font)
        self.starting_node_entry.grid(row=9, column=0, padx=20, pady=0)

        self.destination_node_label = customtkinter.CTkLabel(master=self,
                                                             text='Destination node:',
                                                             font=input_label_font)
        self.destination_node_label.grid(row=10, column=0, padx=20, pady=0)

        self.destination_node_entry = customtkinter.CTkEntry(master=self,
                                                             placeholder_text="Marker number",
                                                             font=entry_font)
        self.destination_node_entry.grid(row=11, column=0, padx=20, pady=(0, 5))

        # Select algorithm
        self.select_algorithm_label = customtkinter.CTkLabel(master=self,
                                                             text="Select algorithm:",
                                                             font=input_label_font)
        self.select_algorithm_label.grid(row=12, column=0, padx=20, pady=(5, 0))

        self.algorithm_options = customtkinter.CTkOptionMenu(master=self,
                                                             values=['A*', 'UCS'],
                                                             font=select_algorithm_font)
        self.algorithm_options.grid(row=13, column=0, padx=20, pady=(0, 10))

        # Start button is defined in MapTab

        self.status_message = customtkinter.CTkLabel(master=self,
                                                     text='',
                                                     font=message_font)
        self.status_message.grid(row=15, column=0, padx=20, pady=0)

        # Select GUI theme
        self.select_theme_label = customtkinter.CTkLabel(master=self,
                                                         text="Select theme:",
                                                         font=select_theme_font)
        self.select_theme_label.grid(row=17, column=0, padx=20, pady=0)

        self.theme_options = customtkinter.CTkOptionMenu(master=self,
                                                         values=["Dark", "Light", "System"],
                                                         font=select_theme_font,
                                                         command=util.change_appearance_mode)
        self.theme_options.grid(row=18, column=0, padx=20, pady=(0, 20))


class MapOutputFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure the grid system
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(3, weight=0)

        # Search map entry is defined in MapTab

        # Search map button is defined in MapTab

        # Map widget is defined in MapTab

        # Result tab view
        self.result_tab_view = MapResultTabView(master=self,
                                                height=125)
        self.result_tab_view.grid(row=3, column=0, columnspan=3, padx=20, pady=20, sticky='we')
        self.result_tab_view._segmented_button.configure(font=('Segoe UI', -13, 'bold'))


class MapResultTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        output_font = customtkinter.CTkFont(family='Segoe UI', size=-14, weight='normal')

        # Create two tabs for output
        self.add('Route')
        self.add('Distance')

        self.tab('Route').grid_columnconfigure(0, weight=1)
        self.tab('Distance').grid_columnconfigure(0, weight=1)

        # Create a scrollable frame to hold the route
        self.route_scrollable_frame = customtkinter.CTkScrollableFrame(master=self.tab('Route'),
                                                                       height=30,
                                                                       orientation='horizontal')
        self.route_scrollable_frame.grid(row=0, column=0, columnspan=1, pady=10, sticky='ns')

        self.route_label = customtkinter.CTkLabel(master=self.route_scrollable_frame,
                                                  text='',
                                                  text_color='green',
                                                  font=output_font)
        self.route_label.grid(row=0, column=0, padx=10)

        # Create a label for distance
        self.distance_label = customtkinter.CTkLabel(master=self.tab('Distance'),
                                                     text='',
                                                     text_color='green',
                                                     font=output_font)
        self.distance_label.grid(row=0, column=0, pady=(20, 0))
